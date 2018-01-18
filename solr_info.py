import collectd
import urllib2
import json
import itertools


SOLR_HOST = "localhost"
SOLR_PORT = "8080"
VERBOSE_LOGGING = False
SOLR_HANDLERS = {"query": "/select", "suggest": "/suggest", "simillar": "/mlt"}

SOLR_INSTANCES = {
}

def configure_callback(conf):
    """Received configuration information"""
    global SOLR_HOST, SOLR_PORT, SOLR_INSTANCES, VERBOSE_LOGGING
    for node in conf.children:
        if node.key == "Instance":
            # if the instance is named, get the first given name
            if len(node.values):
                if len(node.values) > 1:
                    collectd.info("%s: Ignoring extra instance names (%s)" % (__name__, ", ".join(node.values[1:])))
                solr_instance = node.values[0]
            # else register an empty name instance
            else:
                solr_instance = 'default'

        for child in node.children:
            if child.key == 'Host':
                SOLR_HOST = child.values[0]
            elif child.key == 'Port':
                SOLR_PORT = int(child.values[0])
            elif child.key == 'Verbose':
                VERBOSE_LOGGING = bool(child.values[0])
            else:
                collectd.warning('solr_info plugin: Unknown config key: %s.' % node.key)

        # add this instance to the dict of instances
        SOLR_INSTANCES[solr_instance] = "http://" + SOLR_HOST + ":" + str(SOLR_PORT) + "/solr/" + solr_instance
        continue

    log_verbose('Configured with host=%s, port=%s, instance=%s' % (SOLR_HOST, SOLR_PORT, solr_instance))


def dispatch_value(plugin_category, value, value_name, value_type, type_instance=None):
    val = collectd.Values(plugin="solr_info")
    val.type = value_type

    val.plugin_instance = plugin_category.replace('-', '_')+"-"+value_name

    if type_instance is not None:
        val.type_instance = type_instance
    else:
        val.type_instance = value_name
    val.values = [value]
    val.dispatch()


def fetch_data():
    global SOLR_INSTANCES, SOLR_HANDLERS
    data = {}

    for solr_instance, url in SOLR_INSTANCES.iteritems():
        stats_url = "%s/admin/mbeans?stats=true&wt=json" % (url)

        stats = urllib2.urlopen(stats_url)
        solr_data = json.load(stats)

        # Searcher information
        solr_data = solr_data["solr-mbeans"]

        # Data is return in form of [ "TYPE", { DATA }, "TYPE", ... ] so pair them up
        solr_data_iter = iter(solr_data)
        solr_data = itertools.izip(solr_data_iter, solr_data_iter)

        data[solr_instance] = {"cache": {}, "handler_stats": {}, "update_stats": {}}
        for module, module_data in solr_data:
            if module == "CORE":
                data[solr_instance]["docs"] = module_data["searcher"]["stats"]["numDocs"]
            elif module == "CACHE":
                data[solr_instance]["cache"]["size"] = module_data["fieldValueCache"]["stats"]["size"]
                data[solr_instance]["cache"]["hitratio"] = module_data["fieldValueCache"]["stats"]["hitratio"]
                data[solr_instance]["cache"]["evictions"] = module_data["fieldValueCache"]["stats"]["evictions"]
            elif module == "QUERYHANDLER":
                #interesting_handlers = { endpoint: name for name, endpoint in SOLR_HANDLERS.iteritems() }
                # Fix python 2.6
                interesting_handlers = dict((endpoint, name) for (endpoint, name) in SOLR_HANDLERS.iteritems())
                for handler, handler_data in module_data.iteritems():
                    if handler not in interesting_handlers:
                        continue

                    handler_name = interesting_handlers[handler]
                    data[solr_instance]["handler_stats"][handler_name] = {}
                    data[solr_instance]["handler_stats"][handler_name]["requests"] = handler_data["stats"]["requests"]
                    data[solr_instance]["handler_stats"][handler_name]["errors"] = handler_data["stats"]["errors"]
                    data[solr_instance]["handler_stats"][handler_name]["timeouts"] = handler_data["stats"]["timeouts"]
                    data[solr_instance]["handler_stats"][handler_name]["time_per_request"] = handler_data["stats"]["avgTimePerRequest"]
                    data[solr_instance]["handler_stats"][handler_name]["requests_per_second"] = handler_data["stats"]["avgRequestsPerSecond"]
            elif module == "UPDATEHANDLER":
                data[solr_instance]["update_stats"]["commits"] = module_data["updateHandler"]["stats"]["commits"]
                data[solr_instance]["update_stats"]["autocommits"] = module_data["updateHandler"]["stats"]["autocommits"]
                if module_data["updateHandler"]["stats"].has_key('soft autocommits'):
                    data[solr_instance]["update_stats"]["soft_autocommits"] = module_data["updateHandler"]["stats"]["soft autocommits"]
                data[solr_instance]["update_stats"]["optimizes"] = module_data["updateHandler"]["stats"]["optimizes"]
                data[solr_instance]["update_stats"]["rollbacks"] = module_data["updateHandler"]["stats"]["rollbacks"]
                data[solr_instance]["update_stats"]["expunges"] = module_data["updateHandler"]["stats"]["expungeDeletes"]
                data[solr_instance]["update_stats"]["pending_docs"] = module_data["updateHandler"]["stats"]["docsPending"]
                data[solr_instance]["update_stats"]["adds"] = module_data["updateHandler"]["stats"]["adds"]
                data[solr_instance]["update_stats"]["deletes_by_id"] = module_data["updateHandler"]["stats"]["deletesById"]
                data[solr_instance]["update_stats"]["deletes_by_query"] = module_data["updateHandler"]["stats"]["deletesByQuery"]
                data[solr_instance]["update_stats"]["errors"] = module_data["updateHandler"]["stats"]["errors"]
    return data


def read_callback():
    data = fetch_data()
    for solr_instance in SOLR_INSTANCES:
        dispatch_value(solr_instance, data[solr_instance]["docs"], "index", "gauge", "documents")
        dispatch_value(solr_instance, data[solr_instance]["cache"]["size"], "cache", "gauge", "size")
        dispatch_value(solr_instance, data[solr_instance]["cache"]["hitratio"], "cache_hitratio", "gauge", "hitratio")
        dispatch_value(solr_instance, data[solr_instance]["cache"]["evictions"], "cache", "gauge", "evictions")

        for handler_name, handler_data in data[solr_instance]["handler_stats"].iteritems():
            dispatch_value(solr_instance, handler_data["requests"], handler_name, "gauge", "requests")
            dispatch_value(solr_instance, handler_data["errors"], handler_name, "gauge", "errors")
            dispatch_value(solr_instance, handler_data["timeouts"], handler_name, "gauge", "timeouts")
            dispatch_value(solr_instance, handler_data["time_per_request"], "request_times", "gauge", handler_name)
            dispatch_value(solr_instance, handler_data["requests_per_second"], "requests_per_second", "gauge", handler_name)

        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["commits"], "update", "gauge", "commits")
        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["autocommits"], "update", "gauge", "autocommits")
        if data[solr_instance]["update_stats"].has_key("soft_autocommits"):
            dispatch_value(solr_instance, data[solr_instance]["update_stats"]["soft_autocommits"], "update", "gauge", "soft_autocommits")
        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["optimizes"], "update", "gauge", "optimizes")
        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["expunges"], "update", "gauge", "expunges")
        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["rollbacks"], "update", "gauge", "rollbacks")
        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["pending_docs"], "update", "gauge", "pending_docs")
        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["adds"], "update", "gauge", "adds")
        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["deletes_by_id"], "update", "gauge", "deletes_by_id")
        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["deletes_by_query"], "update", "gauge", "deletes_by_query")
        dispatch_value(solr_instance, data[solr_instance]["update_stats"]["errors"], "update", "gauge", "errors")


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('solr_info plugin [verbose]: %s' % msg)


collectd.register_config(configure_callback)
collectd.register_read(read_callback)

