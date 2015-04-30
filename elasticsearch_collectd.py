#! /usr/bin/python

import collectd
import json
import urllib2
import socket

global URL, STAT, PREFIX, ES_HOST, ES_PORT, ES_CLUSTER

PREFIX = "elasticsearch"
ES_CLUSTER = "elasticsearch"
ES_HOST = "localhost"
ES_PORT = 9200
VERBOSE_LOGGING = False
STAT=dict()

# INDICES METRICS #
## CACHE
STAT['indices_cache_evictions-filter'] = { "type": "counter", "path": "nodes.%s.indices.cache.filter_evictions" }
STAT['indices_cache_evictions-field'] = { "type": "counter", "path": "nodes.%s.indices.cache.field_evictions" }
STAT['indices_cache_size-filter'] = { "type": "bytes", "path": "nodes.%s.indices.cache.filter_size_in_bytes" }
STAT['indices_cache_size-field'] = { "type": "bytes", "path": "nodes.%s.indices.cache.field_size_in_bytes" }
STAT['indices_cache_count-filter'] = { "type": "counter", "path": "nodes.%s.indices.cache.filter_count" }

## DOCS
STAT['indices_docs-count'] = { "type": "gauge", "path": "nodes.%s.indices.docs.count" }
STAT['indices_docs-deleted'] = { "type": "counter", "path": "nodes.%s.indices.docs.deleted" }

## FLUSH
STAT['indices_total-flush'] = { "type": "counter", "path": "nodes.%s.indices.flush.total" }
STAT['indices_time-flush'] = { "type": "counter", "path": "nodes.%s.indices.flush.total_time_in_millis" }

## GET
STAT['indices_get_time-current'] = { "type": "counter", "path": "nodes.%s.indices.get.time_in_millis" }
STAT['indices_get_time-exists'] = { "type": "counter", "path": "nodes.%s.indices.get.exists_time_in_millis" }
STAT['indices_get_time-missing'] = { "type": "counter", "path": "nodes.%s.indices.get.missing_time_in_millis" }
STAT['indices_get_total-current'] = { "type": "counter", "path": "nodes.%s.indices.get.total" }
STAT['indices_get_total-exists'] = { "type": "counter", "path": "nodes.%s.indices.get.exists_total" }
STAT['indices_get_total-missing'] = { "type": "counter", "path": "nodes.%s.indices.get.missing_total" }

## INDEXING
STAT['indices_indexing_time-delete'] = { "type": "counter", "path": "nodes.%s.indices.indexing.delete_time_in_millis" }
STAT['indices_indexing_time-index'] = { "type": "counter", "path": "nodes.%s.indices.indexing.index_time_in_millis" }
STAT['indices_indexing_total-delete'] = { "type": "counter", "path": "nodes.%s.indices.indexing.delete_total" }
STAT['indices_indexing_total-index'] = { "type": "counter", "path": "nodes.%s.indices.indexing.index_total" }

## MERGES
STAT['indices_merges-current'] = { "type": "gauge", "path": "nodes.%s.indices.merges.current" }
STAT['indices_merges-total'] = { "type": "counter", "path": "nodes.%s.indices.merges.total" }
STAT['indices_merges_docs-current'] = { "type": "gauge", "path": "nodes.%s.indices.merges.current_docs" }
STAT['indices_merges_docs-total'] = { "type": "gauge", "path": "nodes.%s.indices.merges.total_docs" }
STAT['indices_merges_size-current'] = { "type": "bytes", "path": "nodes.%s.indices.merges.current_size_in_bytes" }
STAT['indices_merges_size-total'] = { "type": "bytes", "path": "nodes.%s.indices.merges.total_size_in_bytes" }
STAT['indices_merges_time-total'] = { "type": "counter", "path": "nodes.%s.indices.merges.total_time_in_millis" }

## REFRESH
STAT['indices_total-refresh'] = { "type": "counter", "path": "nodes.%s.indices.refresh.total" }
STAT['indices_time-refresh'] = { "type": "counter", "path": "nodes.%s.indices.refresh.total_time_in_millis" }

## SEARCH
STAT['indices_search_total-query'] = { "type": "counter", "path": "nodes.%s.indices.search.query_total" }
STAT['indices_search_current-query'] = { "type": "gauge", "path": "nodes.%s.indices.search.query_current" }
STAT['indices_search_fetch-current'] = { "type": "counter", "path": "nodes.%s.indices.search.fetch_current" }
STAT['indices_search_fetch-total'] = { "type": "counter", "path": "nodes.%s.indices.search.fetch_total" }
STAT['indices_search_time-fetch'] = { "type": "counter", "path": "nodes.%s.indices.search.fetch_time_in_millis" }
STAT['indices_search_time-query'] = { "type": "counter", "path": "nodes.%s.indices.search.query_time_in_millis" }

## STORE
STAT['indices_size-store'] = { "type": "bytes", "path": "nodes.%s.indices.store.size_in_bytes" }

# JVM METRICS #
## MEM
STAT['jvm_mem-heap_committed'] = { "type": "bytes", "path": "nodes.%s.jvm.mem.heap_committed_in_bytes" }
STAT['jvm_mem-heap_used'] = { "type": "bytes", "path": "nodes.%s.jvm.mem.heap_used_in_bytes" }
STAT['jvm_mem-non_heap_committed'] = { "type": "bytes", "path": "nodes.%s.jvm.mem.non_heap_committed_in_bytes" }
STAT['jvm_mem-non_heap_used'] = { "type": "bytes", "path": "nodes.%s.jvm.mem.non_heap_used_in_bytes" }

## THREADS
STAT['jvm_threads-count'] = { "type": "gauge", "path": "nodes.%s.jvm.threads.count" }
STAT['jvm_threads-peak'] = { "type": "gauge", "path": "nodes.%s.jvm.threads.peak_count" }

## GC
STAT['jvm_gc-time'] = { "type": "counter", "path": "nodes.%s.jvm.gc.collection_time_in_millis" }
STAT['jvm_gc-count'] = { "type": "counter", "path": "nodes.%s.jvm.gc.collection_count" }

# TRANSPORT METRICS #
STAT['transport_open-server'] = { "type": "gauge", "path": "nodes.%s.transport.server_open" }
STAT['transport_count-rx'] = { "type": "counter", "path": "nodes.%s.transport.rx_count" }
STAT['transport_count-tx'] = { "type": "counter", "path": "nodes.%s.transport.tx_count" }
STAT['transport_size-rx'] = { "type": "bytes", "path": "nodes.%s.transport.rx_size_in_bytes" }
STAT['transport_size-tx'] = { "type": "bytes", "path": "nodes.%s.transport.tx_size_in_bytes" }

# HTTP METRICS #
STAT['http_open-current'] = { "type": "gauge", "path": "nodes.%s.http.current_open" }
STAT['http_open-total'] = { "type": "gauge", "path": "nodes.%s.http.total_opened" }

# PROCESS METRICS #
STAT['process-open_file_descriptors'] = { "type": "gauge", "path": "nodes.%s.process.open_file_descriptors" }

# FUNCTION: Collect stats from JSON result
def lookup_stat(stat, json):

    node = json['nodes'].keys()[0]
    val = dig_it_up(json, STAT[stat]["path"] % node )

    # Check to make sure we have a valid result
    # dig_it_up returns False if no match found
    if not isinstance(val,bool):
        return int(val)
    else:
        return None

def configure_callback(conf):
    """Received configuration information"""
    global ES_HOST, ES_PORT, ES_URL, VERBOSE_LOGGING
    for node in conf.children:
        if node.key == 'Host':
            ES_HOST = node.values[0]
        elif node.key == 'Port':
            ES_PORT = int(node.values[0])
        elif node.key == 'Verbose':
            VERBOSE_LOGGING = bool(node.values[0])
        elif node.key == 'Cluster':
            ES_CLUSTER = node.values[0]
        else:
            collectd.warning('elasticsearch plugin: Unknown config key: %s.'
                             % node.key)
    ES_URL = "http://" + ES_HOST + ":" + str(ES_PORT) + "/_nodes/_local/stats?http=true&process=true&jvm=true&transport=true"

    log_verbose('Configured with host=%s, port=%s, url=%s' % (ES_HOST, ES_PORT, ES_URL))

def fetch_stats(): 
    global ES_URL, ES_CLUSTER

    try:
        result = json.load(urllib2.urlopen(ES_URL, timeout = 10))
    except urllib2.URLError, e:
        collectd.error('elasticsearch plugin: Error connecting to %s - %r' % (ES_URL, e))
        return None
    print result['cluster_name']
  
    ES_CLUSTER = result['cluster_name']
    return parse_stats(result)

def parse_stats(json):
    """Parse stats response from ElasticSearch"""
    for name,key in STAT.iteritems():
        result = lookup_stat(name, json)
        dispatch_stat(result, name, key)

def dispatch_stat(result, name, key):
    """Read a key from info response data and dispatch a value"""
    if not key.has_key("path"):
        collectd.warning('elasticsearch plugin: Stat not found: %s' % key)
        return
    type = key["type"]
    log_verbose('Parse %s : %s' % (name, result))
    if result != None:
        value = int(result)
        log_verbose('Sending value[%s]: %s=%s' % (type, name, value))

        val = collectd.Values(plugin='elasticsearch')
        val.plugin_instance = ES_CLUSTER
        val.type = type
        val.type_instance = name
        val.values = [value]
        val.dispatch()

def read_callback():
    log_verbose('Read callback called')
    stats = fetch_stats()

def dig_it_up(obj,path):
    try:
        if type(path) in (str,unicode):
            path = path.split('.')
        return reduce(lambda x,y:x[y],path,obj)
    except:
        return False

def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('elasticsearch plugin [verbose]: %s' % msg)

collectd.register_config(configure_callback)
collectd.register_read(read_callback)
