'''

New Integration Test for libvirt restart with snapshot.

@author: Jiajun Xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global vm
    loop = 20
    count = 0
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vm("test_libvirt_snapshot_vm", image_name, l3_name)
    test_obj_dict.add_vm(vm)
    vm.check()

    volume_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid
     
    snapshots = test_obj_dict.get_volume_snapshot(volume_uuid)
    snapshots.set_utility_vm(vm)
    while count <= loop:
        sp_name = "create_snapshot" + str(count)
        snapshots.create_snapshot(sp_name)
        snapshots.check()
        count += 1

    host = test_lib.lib_find_host_by_vm(vm.get_vm())
    result = test_lib.lib_execute_ssh_cmd(host.managementIp, 'root', 'password', 'service libvirtd restart')

    time.sleep(600)

    vm.check()
    snapshots.check()

    snapshots.delete()
    test_obj_dict.rm_volume_snapshot(snapshots)
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Libvirt restart with snapshot passed')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
