#!/usr/bin/env python 
#--------------------------------------
# Auteur : Frederick Lemasson
# Date : 16/11/2014
# Version : 0.1
#--------------------------------------

import os
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
	queueCount={}

	for queue in ['maildrop','incoming','active','deferred','hold']:
		queueCount[queue]=0
		for root, dirs, files in os.walk("/var/spool/postfix/"+queue):
		    queueCount[queue] += len(files)

	for queue in queueCount:
		#print("Mails in "+str(queue)+" : "+str(queueCount[queue]))
		dispatch_stat(key=queue, value=queueCount[queue])


def dispatch_stat(key, value, type='gauge'):
    """Read a key from info response data and dispatch a value"""
    value = int(value)
    log_verbose('Sending value[%s]: %s=%s' % (type, key, value))

    val = collectd.Values(plugin='mailqueues')
    #val.plugin_instance = pinstance
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



