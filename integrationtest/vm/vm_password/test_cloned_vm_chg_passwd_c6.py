'''
test for cloned vm changing password
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstacklib.utils.ssh as ssh
import test_stub
import time




exist_users = ["root"]

users   = ["root",       "aa"            ]
passwds = ["95_aaapcn",  "0_aIGFDFBBN"   ]

vm = None

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vn_prefix = 'vm-clone-%s' % time.time()
#vm_names = ['%s-cloned-vm1' % vn_prefix, '%s-cloned-vm2' % vn_prefix]
#in_vm_names = ['%s-twice-cloned-vm1' % vn_prefix, '%s-twice-cloned-vm2' % vn_prefix]

vm_names = ['%s-cloned-vm1' % vn_prefix]
in_vm_names = ['%s-twice-cloned-vm1' % vn_prefix]

def force_vm_auto_boot(vm):
    cmd = "sed -i \"s/  set timeout=-1/  set timeout=3/g\" /boot/grub/grub.cfg; sync"
    ret, output, stderr = ssh.execute(cmd, vm.get_vm().vmNics[0].ip, "root", "password", False, 22)
    if ret != 0:
        test_util.test_logger("Force vm auto boot setting failed.")



def test():
    global vm, exist_users
    test_util.test_dsc('cloned vm change password test')

    vm = test_stub.create_vm(vm_name = '1st-created-vmi-c6', image_name = "imageName_i_c6")
    test_obj_dict.add_vm(vm)
    vm.check()

    force_vm_auto_boot(vm)

    test_util.test_logger("change vm password for initial created vm")
    inv = vm_ops.change_vm_password(vm.get_vm().uuid, "root", "password", skip_stopped_vm = None, session_uuid = None)
    if not inv:
        test_util.test_fail("change vm password failed")
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    for bs in backup_storage_list:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
        #if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
        #    break
        #if bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
        #    break
    else:
        vm.destroy()
        test_util.test_skip('Not find image store type backup storage.')

    for (usr,passwd) in zip(users, passwds):
        if usr not in exist_users:
            test_util.test_logger("find new account: <%s:%s>" %(usr, passwd))
            test_stub.create_user_in_vm(vm.get_vm(), usr, passwd) 
            exist_users.append(usr)

        #new vm->cloned new_vm1/new_vm2
        test_util.test_logger("1st clone")
        new_vms = vm.clone(vm_names)

        if len(new_vms) != len(vm_names):
            test_util.test_fail('only %s VMs have been cloned, which is less than required: %s' % (len(new_vms), vm_names))

        for new_vm in new_vms:
            new_vm.update()
            #new_vm.check()
            test_obj_dict.add_vm(new_vm)

            #When vm is running:
            test_util.test_logger("vm running && change 1st cloned vm password:<%s:%s:%s>" %(new_vm, usr, passwd))
            inv = vm_ops.change_vm_password(new_vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)
            if not inv:
                test_util.test_fail("change cloned vms password failed")

            if not test_lib.lib_check_login_in_vm(new_vm.get_vm(), usr, passwd):
                test_util.test_fail("check login cloned vm with user:%s password: %s failed", usr, passwd)

            #When vm is stopped:
            new_vm.stop()
            test_util.test_logger("vm stopped && change 1st cloned vm password:<%s:%s:%s>" %(new_vm, usr, passwd))
            inv = vm_ops.change_vm_password(new_vm.get_vm().uuid, "root", test_stub.original_root_password)
            if not inv:
                test_util.test_fail("recover vm password failed")

            new_vm.start()
            new_vm.check()
            
            #test use the cloned vm change password to clone new vm and then change password
            test_util.test_logger("2nd cloned")
            in_new_vms = new_vm.clone(in_vm_names)

            new_vm.destroy()
            new_vm.check()
            new_vm.expunge()
            new_vm.check()

            for in_new_vm in in_new_vms:
                in_new_vm.update()
                test_obj_dict.add_vm(in_new_vm)

                test_util.test_logger("vm running && change 2nd cloned vm password:<%s:%s:%s>" %(new_vm, usr, passwd))
                inv = vm_ops.change_vm_password(in_new_vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)
                if not inv:
                    test_util.test_fail("change cloned in_vm password failed")

                if not test_lib.lib_check_login_in_vm(in_new_vm.get_vm(), usr, passwd):
                    test_util.test_fail("check login cloned in_vm with user:%s password: %s failed", usr, passwd)

                #When vm is stopped:
                in_new_vm.stop()
                test_util.test_logger("vm stopped && change 2nd cloned vm password:<%s:%s:%s>" %(new_vm, usr, passwd))
                inv = vm_ops.change_vm_password(in_new_vm.get_vm().uuid, "root", test_stub.original_root_password)
                if not inv:
                    test_util.test_fail("recover vm password failed")

                in_new_vm.start()
                in_new_vm.check()
                in_new_vm.destroy()
                in_new_vm.check()
                in_new_vm.expunge()
                in_new_vm.check()

    vm.destroy()
    vm.check()

    vm.expunge()
    vm.check()

    test_util.test_pass('Set password when VM is creating is successful.')


#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_robot_cleanup(test_obj_dict)
