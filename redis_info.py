# redis-collectd-plugin - redis_info.py
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; only version 2 of the License is applicable.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# Authors:
#   Garret Heaton <powdahound at gmail.com>
#
# About this plugin:
#   This plugin uses collectd's Python plugin to record Redis information.
#
# collectd:
#   http://collectd.org
# Redis:
#   http://redis.googlecode.com
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml

import collectd
import socket
import re

REDIS_INSTANCES = {}
REDIS_PI_DEFAULT = False
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_AUTH = None
VERBOSE_LOGGING = False


def fetch_info(host, port, auth=None):
    """Connect to Redis server and request info"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        log_verbose('redis_info plugin : Connected to Redis at %s:%s' % (host, port))
    except socket.error, e:
        collectd.error('redis_info plugin: Error connecting to %s:%d - %r' % (host, port, e))
        return None

    fp = s.makefile('r')

    if auth is not None:
        log_verbose('redis_info plugin : Sending auth command')
        s.sendall('auth %s\r\n' % (auth))

        status_line = fp.readline()
        if not status_line.startswith('+OK'):
            # -ERR invalid password
            # -ERR Client sent AUTH, but no password is set
            collectd.error('redis_info plugin: Error sending auth to %s:%d - %r' % (host, port, status_line))
            return None

    log_verbose('redis_info plugin : Sending info command')
    s.sendall('info\r\n')

    status_line = fp.readline()
    if not status_line.startswith('-ERR') and not status_line.startswith('-BUSY'):
        content_length = int(status_line[1:-1]) # status_line looks like: $<content_length>
        data = fp.read(content_length)
        log_verbose('redis_info plugin : Received data: %s' % data)
    else:
        data = ''

    # process 'info commandstats'
    log_verbose('Sending info commandstats command')
    s.sendall('info commandstats\r\n')
    fp.readline()  # skip first line in the response because it is empty
    status_line = fp.readline()
    log_verbose('Received line: %s' % status_line)
    if not status_line.startswith('-ERR') and not status_line.startswith('-BUSY'):
        content_length = int(status_line[1:-1])  # status_line looks like: $<content_length>
        datac = fp.read(content_length)  # fetch commandstats to different data buffer
        log_verbose('Received data: %s' % datac)
    else:
        datac = ''

    # process 'cluster info'
    log_verbose('Sending cluster info command')
    s.sendall('cluster info\r\n')
    fp.readline()  # skip first line in the response because it is empty
    status_line = fp.readline()
    log_verbose('Received line: %s' % status_line)
    if not status_line.startswith('-ERR') and not status_line.startswith('-BUSY'):
        content_length = int(status_line[1:-1])  # status_line looks like: $<content_length>
        datacluster = fp.read(content_length)  # fetch cluster info to different data buffer
        log_verbose('Received data: %s' % datacluster)
    else:
        datacluster = ''

    s.close()

    linesep = '\r\n' if '\r\n' in data else '\n'
    data_dict = parse_info(data.split(linesep))
    datac_dict = parse_info(datac.split(linesep))
    datacluster_dict = parse_info(datacluster.split(linesep))

    # let us see more raw data just in case
    log_verbose('Data: %s' % len(data_dict))
    log_verbose('Datac: %s' % len(datac_dict))
    log_verbose('Datacluster: %s' % len(datacluster_dict))

    # merge three data sets into one
    data_full = data_dict.copy()
    data_full.update(datac_dict)
    data_full.update(datacluster_dict)

    log_verbose('Data Full: %s' % len(data_full))

    # this generates hundreds of lines but helps in debugging a lot
    if VERBOSE_LOGGING:
        for key in data_full:
            log_verbose('Data Full detail: %s = %s' % (key, data_full[key]))

    return data_full


def parse_info(info_lines):
    """Parse info response from Redis"""
    info = {}
    for line in info_lines:
        if "" == line or line.startswith('#'):
            continue

        if ':' not in line:
            collectd.warning('redis_info plugin: Bad format for info line: %s' % line)
            continue

        key, val = line.split(':')

        # Handle multi-value keys (for dbs and slaves).
        # db lines look like "db0:keys=10,expire=0"
        # slave lines look like "slave0:ip=192.168.0.181,port=6379,state=online,offset=1650991674247,lag=1"
        if ',' in val:
            split_val = val.split(',')
            val = {}
            for sub_val in split_val:
                k, _, v = sub_val.rpartition('=')
                val[k] = v

        info[key] = val

    info["changes_since_last_save"] = info.get("changes_since_last_save", info.get("rdb_changes_since_last_save"))

    # For each slave add an additional entry that is the replication delay
    regex = re.compile("slave\d+")
    for key in info:
        if regex.match(key):
            info[key]['delay'] = int(info['master_repl_offset']) - int(info[key]['offset'])

    return info


def configure_callback(conf):
    """Receive configuration block"""
    global REDIS_INSTANCES, VERBOSE_LOGGING, REDIS_PI_DEFAULT

    for node in conf.children:
        if node.key == 'Verbose':
            VERBOSE_LOGGING = bool(node.values[0])

        elif node.key == 'Enable_PI_default':
            REDIS_PI_DEFAULT = bool(node.values[0])

        elif node.key == 'Instance':
            # if the instance is named, get the first given name
            if len(node.values):
                if len(node.values) > 1:
                    collectd.info("%s: Extra instance names (%s) converting instance name to (%s)" % (__name__, ", ".join(node.values[1:]), '_'.join(node.values) ))
                    redis_instance = '_'.join(node.values)
                else:
                    redis_instance = node.values[0]
            # else register an empty name instance
            else:
                redis_instance = 'default'
            for child in node.children:
                if child.key == 'Host':
                    host = child.values[0]
                elif child.key == 'Port':
                    port = int(child.values[0])
                elif child.key == 'Auth':
                    auth = child.values[0]
                else:
                    collectd.warning('redis_info plugin: Unknown config key: %s.' % child.key)

            if 'host' in locals() and 'port' in locals():
                if 'auth' not in locals():
                    auth = None
                REDIS_INSTANCES[redis_instance] = { 'host': host, 'port': port, 'auth': auth }
                log_verbose('redis_info plugin : Configured with host=%s, port=%s, using_auth=%s' % (host, port, auth))
            else:
                collectd.error("redis_info plugin : Ignoring instance name (%s)" % (redis_instance))
        else:
            collectd.error("redis_info plugin : Ignoring (%s)" % (str(node.key)))

    # Fallback to default if no config
    if not bool(REDIS_INSTANCES):
        REDIS_INSTANCES['default'] = { 'host': REDIS_HOST, 'port': REDIS_PORT, 'auth': REDIS_AUTH }


def read_callback():
    global REDIS_INSTANCES

    log_verbose('redis_info plugin : Read callback called')
    for redis_instance, redis_config in REDIS_INSTANCES.iteritems():
        info = fetch_info(redis_config['host'], redis_config['port'], redis_config['auth'])

        if not info:
            collectd.error('redis_info plugin: No info received')
            return

        # send high-level values
        dispatch_value(redis_instance, info, 'uptime_in_seconds','uptime')
        dispatch_value(redis_instance, info, 'connected_clients', 'gauge', 'clients-connected')
        dispatch_value(redis_instance, info, 'connected_slaves', 'gauge', 'slaves-connected')
        dispatch_value(redis_instance, info, 'blocked_clients', 'gauge', 'clients-blocked')
        dispatch_value(redis_instance, info, 'evicted_keys', 'gauge', 'keys-evicted')
        dispatch_value(redis_instance, info, 'expired_keys', 'gauge', 'keys-expired')
        dispatch_value(redis_instance, info, 'used_memory', 'bytes')
        dispatch_value(redis_instance, info, 'changes_since_last_save', 'gauge', 'changes-since_last_save')
        dispatch_value(redis_instance, info, 'total_connections_received', 'counter', 'connections-received')
        dispatch_value(redis_instance, info, 'total_commands_processed', 'counter', 'commands-processed')

        # send replication stats, but only if they exist (some belong to master only, some to slaves only)
        if 'master_repl_offset' in info: dispatch_value(redis_instance, info, 'master_repl_offset', 'gauge', 'repl_offset-master')
        if 'master_last_io_seconds_ago' in info: dispatch_value(redis_instance, info, 'master_last_io_seconds_ago', 'gauge', 'last_io_seconds_ago-master')
        if 'slave_repl_offset' in info: dispatch_value(redis_instance, info, 'slave_repl_offset', 'gauge', 'repl_offset-slave')

        # database and vm stats
        for key in info:
            if key.startswith('repl_'):
                dispatch_value(redis_instance, info, key, 'gauge', 'repl-%s' % key[5:])
            if key.startswith('vm_stats_'):
                dispatch_value(redis_instance, info, key, 'gauge', 'vm_stats-%s' % key[9:])
            if key.startswith('db'):
                dispatch_value(redis_instance, info[key], 'keys', 'gauge', 'db-%s-keys' % key)
                dispatch_value(redis_instance, info[key], 'expires', 'gauge', 'db-%s-expires-keys' % key)
            if key.startswith('slave'):
                dispatch_value(redis_instance, info[key], 'delay', 'delay', key)
            if key.startswith('cmdstat_'):
                dispatch_value(redis_instance, info[key], 'calls', 'counter', 'cmdstat-%s' % key[8:])
                dispatch_value(redis_instance, info[key], 'usec_per_call', 'delay', 'cmdstat-%s' % key[8:])
            if key.startswith('cluster_slots_'):
                dispatch_value(redis_instance, info, key, 'gauge', 'cluster_slots-%s' % key[14:])
            if key.startswith('cluster_stats_'):
                dispatch_value(redis_instance, info, key, 'gauge', 'cluster_stats-%s' % key[14:])


def dispatch_value(plugin_instance, info, key, type, type_instance=None):
    """Read a key from info response data and dispatch a value"""
    global REDIS_PI_DEFAULT

    if key not in info:
        log_verbose('redis_info plugin: Info key not found: %s' % key)
        return

    if not type_instance:
        type_instance = key

    try:
        value = int(info[key])
    except ValueError:
        value = float(info[key])
    except TypeError:
        log_verbose('No info for key: %s' % key)
        return

    log_verbose('redis_info plugin : Sending value: %s/%s=%s' % (plugin_instance, type_instance, value))

    val = collectd.Values(plugin='redis_info')
    if plugin_instance != "default" or REDIS_PI_DEFAULT:
        val.plugin_instance = plugin_instance
    val.type = type
    val.type_instance = type_instance
    val.values = [value]
    val.dispatch()


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('redis_info plugin [verbose]: %s' % msg)


# register callbacks
collectd.register_config(configure_callback)
collectd.register_read(read_callback)

