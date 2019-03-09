'''

@author: MengLai
'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.console_operations as cons_ops
import zstackwoodpecker.operations.scenario_operations as sce_ops 
import zstacklib.utils.ssh as ssh

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
zstack_management_ip = os.environ.get('zstackManagementIp')
vm_inv = None

def create_vm(image):
    l3_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    image_uuid = image.uuid
    #vm_name = 'zs_install_inst_console_proxy_%s' % image.name
    vm_nme = os.environ.get('vmName')
    vm_instrance_offering_uuid = os.environ.get('instanceOfferingUuid')

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(vm_instrance_offering_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_inv = sce_ops.create_vm(zstack_management_ip, vm_creation_option)

    return vm_inv

def test():
    global vm_inv
    
    iso_path = os.environ.get('iso_path')
    upgrade_script_path = os.environ.get('upgradeScript')
    test_util.test_dsc('Create test vm to test zstack installation with console proxy.')

    conditions = res_ops.gen_query_conditions('name', '=', os.environ.get('imageNameBase_21_ex'))
    image = res_ops.query_resource(res_ops.IMAGE, conditions)[0]

    vm_inv = create_vm(image) 

    time.sleep(60)

    vm_ip = vm_inv.vmNics[0].ip
    vip = '172.20.61.253'
    if vip == vm_ip:
        vip = '172.20.61.254'

    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), test_lib.lib_get_vm_password(vm_inv))
    cmd = '%s ifconfig eth0:0 %s up' % (ssh_cmd, vip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)

    test_stub.update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path)

    target_file = '/root/zstack-all-in-one.tgz'
    test_stub.prepare_test_env(vm_inv, target_file)
    args = '-o -C %s -I %s' % (vip, vm_ip)
    test_stub.execute_install_with_args(ssh_cmd, args, target_file, tmp_file)
    test_stub.check_installation(vm_ip, tmp_file)

    cmd = '%s cat /usr/local/zstack/apache-tomcat/webapps/zstack/WEB-INF/classes/zstack.properties | grep \'consoleProxyOverriddenIp = %s\'' % (ssh_cmd, vip)
    (process_result, check_result) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
    check_result = check_result[:-1]
    test_util.test_dsc('cat result: |%s|' % check_result)
    expect_result = "consoleProxyOverriddenIp = %s" % vip
    if check_result != expect_result:
        test_util.test_fail('Fail to install ZStack with console proxy')

    os.system('rm -f %s' % tmp_file)
    sce_ops.destroy_vm(zstack_management_ip, vm_inv.uuid)    
    test_util.test_pass('ZStack installation Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_inv

    os.system('rm -f %s' % tmp_file)
    sce_ops.destroy_vm(zstack_management_ip, vm_inv.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
