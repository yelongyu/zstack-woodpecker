'''
@author: YeTian
Test install management node with centos7.2 mini image and upgrade zstack iso and add the host
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
vm_inv = None

def create_vm(image):
    l3_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid =  test_lib.lib_get_l3_by_name(l3_name).uuid
    image_uuid = image.uuid
    #vm_name = 'zs_install_%s' % image.name
    vm_name = os.environ.get('vmName')
    vm_instance_offering_uuid = os.environ.get('instanceOfferingUuid')
    
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(vm_instance_offering_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_inv = sce_ops.create_vm(zstack_management_ip, vm_creation_option)

    return vm_inv

def test():
    global vm_inv
    global zone_inv
    global cluster_inv
    global host_inv

    test_util.test_dsc('Create test vm to test zstack install MN on centos7.2 and add the HOST')
    
    conditions = res_ops.gen_query_conditions('name', '=', os.environ.get('imageNameBase_c72'))
    #image = res_ops.query_resource(res_ops.IMAGE, conditions)[0]
    image = sce_ops.query_resource(zstack_management_ip, res_ops.IMAGE, conditions)[0]
    vm_inv = create_vm(image)
    time.sleep(100)
    iso_path = os.environ.get('iso_path')
    upgrade_script_path = os.environ.get('upgradeScript')

    test_util.test_dsc('Install zstack with -o')
    vm_ip = vm_inv.vmNics[0].ip
    test_stub.make_ssh_no_password(vm_ip, tmp_file)
    test_util.test_dsc('Upgrade master iso')
    test_stub.update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path)

    target_file = '/root/zstack-all-in-one.tgz'
    test_stub.prepare_test_env(vm_inv, target_file)
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    args = "-o"

    test_util.test_dsc('start installing the latest zstack-MN')

    test_stub.execute_install_with_args(ssh_cmd, args, target_file, tmp_file)

    test_util.test_dsc('check add the sftp bs and delete the sftp bs')
    test_stub.check_installation(vm_ip, tmp_file)

    test_util.test_dsc('create zone name is zone1')
    zone_inv = test_stub.create_zone1(vm_ip, tmp_file)
    zone_uuid = zone_inv.uuid
   
    test_util.test_dsc('create cluster name is clsuter1')

    cluster_inv = test_stub.create_cluster1(vm_ip, zone_uuid, tmp_file)
    cluster_uuid = cluster_inv.uuid

    test_util.test_dsc('add host name is HOST1')

    host_inv = test_stub.add_kvm_host1(vm_ip, cluster_uuid, tmp_file)
    host_uuid = host_inv.uuid

    os.system('rm -f %s' % tmp_file)
    sce_ops.destroy_vm(zstack_management_ip, vm_inv.uuid)
    test_util.test_pass('Install ZStack with -o  centos7.2 mini-iso Success')


def error_cleanup():
    global vm_inv
    global zone_inv
    global cluster_inv
    global host_inv

    os.system('rm -f %s' % tmp_file)
    sce_ops.destroy_vm(zstack_management_ip, vm_inv.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
    
