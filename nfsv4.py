#!/usr/bin/env python 
#--------------------------------------
# Auteur : Benjamin DUPUIS
# Date : 28/05/2014
# Version : 0.1
# Dependance : pip install procfs
#--------------------------------------

from procfs import Proc
from pprint import pprint
import os.path
import collectd

VERBOSE_LOGGING = False


def configure_callback(conf):
    """Received configuration information"""
    global VERBOSE_LOGGING
    if conf.key == 'Verbose':
        VERBOSE_LOGGING = bool(conf.values[0])
    else:
        collectd.warning('nfsv4 plugin: Unknown config key: %s.' % conf.key)


def fetch_stats(): 
    proc = Proc()
    nfsd_keys = ['total', 'op0-unused', 'op1-unused', 'op2-future', 'access', 'close', 'commit', 'create', 'delegpurge', 'delegreturn', 'getattr', 'getfh', 'link', 'lock', 'lockt', 'locku', 'lookup', 'lookup_root', 'nverify', 'open', 'openattr', 'open_conf', 'open_dgrd', 'putfh', 'putpubfh', 'putrootfh', 'read', 'readdir', 'readlink', 'remove', 'rename', 'renew', 'restorefh', 'savefh', 'secinfo', 'setattr', 'setcltid', 'setcltidconf', 'verify', 'write', 'rellockowner', 'bc_ctl', 'bind_conn', 'exchange_id', 'create_ses', 'destroy_ses', 'free_stateid', 'getdirdeleg', 'getdevinfo', 'getdevlist', 'layoutcommit', 'layoutget', 'layoutreturn', 'secinfononam', 'sequence', 'set_ssv', 'test_stateid', 'want_deleg', 'destroy_clid', 'reclaim_comp']
    
    nfs_keys = ['total', 'read', 'write', 'commit', 'open', 'open_conf', 'open_noat', 'open_dgrd', 'close', 'setattr', 'renew', 'setclntid', 'confirm', 'lock', 'lockt', 'locku', 'access', 'getattr', 'lookup', 'lookup_root', 'remove', 'rename', 'link', 'symlink', 'create', 'pathconf', 'statfs', 'readlink', 'readdir', 'server_caps', 'delegreturn', 'getacl', 'setacl', 'fs_locations', 'rel_lkowner', 'secinfo', 'exchange_id', 'create_ses', 'destroy_ses', 'sequence', 'get_lease_t', 'reclaim_comp', 'layoutget', 'getdevinfo', 'layoutcommit', 'layoutreturn', 'getdevlist']

    if os.path.isfile('/proc/net/rpc/nfsd'):
        nfsd_values = proc.net.rpc.nfsd.proc4ops
        nfsd = dict(zip(nfsd_keys, nfsd_values))
        for key, value in nfsd.items():
            dispatch_stat('server', key, value)

    if os.path.isfile('/proc/net/rpc/nfs'):
        nfs_values = proc.net.rpc.nfs.proc4
        nfs = dict(zip(nfs_keys, nfs_values))
        for key, value in nfs.items():
            dispatch_stat('client', key, value)


def dispatch_stat(pinstance, key, value, type='derive'):
    """Read a key from info response data and dispatch a value"""
    value = int(value)
    log_verbose('Sending value[%s]: %s=%s' % (type, key, value))

    val = collectd.Values(plugin='nfs4')
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
    collectd.info('nfsv4 plugin [verbose]: %s' % msg)


collectd.register_config(configure_callback)
collectd.register_read(read_callback)

