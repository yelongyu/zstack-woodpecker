'''

@author:MengLai 
'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.deploy_operations as deploy_operations

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()

node_ip = os.environ.get('node1Ip')
origin_ip = None
test_config_des = "/home/%s/zstack-woodpecker/integrationtest/vm/installation/test-config-vm-check.xml" % node_ip 
deploy_tmpt_src = "/home/%s/zstack-woodpecker/integrationtest/vm/installation/deploy-vm-check-template.tmpt" % node_ip
deploy_tmpt_des = "/home/%s/zstack-woodpecker/integrationtest/vm/installation/deploy-vm-check.tmpt" % node_ip

def test():
    global test_obj_dict
    global origin_ip
    global test_config_des
    global deploy_tmpt_src
    global deploy_tmpt_des

    origin_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']

    test_util.test_dsc('Create test vm to test zstack all installation in CentOS7.')
#    image_name = os.environ.get('imageName_i_c7')
#    image_name = "zstack_iso_centos7_141"
    image_name = os.environ.get('imageName_i_offline')
    vm = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm)
    if os.environ.get('zstackManagementIp') == None:
        vm.check()
    else:
        time.sleep(60)

    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    target_file = '/root/zstack-all-in-one.tgz'
    test_stub.prepare_test_env(vm_inv, target_file)
    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    test_stub.execute_all_install(ssh_cmd, target_file, tmp_file)

#    test_stub.check_installation(ssh_cmd, tmp_file, vm_inv)

    test_util.test_dsc("Prepare Config Files")
    cmd = "cp %s %s" % (deploy_tmpt_src, deploy_tmpt_des)
    os.system(cmd)
    cmd = "sed -i \"s/templateIP/%s/g\" %s" % (vm_ip, deploy_tmpt_des)
    os.system(cmd)

    test_config_obj = test_util.TestConfig(test_config_des)
    test_config = test_config_obj.get_test_config()
    all_config = test_config_obj.get_deploy_config()
    deploy_config = all_config.deployerConfig
    cmd = "vconfig add zsn0 213"
    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 180)
    cmd = "vconfig add zsn0 212"
    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 180)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = vm_ip
    deploy_operations.deploy_initial_database(deploy_config)

    test_util.test_dsc("Clean up")
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = origin_ip
    os.system('rm -f %s' % deploy_tmpt_des) 
    os.system('rm -f %s' % tmp_file)
    vm.destroy()
    test_obj_dict.rm_vm(vm)
    test_util.test_pass('ZStack installation Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    global origin_ip
    global deploy_tmpt_des
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = origin_ip 
    os.system('rm -f %s' % tmp_file)
    os.system('rm -f %s' % deploy_tmpt_des)
    test_lib.lib_error_cleanup(test_obj_dict)
