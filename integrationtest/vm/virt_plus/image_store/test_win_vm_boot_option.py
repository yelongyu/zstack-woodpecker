'''

New Integration test for testing cloned windows vm boot option. 

@author: ChenyuanXu 
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.shell as shell
# import test_stub
import time
import os
from vncdotool import api

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vn_prefix = 'vm-clone-%s' % time.time()
vm_name = ['%s-vm1' % vn_prefix]
node_ip = os.environ.get('node1Ip')
boot_option_picture = "/home/%s/zstack-woodpecker/win_boot.png" % node_ip

def test():
    global test_obj_dict
    global vm
    import signal
    def handler(signum, frame):
        raise Exception()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(300)
    test_util.test_dsc('Create test clone windows vm boot option')

    image_name = os.environ.get('imageName_windows')
    vm = test_stub.create_vm(image_name = image_name)
    test_obj_dict.add_vm(vm)

    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    for bs in backup_storage_list:
        if bs.type in [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE, inventory.CEPH_BACKUP_STORAGE_TYPE]:
            break
    else:
        vm.destroy()
        test_util.test_skip('Not find image store or ceph type backup storage.')

    new_vm = vm.clone(vm_name)[0]
    test_obj_dict.add_vm(new_vm)
    console = test_lib.lib_get_vm_console_address(new_vm.get_vm().uuid)
    test_util.test_logger('[vm:] %s console is on %s:%s' % (new_vm.get_vm().uuid, console.hostIp, console.port))
    display = str(int(console.port)-5900)

    client = api.connect(console.hostIp+":"+display)
    client.keyPress('esc')
    time.sleep(2)
    client.expectRegion(boot_option_picture,0,100)

    vm.destroy()
    new_vm.destroy()

    test_util.test_pass('VM With Volumes Boot Option Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
