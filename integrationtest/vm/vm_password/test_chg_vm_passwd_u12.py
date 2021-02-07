'''
test for changing vm password
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

users   = ["root",      "root"      ]
passwds = ["password",  "95_aaapcn" ]

vm = None
cur_usr = None
cur_passwd = None

def check_vm_is_alive(vm):
    global cur_usr, cur_passwd
    cmd = "pwd"
    ret, output, stderr = ssh.execute(cmd, vm.get_vm().vmNics[0].ip, cur_usr, cur_passwd, False, 22)
    if ret != 0:
        test_util.test_logger("VM is not alived when exception triggered: ip:%s; cmd:%s; user:%s; password:%s; stdout:%s, stderr:%s" %(vm.get_vm().vmNics[0].ip, cmd, cur_usr, cur_passwd, output, stderr))

def check_qemu_ga_is_alive(vm):
    global cur_usr, cur_passwd
    cmd = "ps -aux|grep ga|grep qemu"
    ret, output, stderr = ssh.execute(cmd, vm.get_vm().vmNics[0].ip, cur_usr, cur_passwd, False, 22)
    if ret != 0:
        test_util.test_logger("qemu-ga is not alived when exception triggered: ip:%s; cmd:%s; user:%s; password:%s; stdout:%s, stderr:%s" %(vm.get_vm().vmNics[0].ip, cmd, cur_usr, cur_passwd, output, stderr))


def test():
    global vm, exist_users, cur_usr, cur_passwd
    test_util.test_dsc('change VM with assigned password test')

    image_name = "imageName_i_u12"
    ps_type = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].type
    if ps_type == 'MiniStorage':
        image_name = os.environ.get(image_name)
    vm = test_stub.create_vm(vm_name='ckvmpswd-u12-64', image_name=image_name)
    vm.check()

    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    for bs in backup_storage_list:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
        if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
            break
        if bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
            break
    else:
        vm.destroy()
        test_util.test_skip('Not find image store type backup storage.')

    cur_usr = "root"
    cur_passwd = "password"

    vm_ops.set_vm_qga_enable(vm.get_vm().uuid)

    for (usr,passwd) in zip(users, passwds):

        #When vm is running:
        vm_ops.change_vm_password(vm.get_vm().uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None)

        cur_usr = usr
        cur_passwd = passwd

        if not test_lib.lib_check_login_in_vm(vm.get_vm(), usr, passwd):
            test_util.test_fail("create vm with user:%s password: %s failed", usr, passwd)

        #When vm is stopped:
        #vm.stop()
        vm_ops.change_vm_password(vm.get_vm().uuid, "root", test_stub.original_root_password)

        cur_usr = "root"
        cur_passwd = "password"

        #vm.start()
        vm.check()


    vm.destroy()
    vm.check()

    vm.expunge()
    vm.check()

    test_util.test_pass('Set password when VM is creating is successful.')


#Will be called only if exception happens in test().
def error_cleanup():
    global vm

    check_vm_is_alive(vm)
    check_qemu_ga_is_alive(vm)

    if vm:
        vm.destroy()
        vm.expunge()
