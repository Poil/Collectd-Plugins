#!/usr/bin/env python 
#--------------------------------------
# Auteur Original : Frederick Lemasson
# Date : 10/11/2016
# Version : 0.2
#--------------------------------------
# History :
#   0.1 - 16/11/2014 - FLM : initial version
#   0.2 - 10/11/2016 - BDU : add multi instance
#--------------------------------------
import os
import glob
import collectd

VERBOSE_LOGGING = False


def configure_callback(conf):
    """Received configuration information"""
    global VERBOSE_LOGGING
    if conf.key == 'Verbose':
        VERBOSE_LOGGING = bool(conf.values[0])
    else:
        collectd.warning('mailqueues plugin: Unknown config key: %s.' % conf.key)


def fetch_stats(): 
    postfix_instances = glob.glob('/var/spool/postfix*')
    for instance in postfix_instances:
        instance_name = os.path.basename(os.path.normpath(instance)).rsplit('-')[-1]
        if instance_name == 'postfix':
            instance_name = ''
        queueCount = {}
        for queue in ['maildrop','incoming','active','deferred','hold']:
            queueCount[queue] = 0
            for root, dirs, files in os.walk(os.path.join(instance,queue)):
                queueCount[queue] += len(files)

        for queue in queueCount:
            dispatch_stat(pinstance=instance_name, key=queue, value=queueCount[queue])


def dispatch_stat(pinstance, key, value, type='gauge'):
    """Read a key from info response data and dispatch a value"""
    value = int(value)
    log_verbose('Sending value[%s]: %s=%s' % (type, key, value))

    val = collectd.Values(plugin='mailqueues')
    val.plugin_instance = pinstance
    val.type = type
    val.type_instance = key
    val.values = [value]
    val.dispatch()


def read_callback():
    log_verbose('Read callback called')
    stats = fetch_stats()


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('PostfixQueuesMailsCount plugin [verbose]: %s' % msg)


collectd.register_config(configure_callback)
collectd.register_read(read_callback)

