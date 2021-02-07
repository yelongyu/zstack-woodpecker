import os
import sys
import traceback

import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import apibinding.inventory as inventory

class zstack_vcenter_volume_file_checker(checker_header.TestChecker):
    '''check vcenter volume file existencex . If it is in host, 
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_vcenter_volume_file_checker, self).check()
        volume = self.test_obj.volume
        volume_installPath = volume.installPath
        if not volume_installPath:
            test_util.test_logger('Check result: [installPath] is Null for [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
            return self.judge(False)

        ps_uuid = volume.primaryStorageUuid
        ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)
        if test_lib.lib_is_ps_iscsi_backend(ps_uuid):
            self.check_iscsi(volume, volume_installPath, ps)

        elif ps.type == inventory.VCENTER_PRIMARY_STORAGE_TYPE:
            cond = res_ops.gen_query_conditions('volume.uuid', '=', volume.uuid)
            vc_ps = res_ops.query_resource(res_ops.VCENTER_PRIMARY_STORAGE, cond)
            global vc_ps_volume_expunged
            if vc_ps:
                vc_ps = vc_ps[0]
                sign = 1
                vc_ps_volume_expunged = vc_ps
            else:
                sign = 0
                vc_ps = vc_ps_volume_expunged
            #connect vcenter, get datastore.host
            import ssl
            from pyVmomi import vim
            import atexit
            from pyVim import connect
            import zstackwoodpecker.zstack_test.vcenter_checker.zstack_vcenter_vm_checker as vm_checker

            vcenter_password = os.environ['vcenterpwd']
            vcenter_server = os.environ['vcenter']
            vcenter_username = os.environ['vcenteruser']

            sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            sslContext.verify_mode = ssl.CERT_NONE
            SI = connect.SmartConnect(host=vcenter_server, user=vcenter_username, pwd=vcenter_password, port=443, sslContext=sslContext)
            if not SI:
                test_util.test_fail("Unable to connect to the vCenter")
            content = SI.RetrieveContent()
            datastore = vm_checker.get_obj(content, [vim.Datastore], name=vc_ps.name)
            test_util.test_logger(datastore)
            host = str(datastore.host[0].key)
            host_morval = host.split(':')[1][:-1]
            test_util.test_logger(host_morval)
            atexit.register(connect.Disconnect, SI)

            cond = res_ops.gen_query_conditions('hypervisorType', '=', 'ESX')
            vc_hosts = res_ops.query_resource(res_ops.HOST, cond)
            for vc_host in vc_hosts:
                if vc_host.morval == host_morval:
                    vc_host = vc_host.managementIp
                    break
            if not vc_host:
                return self.judge(False)

            if volume_installPath.startswith('[' + vc_ps.name + ']'):
                test_util.test_logger(vc_ps.url)
                if sign:
                    vc_ps.url = vc_ps.url.split('//')[1]
                    test_util.test_logger(vc_ps.url)
                volume_installPath = volume_installPath.split('[' + vc_ps.name + ']')[1].lstrip()
                volume_installPath = vc_ps.url + volume_installPath

            file_exist = "file_exist"
            cmd = '[ -f %s ] && echo %s' % (volume_installPath, file_exist)
            vchost_user = os.environ['vchostUser']
            vchost_password = os.environ['vchostpwd']
            #test_lib.lib_execute_ssh_cmd(vc_host, vchost_user, vchost_password, cmd, 180)
            result = test_lib.lib_execute_ssh_cmd(vc_host, vchost_user, vchost_password, cmd, 180)
            test_util.test_logger(result)
            result = str(result)
            test_util.test_logger(result)
            if result.rstrip('\n') == "file_exist":
                test_util.test_logger(result.rstrip('\n'))
                return self.judge(True)
            else:
                return self.judge(False)

        

class zstack_vcenter_volume_attach_checker(checker_header.TestChecker):
    '''
        Check if volume is really attached to vm in vcenter.
    '''
    def check(self):
        super(zstack_vcenter_volume_attach_checker, self).check()
        volume = self.test_obj.volume
       
        if not self.test_obj.target_vm:
            test_util.test_logger('Check result: test [volume:] %s does NOT have vmInstance record in test structure. Can not do furture checking.' % volume.uuid)
            return self.judge(False)

        vm = self.test_obj.target_vm.vm

        if volume.format == "vmtx":
        #connect vcenter
            import ssl
            from pyVmomi import vim
            import atexit
            from pyVim import connect
            import zstackwoodpecker.zstack_test.vcenter_checker.zstack_vcenter_vm_checker as vm_checker
            vcenter_password = os.environ['vcenterpwd']
            vcenter_server = os.environ['vcenter']
            vcenter_username = os.environ['vcenteruser']
            sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            sslContext.verify_mode = ssl.CERT_NONE
            SI = connect.SmartConnect(host=vcenter_server, user=vcenter_username, pwd=vcenter_password, port=443, sslContext=sslContext)
            if not SI:
                test_util.test_fail("Unable to connect to the vCenter")
            content = SI.RetrieveContent()
            vc_vm = vm_checker.get_obj(content, [vim.VirtualMachine], name=vm.name)
            for i in vc_vm.config.hardware.device:
                if isinstance(i, vim.vm.device.VirtualDisk):
                    volumefile = i.backing.fileName
                    test_util.test_logger(volumefile)
                    test_util.test_logger(volume.installPath)
                    if volume.installPath == volumefile:
                        test_util.test_logger("find specified data volume attached to vm")
                        atexit.register(connect.Disconnect, SI)
                        return self.judge(True)
            
            test_util.test_logger("not find specified data volume attached to vm")
            atexit.register(connect.Disconnect, SI)
            return self.judge(False)
        

        