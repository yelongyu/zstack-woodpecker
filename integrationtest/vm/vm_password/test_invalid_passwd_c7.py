'''
Change VM password
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstacklib.utils.ssh as ssh
import test_stub


#users   = ["root",     "root",     "root",       "root", "root",                 "a", "aa", " a", "a:@", "???", "."]
#passwds = ["password", "98765725", "95_aaapcn ", "0",    "9876,*&#$%^&**&()+_=", "0", "a.", " .", ")" ,  "^",  "+"]
exist_users = ["root"]

users   = ["root",      "root",      "root",    "root",          "_aa", "bc ", " & a", " "  ]
passwds = ["*#$",       " ",         "*"*265,   "",              "&ad", " "*265, "aa", "??" ] 


vm = None

def test():
    global vm, exist_users
    test_util.test_dsc('change VM with assigned password test')


    for (usr,passwd) in zip(users, passwds):

        test_util.test_dsc("username:%s, password: \"%s\"" %(usr, passwd))

        #Create VM API
        try:
            vm = test_stub.create_vm(vm_name = passwd +'-c7-vm', image_name = "imageName_i_c7", root_password=root_password)
            test_util.test_fail("the invaild password: %s successfully be set", passwd)
        except:
            pass

        #Check bs type
        vm = test_stub.create_vm(vm_name = passwd +'-c7-vm', image_name = "imageName_i_c7")
        backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
        for bs in backup_storage_list:
            if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
                break
            if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
                break
        else:
            test_util.test_skip('Not find image store type backup storage.')

        #inject normal account username/password
        if usr not in exist_users:
            test_stub.create_user_in_vm(vm.get_vm(), usr, passwd) 
            exist_users.append(usr)


        #Change VM API && Running
        try:
            vm_ops.change_vm_password(vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)
            test_util.test_fail("the invaild password: %s successfully be set", passwd)
        except:
            pass


        #Change VM API && Stopped
        vm.stop()
        try:
            vm_ops.change_vm_password(vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)
            test_util.test_fail("the invaild password: %s successfully be set", root_password)
        except:
            pass

        if not test_lib.lib_check_login_in_vm(vm.get_vm(), "root", "password"):
            test_util.test_fail("create vm with root password: \"password\" failed")

        #vm.start()
        #vm.check()
        vm.destroy()
        vm.expunge()
        vm.check()

    test_util.test_pass('Invalid password test is passed.')


#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
        vm.expunge()
