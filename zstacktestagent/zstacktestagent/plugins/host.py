'''

@author: Frank
'''
import zstacktestagent.testagent  as testagent
import zstacklib.utils.shell      as shell
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.http       as http
import zstacklib.utils.linux      as linux
import zstacklib.utils.log        as log

logger = log.get_logger(__name__)

class CreateVlanDeviceCmd(testagent.AgentCommand):
    def __init__(self):
        super(CreateVlanDeviceCmd, self).__init__()
        self.ethname = None
        self.vlan = None
        self.ip = None
        self.netmask = None

class SetDeviceIpCmd(testagent.AgentCommand):
    def __init__(self):
        super(SetDeviceIpCmd, self).__init__()
        self.ethname = None
        self.ip = None
        self.netmask = None

class FlushDeviceIpCmd(testagent.AgentCommand):
    def __init__(self):
        super(FlushDeviceIpCmd, self).__init__()
        self.ethname = None

class DeleteVlanDeviceCmd(testagent.AgentCommand):
    def __init__(self):
        super(DeleteVlanDeviceCmd, self).__init__()
        self.vlan_ethname = None

class DeleteBridgeCmd(testagent.AgentCommand):
    def __init__(self):
        super(DeleteVlanDeviceCmd, self).__init__()
        self.bridge_name = None

class HostShellCmd(testagent.AgentCommand):
    def __init__(self):
        super(HostShellCmd, self).__init__()
        self.command = None

class HostShellRsp(testagent.AgentResponse):
    def __init__(self):
        super(HostShellRsp, self).__init__()
        self.return_code = None
        self.stdout = None
        self.stderr = None
        self.command = None
        
CREATE_VLAN_DEVICE_PATH = '/host/createvlandevice'
DELETE_VLAN_DEVICE_PATH = '/host/deletevlandevice'
DELETE_BRIDGE_PATH = '/host/deletebridgedevice'
SET_DEVICE_IP_PATH = '/host/setdeviceip'
FLUSH_DEVICE_IP_PATH = '/host/flushdeviceip'
HOST_SHELL_CMD_PATH = '/host/shellcmd'
ECHO_PATH = '/host/echo'

class HostAgent(testagent.TestAgent):
    def start(self):
        testagent.TestAgentServer.http_server.register_sync_uri(CREATE_VLAN_DEVICE_PATH, self.create_vlan_device)
        testagent.TestAgentServer.http_server.register_sync_uri(DELETE_VLAN_DEVICE_PATH, self.delete_vlan_device)
        testagent.TestAgentServer.http_server.register_sync_uri(DELETE_BRIDGE_PATH, self.delete_bridge)
        testagent.TestAgentServer.http_server.register_sync_uri(SET_DEVICE_IP_PATH, self.set_device_ip)
        testagent.TestAgentServer.http_server.register_sync_uri(FLUSH_DEVICE_IP_PATH, self.flush_device_ip)
        testagent.TestAgentServer.http_server.register_sync_uri(HOST_SHELL_CMD_PATH, self.host_shell_cmd)
        testagent.TestAgentServer.http_server.register_sync_uri(ECHO_PATH, self.echo)
    
    def stop(self):
        pass

    @testagent.replyerror
    def echo(self):
        logger.debug('echo ping')
        #rsp = testagent.AgentResponse()
        return 
    
    @testagent.replyerror
    def create_vlan_device(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        linux.create_vlan_eth(cmd.ethname, cmd.vlan, cmd.ip_, cmd.netmask_)
        rsp = testagent.AgentResponse()
        logger.debug('create vlan device: %s' % cmd.vlan)
        return jsonobject.dumps(rsp)
    
    @testagent.replyerror
    def set_device_ip(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        linux.set_device_ip(cmd.ethname, cmd.ip, cmd.netmask)
        rsp = testagent.AgentResponse()
        return jsonobject.dumps(rsp)

    @testagent.replyerror
    def flush_device_ip(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        linux.flush_device_ip(cmd.ethname)
        rsp = testagent.AgentResponse()
        return jsonobject.dumps(rsp)

    @testagent.replyerror
    def delete_vlan_device(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        linux.delete_vlan_eth(cmd.vlan_ethname)
        rsp = testagent.AgentResponse()
        logger.debug('delete vlan device: %s' % cmd.vlan)
        return jsonobject.dumps(rsp)
    
    @testagent.replyerror
    def delete_bridge(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        linux.delete_bridge(cmd.bridge_name)
        rsp = testagent.AgentResponse()
        return jsonobject.dumps(rsp)
    
    @testagent.replyerror
    def host_shell_cmd(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        scmd = shell.ShellCmd(cmd.command)
        scmd(False)
        rsp = HostShellRsp()
        rsp.return_code = scmd.return_code
        rsp.stderr = scmd.stderr
        rsp.stdout = scmd.stdout
        rsp.command = cmd.command
        logger.debug('execute %s, the stdout: %s, the stderr: %s' % (cmd.command, scmd.stdout, scmd.stderr))
        return jsonobject.dumps(rsp)
