'''
negative test for changing vm password with invalid password
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import os

test_stub = test_lib.lib_get_specific_stub()

exist_users = ["root"]

users   = [ "bc"       ]
passwds = [ "x"*265    ]


vm = None

def test():
    global vm, exist_users
    test_util.test_dsc('change VM with assigned password test')

    image_name = "imageName_i_c7"
    ps_type = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].type
    if ps_type == 'MiniStorage':
        image_name = os.environ.get(image_name)

    for (usr,passwd) in zip(users, passwds):

        test_util.test_dsc("username:%s, password: \"%s\"" %(usr, passwd))

        #Create VM API
        if usr == "root":
            try:
                vm = test_stub.create_vm(vm_name='c7-vm', image_name=image_name, root_password=passwd)
            except:
                pass
            else:
                test_util.test_fail("create vm && the invaild password: %s successfully be set" % (passwd))

        #Check bs type
        vm = test_stub.create_vm(vm_name='c7-vm', image_name=image_name)
        vm.check()
        vm_ops.set_vm_qga_enable(vm.get_vm().uuid)
        backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
        for bs in backup_storage_list:
            if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
                break
            if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
                break
            if bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
                break
        else:
            test_util.test_skip('Not find image store type backup storage.')

        #inject normal account username/password
        if usr not in exist_users:
            test_stub.create_user_in_vm(vm.get_vm(), usr, "password")
            exist_users.append(usr)


        #Change VM API && Running
        try:
            vm_ops.change_vm_password(vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)
        except:
            pass
        else:
            test_util.test_fail("vm running && the invaild password: %s successfully be set" %(passwd))

        #Change VM API && Stopped
        #vm.stop()
        try:
            vm_ops.change_vm_password(vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)
        except:
            pass
        else:
            test_util.test_fail("vm stopped && the invaild password: %s successfully be set" %(passwd))

        #vm.start()
        vm.check()

        if not test_lib.lib_check_login_in_vm(vm.get_vm(), "root", "password"):
            test_util.test_fail("create vm with root password: \"password\" failed")

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
