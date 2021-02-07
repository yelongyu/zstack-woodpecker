'''

New Integration test for testing vm with 2 additional data volumes boot option. 

@author: ChenyuanXu
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.shell as shell
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os
from vncdotool import api

test_stub = test_lib.lib_get_specific_stub()
test_obj_dict = test_state.TestStateDict()
node_ip = os.environ.get('node1Ip')
boot_option_picture = "/home/%s/zstack-woodpecker/vm_volumes_boot.png" % node_ip
vm = None

def test():
    global test_obj_dict
    global vm
    import signal
    def handler(signum, frame):
        raise Exception()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)

    test_util.test_dsc('Create test vm with 2 additional data volumes boot option')
    conf_ops.change_global_config('vm', 'bootMenu', 'false')

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, [])[0]
    if ps.type != "MiniStorage":
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        disk_offering_uuids = [disk_offering.uuid]
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName'))
        disk_offering_uuids.append(disk_offering.uuid)
        vm = test_stub.create_vm_with_volume(data_volume_uuids = disk_offering_uuids)
    else:
        vm = test_stub.create_vm()
        vol1 = test_stub.create_volume('mini_volume_1')
        vol2 = test_stub.create_volume('mini_volume_2')
        vol1.attach(vm)
        vol2.attach(vm)
    test_obj_dict.add_vm(vm)
    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid)
    test_util.test_logger('[vm:] %s console is on %s:%s' % (vm.get_vm().uuid, console.hostIp, console.port))
    display = str(int(console.port)-5900)

    client = api.connect(console.hostIp+":"+display)
    time.sleep(2)
    client.keyPress('esc')
    try:
        client.expectRegion(boot_option_picture,0,100)
    except:
        test_util.test_logger('Success to not enable boot menu.')
    else:
        test_util.test_fail('Fail to not enable boot menu.')

    vm.destroy()
    test_util.test_pass('VM With Volumes Boot Option Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()

