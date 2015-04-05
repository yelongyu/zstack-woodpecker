'''

@author: Frank
'''

import zstacklib.utils.http as http
import zstacklib.utils.log as log
import zstacklib.utils.plugin as plugin
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.daemon as daemon
import zstacklib.utils.iptables as iptables
import os.path
import functools
import traceback
import pprint

logger = log.get_logger(__name__)
TESTAGENT_PORT = 9393

class TestAgent(plugin.Plugin):
    pass

class TestAgentServer(object):
    http_server = http.HttpServer(port=TESTAGENT_PORT)
    http_server.logfile_path = log.get_logfile_path()
    
    def __init__(self):
        self.plugin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'plugins')
        self.plugin_rgty = plugin.PluginRegistry(self.plugin_path)
    
    def start(self, in_thread=True):
        self.plugin_rgty.configure_plugins({})
        self.plugin_rgty.start_plugins()
        if in_thread:
            self.http_server.start_in_thread()
        else:
            self.http_server.start()
    
    def stop(self):
        self.plugin_rgty.stop_plugins()
        self.http_server.stop()

class AgentResponse(object):
    def __init__(self, success=True, error=None):
        self.success = success
        self.error = error if error else ''

class AgentCommand(object):
    def __init__(self):
        pass
    
def replyerror(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            content = traceback.format_exc()
            err = '%s\n%s\nargs:%s' % (str(e), content, pprint.pformat([args, kwargs]))
            rsp = AgentResponse()
            rsp.success = False
            rsp.error = err
            logger.warn(err)
            raise http.HTTPError('500 Internal Server Error\n %s' % err, err)
    return wrap

class TestAgentDaemon(daemon.Daemon):
    def __init__(self, pidfile):
        super(TestAgentDaemon, self).__init__(pidfile)
    
    def run(self):
        self.agent = TestAgentServer()
        self.agent.start(False)
    
def build_http_path(ip, path):
    return 'http://%s:%s/%s' % (ip, str(TESTAGENT_PORT), path)
