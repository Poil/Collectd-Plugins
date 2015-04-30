#!/usr/bin/env python
# Varnish libraries are created by parsing the libvarnishapi headers.
# This module works only with Varnish 3 as the api use now VSC_Open instead of VSL_Openstats.

import re
import sys
import varnish
import collectd
import subprocess




#####################################

# Class used to store values
class VarnishStat():
    def __init__(self, rrd_type, operation=False):
        self.rrd_type = rrd_type
        self.operation = operation
    def get_stat(self,current_stat_name ,all_stats):
        if self.operation:
            splitted_operation = re.findall("[\w.]+|[*/\-+()]", self.operation)
            correct_list = [str(float(all_stats['%s' % op].value)) if re.match("""[^\W\d_]""", op) else op for op in splitted_operation]
            try:
              result = eval(''.join(correct_list))
            except ZeroDivisionError:
              result = 0 
            return [result]
        else:
            return [all_stats[current_stat_name].value]
            
#########################             

# Defines default graphing parameters
collects = {
     'data_structures' : True,
     'session' : True,
     'request_rate' : True,
     'transfer_rates' : True,
     'backend_traffic' : True,
     'vcl_and_bans' : True,
     'losthdr' : True,
     'uptime' : True,
     'threads' : True,
     'memory_usage' : True,
     'expunge' : True,
     'session_herd' : True,
     'shm_writes' : True,
     'objoverflow' : True,
     'hcb' : True,
     'bad' : True,
     'objects' : True,
     'allocations' : True,
     'lru' : True,
     'objects_per_objhead' : True,
     'hit_rate' : True,
     'shm' : True,
     'esi' : True
 }


# multi instances?
instances = {
    '': dict(collects),
}

# Group graphs dict
common_graphs_dict = {
    'request_rate' : {
        'client_req' : VarnishStat('derive'),
        'cache_hit' : VarnishStat('derive', '(cache_hit/client_req)*100'),
        'cache_hitpass' : VarnishStat('derive', '(cache_hitpass/client_req)*100'),
        'cache_miss' : VarnishStat('derive', '(cache_miss/client_req)*100'),
        'backend_conn' : VarnishStat('derive'),
        'backend_unhealthy' : VarnishStat('derive'),
        's_pipe' : VarnishStat('derive'),
        's_pass' : VarnishStat('derive')
    },
    'hit_rate' : {
        'client_req' : VarnishStat('derive'),
        'cache_hit' : VarnishStat('derive'),
        'cache_miss' : VarnishStat('derive'),
        'cache_hitpass' : VarnishStat('derive')
    },
    'backend_traffic' : {
        'backend_conn' : VarnishStat('derive'),
        'backend_unhealthy' : VarnishStat('derive'),
        'backend_busy' : VarnishStat('derive'),
        'backend_fail' : VarnishStat('derive'),
        'backend_reuse' : VarnishStat('derive'),
        'backend_recycle' : VarnishStat('derive'),
        'backend_req' : VarnishStat('derive')
    },
    'objects' : {
        'n_object' : VarnishStat('gauge'),
        'n_objectcore' : VarnishStat('gauge'),
        'n_objecthead' : VarnishStat('gauge')
    },
    'memory_usage' : {
        'sms_balloc' : VarnishStat('gauge'),
        'sms_nbytes' : VarnishStat('gauge')
    },
    'uptime' : {
        'uptime' : VarnishStat('gauge', 'uptime / 86400')
    },
    'objects_per_objhead' : {
        'n_object' : VarnishStat('gauge'),
        'n_objecthead' : VarnishStat('gauge', 'n_object/n_objecthead')
    },
    'losthdr' : {
        'losthdr' : VarnishStat('derive')
    },
    'hcb' : {
        'hcb_nolock' : VarnishStat('derive'),
        'hcb_lock' : VarnishStat('derive'),
        'hcb_insert' : VarnishStat('derive')
    },
    'esi' : {
        'esi_errors' : VarnishStat('derive')
    },
    'objoverflow' : {
        'n_objoverflow' : VarnishStat('derive')
    },
    'session' : {
        'sess_closed' : VarnishStat('derive'),
        'sess_pipeline' : VarnishStat('derive'),
        'sess_readahead' : VarnishStat('derive'),
        'sess_linger' : VarnishStat('derive')
    },
    'session_herd' : {
        'sess_herd' : VarnishStat('derive')
    },
    'shm_writes' : {
        'shm_records' : VarnishStat('derive'),
        'shm_writes' : VarnishStat('derive')
    },
    'shm' : {
        'shm_flushes' : VarnishStat('derive'),
        'shm_cont' : VarnishStat('derive'),
        'shm_cycles' : VarnishStat('derive'),
    },
    'allocations' : {
        'sms_nreq' : VarnishStat('derive')
    },
    'vcl_and_bans' : {
        'n_backend' : VarnishStat('gauge'),
        'n_vcl' : VarnishStat('derive'),
        'n_vcl_avail' : VarnishStat('derive'), 
        'n_vcl_discard' : VarnishStat('derive'),
        'n_ban' : VarnishStat('gauge'),
        'n_ban_add' : VarnishStat('derive'),
        'n_ban_retire' : VarnishStat('derive'),
        'n_ban_obj_test' : VarnishStat('derive'),
        'n_ban_re_test' : VarnishStat('derive'),
        'n_ban_dups' : VarnishStat('derive')
    },
    'expunge' : {
        'n_expired' : VarnishStat('derive'),
        'n_lru_nuked' : VarnishStat('derive')
    },
    'lru' : {
        'n_lru_moved' : VarnishStat('derive')
    },
    'bad' : {
        'client_drop' : VarnishStat('derive'),
        'backend_unhealthy' : VarnishStat('derive'),
        'fetch_failed' : VarnishStat('derive'),
        'backend_busy' : VarnishStat('derive'),
        'n_wrk_failed' : VarnishStat('derive'),
        'n_wrk_max' : VarnishStat('derive'),
        'n_wrk_drop' : VarnishStat('derive'),
        'n_wrk_lqueue' : VarnishStat('gauge'),
        'losthdr' : VarnishStat('derive'),
        'n_objoverflow' : VarnishStat('derive'),
        'esi_errors' : VarnishStat('derive'),
        'esi_warnings' : VarnishStat('derive'),
        'client_drop_late' : VarnishStat('derive'),
        'accept_fail' : VarnishStat('derive')
    },
    'data_structures' : {
        'n_sess_mem' : VarnishStat('gauge'),
        'n_sess' : VarnishStat('gauge')        
    }
}

varnish3_graphs_dict = {
    'request_rate' : {
        'client_conn' : VarnishStat('derive')
    },
    'transfer_rates' : {
        's_hdrbytes' : VarnishStat('derive', 's_hdrbytes * 8'),
        's_bodybytes' : VarnishStat('derive', 's_bodybytes * 8')
    },
    'threads' : {
        'n_wrk' : VarnishStat('gauge'),
        'n_wrk_create' : VarnishStat('derive'),
        'n_wrk_failed' : VarnishStat('derive'),
        'n_wrk_max' : VarnishStat('derive'),
        'n_wrk_drop' : VarnishStat('derive')
    }
}    

# Should be used later
varnish4_graphs_dict = {
    'request_rate' : {
        'sess_conn' : VarnishStat('derive')
    },
    'objects' : {
        'n_objectcore' : VarnishStat('gauge')
    },
    'transfer_rates' : {
        's_resp_hdrbytes' : VarnishStat('derive'),
        's_resp_bodybytes' : VarnishStat('derive')
    },
    'threads' : {
        'threads' : VarnishStat('gauge'),
        'threads_created' : VarnishStat('derive'),
        'threads_failed' : VarnishStat('derive'),
        'threads_limited' : VarnishStat('derive'),
        'threads_destroyed' : VarnishStat('derive')
    },
    'bad' : {
        'threads_failed' : VarnishStat('derive'),
        'sess_drop' : VarnishStat('derive'),
        'sess_fail' : VarnishStat('derive'),
        'threads_limited' : VarnishStat('derive')
    },
    'data_structures' : {
        'n_srcaddr' : VarnishStat('gauge'),
        'n_srcaddr_act' : VarnishStat('gauge'),
        'n_smf' : VarnishStat('gauge'),
        'n_smf_frag' : VarnishStat('gauge'),
        'n_smf_large' : VarnishStat('gauge'),
        'n_vbe_conn' : VarnishStat('gauge'),
        'n_bereq' : VarnishStat('gauge'),
    }
}



# Class used to merge the group definition dictionnaries
class RUDict(dict):

    def __init__(self, *args, **kw):
        super(RUDict,self).__init__(*args, **kw)

    def update(self, E=None, **F):
        if E is not None:
            if 'keys' in dir(E) and callable(getattr(E, 'keys')):
                for k in E:
                    if k in self:
                        self.r_update(k, E)
                    else:
                        self[k] = E[k]
            else:
                for (k, v) in E:
                    self.r_update(k, {k:v})

        for k in F:
            self.r_update(k, {k:F[k]})

    def r_update(self, key, other_dict):
        if isinstance(self[key], dict) and isinstance(other_dict[key], dict):
            od = RUDict(self[key])
            nd = other_dict[key]
            od.update(nd)
            self[key] = od
        else:
            self[key] = other_dict[key]

# Parse collectd config file
def config(conf):
    global instances
    # get through the nodes under <Module "...">
    for node in conf.children:
        if node.key == "Instance":
            # if the instance is named, get the first given name
            if len(node.values):
                if len(node.values) > 1:
                    collectd.info("%s: Ignoring extra instance names (%s)" % (__name__, ", ".join(node.values[1:])) )
                instance = node.values[0]
            # else register an empty name instance
            else:
                instance = ''
    
            _collects = dict(collects)
            # get the stats to collect
            for child in node.children:
                # get the stat collection name
                if child.key.find("Collect") == 0:
                    collection = child.key[7:].lower()
                else:
                    collection = child.key.lower()

                # check if this collection is known
                if collection in collects:
                    _collects[collection] = True
                else:
                    collectd.warning("%s: Ignoring unknown configuration option (%s)" % (__name__, child.key))
    
            # add this instance to the dict of instances
            instances[instance] = _collects
            continue

        # unknown configuration node
        collectd.warning("%s: Ignoring unknown node type (%s)" % (__name__, node.key))

def get_varnish_version():
    """
    Launch varnishd -V and retrieve output.
    """
    varnish_output = subprocess.Popen(["varnishd", "-V"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    _, varnish_output = varnish_output.communicate()
    # Dirty regex cause i'm lazy
    varnish_version = re.match(""".*(\d+)\.\d+\.\d+.*""", varnish_output).groups()[0]
    if varnish_version == '4':
        sys.exit("Varnish 4 capabilities not yet implemented.")
    elif varnish_version == '3':
        # Merge common group dict with specific varnish3 stats
        current_varnish_group_dict.update(varnish3_graphs_dict)
    else:
        sys.exit("Wrong Varnish version. Should be v3-v4.")
    
def read_instance_stats(instance, instance_stats):
    """
    This function loops over the current varnish version graphs groups.
    """
    # Loop over configuration
    config_dict = instances[instance]
    for graph_group in config_dict.keys():
        for stat_name, v_obj in current_varnish_group_dict[graph_group].items():
            dispatch_metric(instance, graph_group, instance_stats, stat_name, v_obj)

#######################################
# Dispatch metric to rrd
def dispatch_metric(instance, instance_type, stats, value, varnish_object):
    metric = collectd.Values()
    metric.plugin = 'varnish3'
    metric.plugin_instance = instance and instance or 'default'
    metric.plugin_instance += "-%s" % instance_type
    metric.type = varnish_object.rrd_type
    metric.type_instance = value
    metric.values = varnish_object.get_stat(value, stats)
    metric.dispatch()

#################
# Loop overs instances
def read_instance(instance):
    with varnish.Instance() as v:
        instance_stats = v.stats.read()
    #dispatch(instance, instance_stats)
    read_instance_stats(instance, instance_stats)

# Read one instance
def read():
    for instance in instances:
        read_instance(instance)

######### INIT ############
# Instanciate the definitive graphs group dict
current_varnish_group_dict = RUDict(common_graphs_dict)
# Init varnish version
get_varnish_version()
# Retrieve config file
collectd.register_config(config)
# Read collected stats
collectd.register_read(read)
