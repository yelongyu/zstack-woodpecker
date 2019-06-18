'''

@author: Yetian
New install management node with 2.1.1 image and install one management node

'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.scenario_operations as sce_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
zstack_management_ip = os.environ.get('zstackManagementIp')
vm1_inv = None
vm2_inv = None

def create_vm(image):
    l3_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    image_uuid = image.uuid
    #vm_name = 'zs_install_new_install_management_node_%s' % image.name
    vm_name = os.environ.get('vmName')
    vm_instrance_offering_uuid = os.environ.get('instanceOfferingUuid')

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(vm_instrance_offering_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_inv = sce_ops.create_vm(zstack_management_ip, vm_creation_option)
    
    return vm_inv

def test():
    global vm1_inv
    global vm2_inv

    zstack_latest_version = os.environ.get('zstackLatestVersion')
    zstack_latest_path = os.environ.get('zstackLatestInstaller')

    iso_path = os.environ.get('iso_path')
    upgrade_script_path = os.environ.get('upgradeScript')

    test_util.test_dsc('Create 2 CentOS7 vm to test install management node installation')

    conditions = res_ops.gen_query_conditions('name', '=', os.environ.get('imageNameBase_21_ex'))
    #image = res_ops.query_resource(res_ops.IMAGE, conditions)[0]
    image = sce_ops.query_resource(zstack_management_ip, res_ops.IMAGE, conditions)[0]
    vm1_inv = create_vm(image) 
    vm2_inv = create_vm(image)

    vm1_ip = vm1_inv.vmNics[0].ip
    vm2_ip = vm2_inv.vmNics[0].ip

    time.sleep(60)
    test_stub.make_ssh_no_password(vm1_ip, tmp_file)
    test_stub.update_iso(vm1_ip, tmp_file, iso_path, upgrade_script_path)

    target_file = '/root/zstack-all-in-one.tgz'
    test_stub.prepare_test_env(vm1_inv, target_file)
    ssh_cmd1 = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm1_ip
    ssh_cmd2 = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm2_ip

    test_util.test_dsc('Install zstack 2.1.1 master mangement node on vm1')
    cmd= '%s "[ -e /usr/local/zstack ] && echo yes || echo no"' % ssh_cmd1
    (process_result, cmd_stdout) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('check /usr/local/zstack fail, cmd_stdout:%s' % cmd_stdout)
    cmd_stdout = cmd_stdout[:-1]
    if cmd_stdout == "yes":
        cmd = '%s "rm -rf /usr/local/zstack"' % ssh_cmd
        (process_result, cmd_stdout) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
        if process_result != 0:
            test_util.test_fail('delete /usr/local/zstack fail')
    test_stub.execute_all_install(ssh_cmd1, target_file, tmp_file)
    

    #test_util.test_dsc('Upgrade the latest master zstack')
    #test_stub.upgrade_zstack(vm1_ip, zstack_latest_path, tmp_file)
    #test_stub.check_zstack_version(vm1_ip, tmp_file, zstack_latest_version)
    #test_stub.start_mn(vm1_ip, tmp_file)
    #test_stub.check_installation(vm1_ip, tmp_file)

    test_util.test_dsc('only Install one management node on vm2')
    host_list = 'root:password@%s ' % vm2_ip
    cmd = '%s "zstack-ctl install_management_node --host=%s"' % (ssh_cmd1, host_list)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)

    test_util.test_dsc('Check installation on vm1')
    test_stub.check_installation(vm1_ip, tmp_file)

    test_util.test_dsc('Check installation on vm2')
    test_stub.make_ssh_no_password(vm2_ip, tmp_file)
    cmd = '%s "zstack-ctl start_node"' % ssh_cmd2
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    test_stub.check_installation(vm1_ip, tmp_file)

    test_util.test_dsc('check installation stop_node one ')
    test_stub.stop_node(vm1_ip, tmp_file)
    test_stub.start_node(vm2_ip, tmp_file)
    test_stub.check_installation(vm2_ip, tmp_file)

    test_util.test_dsc('check installation stop_node the second one ')
    test_stub.start_node(vm1_ip, tmp_file)
    test_stub.stop_node(vm2_ip, tmp_file)
    test_stub.check_installation(vm1_ip, tmp_file)

    os.system('rm -f %s' % tmp_file)
    sce_ops.destroy_vm(zstack_management_ip, vm1_inv.uuid)
    sce_ops.destroy_vm(zstack_management_ip, vm2_inv.uuid)

    test_util.test_pass('ZStack install management nodes installation Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm1_inv
    global vm2_inv
    
    os.system('rm -f %s' % tmp_file)
    sce_ops.destroy_vm(zstack_management_ip, vm1_inv.uuid)
    sce_ops.destroy_vm(zstack_management_ip, vm2_inv.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
