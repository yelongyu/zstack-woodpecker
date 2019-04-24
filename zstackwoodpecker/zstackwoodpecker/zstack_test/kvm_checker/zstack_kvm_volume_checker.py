import os
import sys
import traceback
import urllib2

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

class zstack_kvm_volume_file_checker(checker_header.TestChecker):
    '''check kvm volume file existencex . If it is in host, 
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_volume_file_checker, self).check()
        volume = self.test_obj.volume
        volume_installPath = volume.installPath
        if not volume_installPath:
            test_util.test_logger('Check result: [installPath] is Null for [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
            return self.judge(False)

        ps_uuid = volume.primaryStorageUuid
        ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)
        if test_lib.lib_is_ps_iscsi_backend(ps_uuid):
            self.check_iscsi(volume, volume_installPath, ps)
        elif ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
            self.check_nfs(volume, volume_installPath)
        elif ps.type == inventory.LOCAL_STORAGE_TYPE:
            host = test_lib.lib_get_local_storage_volume_host(volume.uuid)
            if not host:
                return self.judge(False)

            self.check_file_exist(volume, volume_installPath, host)
        elif ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
            self.check_ceph(volume, volume_installPath, ps)
        elif ps.type == 'SharedBlock':
            self.check_sharedblock(volume, volume_installPath, ps)
        elif ps.type == 'AliyunEBS':
            self.check_ebs(ps, volume_installPath)
        elif ps.type == 'MiniStorage':
            self.check_mini(volume, volume_installPath, ps)

    def check_ebs(self, ps, volume_installPath):
        import zstackwoodpecker.operations.scenario_operations as sce_ops
        url = ps.url.replace('ocean/api', 'auto/test')
        req = urllib2.Request(url)
        ebs_domain = urllib2.urlopen(req).read().split('"')[-2]
        vol_name = volume_installPath.split(';')[1].replace('volumeId=', 'ebs-test-disk-')
        cond = res_ops.gen_query_conditions('name', 'like', vol_name + '%')
        ret = sce_ops.query_resource(ebs_domain, res_ops.VOLUME, cond).inventories
        if ret:
            return self.judge(True)
        else:
            return self.judge(False)

    def check_sharedblock(self, volume, volume_installPath, ps):
        devPath = "/dev/" + volume_installPath.split("sharedblock://")[1]
        cmd = 'lvscan'
        conditions = res_ops.gen_query_conditions('primaryStorage.uuid', '=', ps.uuid)
        cluster = res_ops.query_resource(res_ops.CLUSTER, conditions)[0]
        conditions = res_ops.gen_query_conditions('clusterUuid', '=', cluster.uuid)
        host = res_ops.query_resource(res_ops.HOST, conditions)[0]
        result = test_lib.lib_execute_ssh_cmd(host.managementIp, 'root', 'password', cmd)
        if devPath in result:
            return self.judge(True)
        else:
            return self.judge(False)

    def check_mini(self, volume, volume_installPath, ps):
        devPath = "/dev/" + volume_installPath.split("mini://")[1]
        cmd = 'lvscan'
        conditions = res_ops.gen_query_conditions('primaryStorage.uuid', '=', ps.uuid)
        cluster = res_ops.query_resource(res_ops.CLUSTER, conditions)[0]
        conditions = res_ops.gen_query_conditions('clusterUuid', '=', cluster.uuid)
        host = res_ops.query_resource(res_ops.HOST, conditions)[0]
        result = test_lib.lib_execute_ssh_cmd(host.managementIp, 'root', 'password', cmd)
        if devPath in result:
            return self.judge(True)
        else:
            return self.judge(False)

    def check_iscsi(self, volume, volume_installPath, ps):
        host = test_lib.lib_find_host_by_iscsi_ps(ps)
        if not host:
            test_util.test_logger('Check result: can not find Host, who owns iscsi filesystem backend. [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
            return self.judge(False)
        test_lib.lib_install_testagent_to_host(host)
        volume_file_path = volume_installPath.split(';')[1].split('file://')[1]
        self.check_file_exist(volume, volume_file_path, host)

    def check_ceph(self, volume, volume_installPath, ps):
        monHost = ps.mons[0].hostname
        for key in os.environ.keys():
            if monHost in os.environ.get(key) and ":" in os.environ.get(key) and "@" in os.environ.get(key):
                print "debug message monHost and key is %s and %s" % (monHost,key)
                ceph_host, username, password = \
                        test_lib.lib_get_ceph_info(os.environ.get(key))
                break
        else:
            ceph_host = monHost
            username = 'root'
            password = 'password'

        volume_installPath = volume_installPath.split('ceph://')[1]
        command = 'rbd info %s' % volume_installPath
        if test_lib.lib_execute_ssh_cmd(ceph_host, username, password, command, 10):
            test_util.test_logger('Check result: [volume:] %s [file:] %s exist on ceph [host name:] %s .' % (volume.uuid, volume_installPath, ceph_host))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [volume:] %s [file:] %s does NOT exist on ceph [host name:] %s .' % (volume.uuid, volume_installPath, ceph_host))
            return self.judge(False)

    def check_nfs(self, volume, volume_installPath):
        host = test_lib.lib_get_volume_object_host(self.test_obj)
        if not host:
            test_util.test_logger('Check result: can not find Host, who is belonged to same Zone Uuid of [volume uuid: ] %s. Can not check volume file existence' % volume.uuid)
            return self.judge(False)

        self.check_file_exist(volume, volume_installPath, host)

    def check_file_exist(self, volume, volume_installPath, host):
        cmd = host_plugin.HostShellCmd()
        file_exist = "file_exist"
        cmd.command = '[ -f %s ] && echo %s' % (volume_installPath, file_exist)
        rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, host_plugin.HOST_SHELL_CMD_PATH), cmd)
        rsp = jsonobject.loads(rspstr)
        output = jsonobject.dumps(rsp.stdout)
        if file_exist in output:
            test_util.test_logger('Check result: [volume:] %s [file:] %s exist on [host name:] %s .' % (volume.uuid, volume_installPath, host.managementIp))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [volume:] %s [file:] %s does not exist on [host name:] %s .' % (volume.uuid, volume_installPath, host.managementIp))
            return self.judge(False)

class zstack_kvm_volume_attach_checker(checker_header.TestChecker):
    '''
        Check if volume is really attached to vm in libvirt system.
    '''
    def check(self):
        super(zstack_kvm_volume_attach_checker, self).check()
        volume = self.test_obj.volume
        if not volume.vmInstanceUuid:
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
        if volume_installPath.startswith('iscsi'):
            volume_installPath = volume_installPath.split(';')[0].split('/iqn')[1]
            volume_installPath = 'iqn%s' % volume_installPath
            volume_installPath = volume_installPath[:-2]
        elif volume_installPath.startswith('ceph'):
            volume_installPath = volume_installPath.split('ceph://')[1]
        elif volume_installPath.startswith('fusionstor'):
            volume_installPath = volume_installPath.split('fusionstor://')[1]
        elif volume_installPath.startswith('sharedblock'):
            volume_installPath = "/dev/" + volume_installPath.split('sharedblock://')[1]
        elif volume_installPath.startswith('mini'):
            _cmd = "drbdsetup show %s | grep device | awk -F';' '{print $1}' | awk '{print $3}'" % volume.uuid
            result = test_lib.lib_execute_ssh_cmd(host.managementIp,host.username, host.password, _cmd, 180)
            volume_installPath = '/dev/drbd' + result.strip()
        elif volume_installPath.startswith('ebs'):
            ps_uuid = volume.primaryStorageUuid
            ps = test_lib.lib_get_primary_storage_by_uuid(ps_uuid)
            url = ps.url.replace('ocean/api', 'dev/name')
            vol_id = volume_installPath.split(';')[1].split('volumeId=')[-1]
            req = urllib2.Request(url, headers={'Volumeid': vol_id})
            volume_installPath = '/dev/' + urllib2.urlopen(req).read().split('"')[-2]



        if volume_installPath in output:
            test_util.test_logger('Check result: [volume:] %s [file:] %s is found in [vm:] %s on [host:] %s .' % (volume.uuid, volume_installPath, vm.uuid, host.managementIp))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [volume:] %s [file:] %s is not found in [vm:] %s on [host:] %s .' % (volume.uuid, volume_installPath, vm.uuid, host.managementIp))
            return self.judge(False)
