'''
Cloned vm change password
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


#users   = ["root",     "root",     "root",       "root", "root",                 "a", "aa", " a", "a:@", "???", "."]
#passwds = ["password", "98765725", "95_aaapcn ", "0",    "9876,*&#$%^&**&()+_=", "0", "a.", " .", ")" ,  "^",  "+"]
exist_users = ["root"]

users   = ["root",      "root",       "_a",          "aa"  ]
passwds = ["password",  "95_aaapcn",  "_0aIGFDFBBN", "a1_" ]

vm = None

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vn_prefix = 'vm-clone-%s' % time.time()
vm_names = ['%s-cloned-vm1' % vn_prefix, '%s-cloned-vm2' % vn_prefix]
in_vm_names = ['%s-twice-cloned-vm1' % vn_prefix, '%s-twice-cloned-vm2' % vn_prefix]


def test():
    global vm, exist_users
    test_util.test_dsc('cloned vm change password test')

    vm = test_stub.create_vm(vm_name = '1st-created-vm', image_name = "imageName_i_c7")
    test_obj_dict.add_vm(vm)
    vm.check()

    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    for bs in backup_storage_list:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
        if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
            break
    else:
        vm.destroy()
        test_util.test_skip('Not find image store type backup storage.')

    for (usr,passwd) in zip(users, passwds):
        if usr not in exist_users:
            test_stub.create_user_in_vm(vm.get_vm(), usr, passwd) 
            exist_users.append(usr)

        #new vm->cloned new_vm1/new_vm2
        new_vms = vm.clone(vm_names)

        if len(new_vms) != len(vm_names):
            test_util.test_fail('only %s VMs have been cloned, which is less than required: %s' % (len(new_vms), vm_names))

        for new_vm in new_vms:
            new_vm.update()
            test_obj_dict.add_vm(new_vm)

            #When vm is running:
            inv = vm_ops.change_vm_password(new_vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)
            if not inv:
                test_util.test_fail("change cloned vms password failed")

            if not test_lib.lib_check_login_in_vm(new_vm.get_vm(), usr, passwd):
                test_util.test_fail("check login cloned vm with user:%s password: %s failed", usr, passwd)

            #When vm is stopped:
            new_vm.stop()
            inv = vm_ops.change_vm_password(new_vm.get_vm().uuid, "root", test_stub.original_root_password)
            if not inv:
                test_util.test_fail("recover vm password failed")

            new_vm.start()
            new_vm.check()
            
            #test use the cloned vm change password to clone new vm and then change password
            in_new_vms = new_vm.clone(in_vm_names)

            new_vm.destroy()
            new_vm.check()
            new_vm.expunge()
            new_vm.check()

            for in_new_vm in in_new_vms:
                in_new_vm.update()
                test_obj_dict.add_vm(in_new_vm)

                inv = vm_ops.change_vm_password(in_new_vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)
                if not inv:
                    test_util.test_fail("change cloned in_vm password failed")

                if not test_lib.lib_check_login_in_vm(in_new_vm.get_vm(), usr, passwd):
                    test_util.test_fail("check login cloned in_vm with user:%s password: %s failed", usr, passwd)

                #When vm is stopped:
                in_new_vm.stop()
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
