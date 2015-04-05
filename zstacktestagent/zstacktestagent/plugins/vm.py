'''

@author: Frank
'''

import zstacktestagent.testagent as testagent
import zstacklib.utils.shell as shell
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.http as http
import zstacklib.utils.linux as linux
import zstacklib.utils.ssh as ssh
import zstacklib.utils.log as log
import threading
import time

logger = log.get_logger(__name__)

class VmStatusCmd(testagent.AgentCommand):
    def __init__(self):
        super(VmStatusCmd, self).__init__()
        self.vm_uuids = None

class VmStatusRsp(testagent.AgentResponse):
    def __init__(self):
        super(VmStatusRsp, self).__init__()
        self.vm_status = {}

class DeleteVmCmd(testagent.AgentCommand):
    def __init__(self):
        super(DeleteVmCmd, self).__init__()
        self.vm_uuids = None

class SshInVmCmd(testagent.AgentCommand):
    def __init__(self):
        super(SshInVmCmd, self).__init__()
        self.ip = None
        self.username = None
        self.password = None
        self.port = 22
        self.timeout = 180 # seconds
        self.command = None

class SshInVmRsp(testagent.AgentResponse):
    def __init__(self):
        super(SshInVmRsp, self).__init__()
        self.result = None

class ScpInVmCmd(testagent.AgentCommand):
    def __init__(self):
        super(ScpInVmCmd, self).__init__()
        self.ip = None
        self.username = None
        self.password = None
        self.port = 22
        self.timeout = 180 # seconds
        self.src_file = None
        self.dst_file = None

class ScpInVmRsp(testagent.AgentResponse):
    def __init__(self):
        super(ScpInVmRsp, self).__init__()
        self.result = None

         
IS_VM_STOPPED_PATH = '/vm/isvmstopped'
IS_VM_DESTROYED_PATH = '/vm/isvmdestroyed'
IS_VM_RUNNING_PATH = '/vm/isvmrunning'
DELETE_VM_PATH = '/vm/deletevm'
SSH_GUEST_VM_PATH = '/vm/sshguestvm'
SCP_GUEST_VM_PATH = '/vm/scpguestvm'
VM_STATUS = '/vm/vmstatus'
LIST_ALL_VM = '/vm/listallvm'
VM_BLK_STATUS = '/vm/vmblkstatus'
ECHO_PATH = '/host/echo'
        
class VmAgent(testagent.TestAgent):
    VM_STATUS_RUNNING = 'running'
    VM_STATUS_STOPPED = 'shut off'
    VM_STATUS_DESTROYED = None
    VM_EXCEPTION_STATUS = 'EXCEPTION_STATUS'
    
    def start(self):
        testagent.TestAgentServer.http_server.register_sync_uri(IS_VM_RUNNING_PATH, self.is_vm_running)
        testagent.TestAgentServer.http_server.register_sync_uri(IS_VM_DESTROYED_PATH, self.is_vm_stopped)
        testagent.TestAgentServer.http_server.register_sync_uri(IS_VM_STOPPED_PATH, self.is_vm_stopped)
        testagent.TestAgentServer.http_server.register_sync_uri(DELETE_VM_PATH, self.delete_vm)
        testagent.TestAgentServer.http_server.register_sync_uri(SSH_GUEST_VM_PATH, self.ssh_in_guest_vm)
        testagent.TestAgentServer.http_server.register_sync_uri(SCP_GUEST_VM_PATH, self.scp_in_guest_vm)
        testagent.TestAgentServer.http_server.register_sync_uri(VM_STATUS, self.get_vm_status)
        testagent.TestAgentServer.http_server.register_sync_uri(LIST_ALL_VM, self.list_all_vms)
        testagent.TestAgentServer.http_server.register_sync_uri(VM_BLK_STATUS, self.get_vm_blk_status)
        testagent.TestAgentServer.http_server.register_sync_uri(ECHO_PATH, self.echo)
        shell.logcmd = True

    @testagent.replyerror
    def echo(self, req):
        logger.debug('echo ping')
        return ''
    
    def stop(self):
        pass
    
    def _list_all_vms(self):
        output = shell.call('virsh list --all')
        return output.split('\n')
    
    def _is_vm_status(self, uuid, status):
        curr_status = self._get_vm_status(uuid)
        if status:
            if status in curr_status:
                return True
        else:
            if curr_status != self.VM_EXCEPTION_STATUS:
                return True
        logger.debug('[vm uuid: %s] does not have status: %s.' % (uuid, status))
        return False

    def _get_vm_status(self, uuid):
        try:
            output = shell.call('virsh domstate %s' % uuid)
        except Exception as e:
            logger.debug('Exception happened when trying to get [vm uuid: %s] status' % uuid)
            return self.VM_EXCEPTION_STATUS
            
        return output

    def _vm_blk_status(self, uuid):
        output = shell.call('virsh domblklist %s' % uuid).split('\n')
        output = output[2:]
        ret = {}
        for item in output:
            if item != '':
                blk = item.split()
                ret[blk[0]] = blk[1]
        return ret

    def _delete_vm(self, uuid):
        shell.call('virsh undefine --managed-save %s' % uuid)
    
    def _destroy_vm(self, uuid):
        shell.call('virsh destroy %s' % uuid)
    
    def _delete_all_vm(self):
        output = self._list_all_vms()
        output = filter(bool, output)
        for o in output:
            uuid = o.split()[1]
            if self.VM_STATUS_RUNNING in o:
                self._destroy_vm(uuid)
                self._delete_vm(uuid)
            else:
                self._delete_vm(uuid)
    
    @testagent.replyerror
    def is_vm_running(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = VmStatusRsp()
        for uuid in cmd.vm_uuids:
            rsp.vm_status[uuid] = self._is_vm_status(uuid, self.VM_STATUS_RUNNING)
        return jsonobject.dumps(rsp)
    
    @testagent.replyerror
    def is_vm_stopped(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = VmStatusRsp()
        for uuid in cmd.vm_uuids:
            rsp.vm_status[uuid] = self._is_vm_status(uuid, self.VM_STATUS_STOPPED)
        return jsonobject.dumps(rsp)
    
    @testagent.replyerror
    def is_vm_destroyed(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = VmStatusRsp()
        for uuid in cmd.vm_uuids:
            rsp.vm_status[uuid] = self._is_vm_status(uuid, self.VM_STATUS_DESTROYED)
        return jsonobject.dumps(rsp)
    
    @testagent.replyerror
    def get_vm_status(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = VmStatusRsp()
        for uuid in cmd.vm_uuids:
            rsp.vm_status[uuid] = self._get_vm_status(uuid)
            logger.debug('[vm:%s status:] %s.' % (uuid, rsp.vm_status[uuid]))
        return jsonobject.dumps(rsp)
    
    @testagent.replyerror
    def get_vm_blk_status(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = VmStatusRsp()

        for uuid in cmd.vm_uuids:
            rsp.vm_status[uuid] = self._vm_blk_status(uuid)
        return jsonobject.dumps(rsp)

    @testagent.replyerror
    def list_all_vms(self, req):
        rsp = VmStatusRsp()
        rsp.vm_status['vms'] = self._list_all_vms()
        return jsonobject.dumps(rsp)

    @testagent.replyerror
    def delete_vm(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        vmuuids = cmd.vm_uuids_
        if not vmuuids:
            self._delete_all_vm()
        else:
            for uuid in vmuuids:
                if self._is_vm_status(uuid, self.VM_STATUS_RUNNING):
                    self._destroy_vm(uuid)
                if (self._is_vm_status(uuid, self.VM_STATUS_STOPPED) or self._is_vm_status(uuid, self.VM_STATUS_DESTROYED)):
                    self._delete_vm(uuid)
        return jsonobject.dumps(testagent.AgentResponse())

    @testagent.replyerror
    def ssh_in_guest_vm(self, req):
        rsp = SshInVmRsp()
        rsp_dict = {'error': None, 'completion': None}
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        
        def login_vm():
            try:
                ret, output, stderr = ssh.execute(cmd.command, cmd.ip, cmd.username, cmd.password, False)
                if ret != 0:
                    rsp.success = False
                    rsp.error = '%s\n%s' % (output, stderr)
                else:
                    rsp.result = output

                rsp_dict['completion'] = True
                return True

            except Exception as e:
                logger.debug('[SSH] unable to ssh in vm[ip:%s], assume its not ready. Exception: %s' % (cmd.ip, str(e)))
                rsp_dict['error'] = True
                rsp_dict['completion'] = True
                
            return False

        thread = threading.Thread(target = login_vm)
        thread.start()
        timeout = time.time() + cmd.timeout 
        while not rsp_dict['completion'] and time.time() < timeout:
            time.sleep(0.5)

        if rsp_dict['completion']:
            if rsp_dict['error']:
                rsp.success = False
                rsp.error = 'ssh command:%s met exception.' % cmd.command
                logger.debug('ssh command:%s met exception.' % cmd.command)
        else:
            logger.debug('[SSH] ssh in vm[%s] doing %s, timeout after %s seconds' % (cmd.ip, cmd.command, cmd.timeout))
            rsp.success = False
            rsp.error = 'ssh execution keeps failure, until timeout: %s' \
                % cmd.timeout

        logger.debug('[SSH] ssh in vm[%s] doing %s done. result is %s' % (cmd.ip, cmd.command, rsp.success))
        return jsonobject.dumps(rsp)

    @testagent.replyerror
    def scp_in_guest_vm(self, req):
        cmd = jsonobject.loads(req[http.REQUEST_BODY])
        rsp = ScpInVmRsp()
        
        try:
            ssh.scp_file(cmd.src_file, cmd.dst_file, cmd.ip, cmd.username, cmd.password, cmd.port)
            rsp.success = True
            rsp.output = '[SCP] Successfully scp %s to [vm:] %s %s' % \
                    (cmd.src_file, cmd.ip, cmd.dst_file)

        except Exception as e:
            logger.debug('[SCP] scp %s to vm[ip:%s] failed: %s.' % \
                    (cmd.src_file, cmd.ip, str(e)))
            rsp.success = False
            rsp.error = str(e)

        return jsonobject.dumps(rsp)
