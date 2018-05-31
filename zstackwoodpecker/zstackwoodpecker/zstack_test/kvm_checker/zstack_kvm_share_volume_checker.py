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

try: 
  import xml.etree.cElementTree as ET 
except ImportError: 
  import xml.etree.ElementTree as ET

class zstack_kvm_share_volume_file_checker(checker_header.TestChecker):
    '''check kvm volume file existencex . If it is in host, 
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_share_volume_file_checker, self).check()
        volume = self.test_obj.volume
        volume_installPath = volume.installPath
        if not volume_installPath:
            test_util.test_logger('Check result: [installPath] is Null for [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
            return self.judge(False)

        ps_uuid = volume.primaryStorageUuid
        ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)
        #if test_lib.lib_is_ps_iscsi_backend(ps_uuid):
        #    self.check_iscsi(volume, volume_installPath, ps)
        #elif ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
        #    self.check_nfs(volume, volume_installPath)
        #elif ps.type == inventory.LOCAL_STORAGE_TYPE:
        #    host = test_lib.lib_get_local_storage_volume_host(volume.uuid)
        #    if not host:
        #        return self.judge(False)

        #    self.check_file_exist(volume, volume_installPath, host)
        if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
            self.check_ceph(volume, volume_installPath, ps)
        elif ps.type == 'SharedBlock':
            self.check_sharedblock(volume, volume_installPath, ps)
        else:
            test_util.test_logger('Check result: [share volume] primary storage is only support ceph, other storage type is not supported.')

    #def check_iscsi(self, volume, volume_installPath, ps):
    #    host = test_lib.lib_find_host_by_iscsi_ps(ps)
    #    if not host:
    #        test_util.test_logger('Check result: can not find Host, who owns iscsi filesystem backend. [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
    #        return self.judge(False)
    #    test_lib.lib_install_testagent_to_host(host)
    #    volume_file_path = volume_installPath.split(';')[1].split('file://')[1]
    #    self.check_file_exist(volume, volume_file_path, host)

    def check_ceph(self, volume, volume_installPath, ps):
        monHost = ps.mons[0].hostname
        for key in os.environ.keys():
            if monHost in os.environ.get(key):
                ceph_host, username, password = \
                        test_lib.lib_get_ceph_info(os.environ.get(key))
                break

        volume_installPath = volume_installPath.split('ceph://')[1]
        command = 'rbd info %s' % volume_installPath
        if test_lib.lib_execute_ssh_cmd(ceph_host, username, password, command, 10):
            test_util.test_logger('Check result: [volume:] %s [file:] %s exist on ceph [host name:] %s .' % (volume.uuid, volume_installPath, ceph_host))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [volume:] %s [file:] %s does NOT exist on ceph [host name:] %s .' % (volume.uuid, volume_installPath, ceph_host))
            return self.judge(False)

    def check_sharedblock(self, volume, volume_installPath, ps):
        devPath = "/dev/" + volume_installPath.split("sharedblock://")[1]
        cmd = 'lvs -o path %s' % devPath
        conditions = res_ops.gen_query_conditions('primaryStorage.uuid', '=', ps.uuid)
        cluster = res_ops.query_resource(res_ops.CLUSTER, conditions)[0]
        conditions = res_ops.gen_query_conditions('clusterUuid', '=', cluster.uuid)
        host = res_ops.query_resource(res_ops.HOST, conditions)[0]
        result = test_lib.lib_execute_ssh_cmd(host.managementIp, 'root', 'password', cmd)
        if devPath in result:
            return self.judge(True)
        else:
            return self.judge(False)

    #def check_nfs(self, volume, volume_installPath):
    #    host = test_lib.lib_get_volume_object_host(self.test_obj)
    #    if not host:
    #        test_util.test_logger('Check result: can not find Host, who is belonged to same Zone Uuid of [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
    #        return self.judge(False)

    #    self.check_file_exist(volume, volume_installPath, host)

    #def check_file_exist(self, volume, volume_installPath, host):
    #    cmd = host_plugin.HostShellCmd()
    #    file_exist = "file_exist"
    #    cmd.command = '[ -f %s ] && echo %s' % (volume_installPath, file_exist)
    #    rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, host_plugin.HOST_SHELL_CMD_PATH), cmd)
    #    rsp = jsonobject.loads(rspstr)
    #    output = jsonobject.dumps(rsp.stdout)
    #    if file_exist in output:
    #        test_util.test_logger('Check result: [volume:] %s [file:] %s exist on [host name:] %s .' % (volume.uuid, volume_installPath, host.managementIp))
    #        return self.judge(True)
    #    else:
    #        test_util.test_logger('Check result: [volume:] %s [file:] %s does not exist on [host name:] %s .' % (volume.uuid, volume_installPath, host.managementIp))
    #        return self.judge(False)

class zstack_kvm_share_volume_attach_checker(checker_header.TestChecker):
    '''
        Check if volume is really attached to vm in libvirt system.
    '''
    def check(self):
        super(zstack_kvm_share_volume_attach_checker, self).check()
        volume = self.test_obj.volume

        sv_cond = res_ops.gen_query_conditions("volumeUuid", '=', volume.uuid)
        share_volume_vm_uuids = res_ops.query_resource_fields(res_ops.SHARE_VOLUME, sv_cond, None, fields=['vmInstanceUuid'])
        #if not volume.vmInstanceUuid:
        if not share_volume_vm_uuids:
            test_util.test_logger('Check result: [volume:] %s does NOT have vmInstanceUuid. It is not attached to any vm.' % volume.uuid)
            return self.judge(False)

        if not self.test_obj.target_vm:
            test_util.test_logger('Check result: test [volume:] %s does NOT have vmInstance record in test structure. Can not do furture checking.' % volume.uuid)
            return self.judge(False)

        vm = self.test_obj.target_vm.vm

        volume_installPath = volume.installPath
        if not volume_installPath:
            test_util.test_logger('Check result: [installPath] is Null for [volume uuid: ] %s. Can not check if volume is attached to vm.' % volume.uuid)
            return self.judge(False)
        host = test_lib.lib_get_vm_host(vm)
        cmd = vm_plugin.VmStatusCmd()
        cmd.vm_uuids = [vm.uuid]
        rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.VM_BLK_STATUS), cmd)
        rsp = jsonobject.loads(rspstr)
        output = jsonobject.dumps(rsp.vm_status[vm.uuid])
        #if volume_installPath.startswith('iscsi'):
        #    volume_installPath = volume_installPath.split(';')[0].split('/iqn')[1]
        #    volume_installPath = 'iqn%s' % volume_installPath
        #    volume_installPath = volume_installPath[:-2]
        #elif volume_installPath.startswith('ceph'):
        if volume_installPath.startswith('ceph'):
            volume_installPath = volume_installPath.split('ceph://')[1]
        elif volume_installPath.startswith('sharedblock'):
            volume_installPath = "/dev/" + volume_installPath.split('sharedblock://')[1]


        if volume_installPath in output:
            test_util.test_logger('Check result: [volume:] %s [file:] %s is found in [vm:] %s on [host:] %s .' % (volume.uuid, volume_installPath, vm.uuid, host.managementIp))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [volume:] %s [file:] %s is not found in [vm:] %s on [host:] %s .' % (volume.uuid, volume_installPath, vm.uuid, host.managementIp))
            return self.judge(False)

class zstack_kvm_virtioscsi_shareable_checker(checker_header.TestChecker):
    '''
        Check if volume has shareable label attached to vm in libvirt system.
    '''
    def check(self):
        super(zstack_kvm_virtioscsi_shareable_checker, self).check()
        volume = self.test_obj.volume

        has_volume = False
        shareable = False
        check_result = False

        #sv_cond = res_ops.gen_query_conditions("volumeUuid", '=', volume.uuid)
        #share_volume_vm_uuids = res_ops.query_resource_fields(res_ops.SHARE_VOLUME, sv_cond, None, fields=['vmInstanceUuid'])
        #test_util.test_logger('share_volume_vm_uuids is %s' %share_volume_vm_uuids)
        print "volume_uuid= %s" %(volume.uuid)
        sv_cond = res_ops.gen_query_conditions("volumeUuid", '=', volume.uuid)
        volume_vmInstanceUuid = res_ops.query_resource_fields(res_ops.SHARE_VOLUME, sv_cond, None, fields=['vmInstanceUuid'])[0].vmInstanceUuid

        host = test_lib.lib_get_vm_host(test_lib.lib_get_vm_by_uuid(volume_vmInstanceUuid))
        test_util.test_logger('vmInstanceUuid_host.ip is %s' %host.managementIp)
        test_util.test_logger('vmInstanceUuid is %s' %volume_vmInstanceUuid)
        #xml = os.popen('virsh dumpxml %s' % volume.vmInstanceUuid)
        xml = os.popen('sshpass -p password ssh root@%s -p %s "virsh dumpxml %s"' %(host.managementIp, host.sshPort, volume_vmInstanceUuid))
        tree = ET.parse(xml)
        root = tree.getroot()
        for domain in root:
            if domain.tag == "devices":
                for device in domain:
                    if device.tag == "disk":
                       for disk in device:
                           if disk.tag == "source":
                               if disk.get("name").find(volume.uuid) > 0:
                                   has_volume = True
                           if disk.tag == "shareable":
                                   shareable = True
                           if has_volume and shareable:
                               check_result = True
                               break

        test_util.test_logger('Check result: The result of check VirtioSCSI shareable label is %s' %check_result)
        return self.judge(check_result)
