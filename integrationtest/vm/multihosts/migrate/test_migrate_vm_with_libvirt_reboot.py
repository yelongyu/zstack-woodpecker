'''

New Integration test for testing vm migration between hosts with libvirt reboot

@author: Jiajun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os

vm = None
test_stub = test_lib.lib_get_specific_stub()

def test():
    global vm

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for i in ps:
        if i.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
            break
        else:
            test_util.test_skip('Skip test on non-Ceph PS')

    cmd = 'service libvirtd restart'
    vm = test_stub.create_vr_vm('migrate_vm', 'imageName_s', 'l3VlanNetwork2')
    vm.check()
    
    host = test_lib.lib_find_host_by_vm(vm.get_vm())

    rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), cmd)
    if rsp:
        test_util.test_fail('%s failed on %s' % (cmd, host.managementIp))
    else:
        test_util.test_logger('%s successfully run on %s' % (cmd, host.managementIp))

    test_stub.migrate_vm_to_random_host(vm)
    vm.check()

    cmd = 'virsh secret-list | grep -v UUID | grep -v ^$ | wc -l'
    rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), cmd)
    if rsp and int(rsp) != 2:
        test_util.test_fail('no virsh secret found on %s, should be a bug' % (host.managementIp))
    else:
        test_util.test_logger('virsh secret is found on %s' % (host.managementIp))

    vm.stop()
    vm.check()

    vm.start()
    vm.check()

    vm.destroy()
    test_util.test_pass('Migrate VM Ops Test Success')


#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
