'''
@author: YeTian  2017-12-23
Test on centos72 mini iso installed zstack 2.2.2 release 381, upgrade the latest zstack
and add zone cluster host ps bs l2 l3 image offering  and create a vm with falt-network
'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.operations.resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
vm_inv = None
new_vm_inv = None

def create_new_vm(new_image):
    new_vm_name = 'new_vm_%s' % image_inv.name
    l3_net_uuid = l3_inv.inventory.uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(vmoffering_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(new_vm_name)
    new_vm_inv = sce_ops.create_vm(vm_ip, vm_creation_option)

    return new_vm_inv

def test():
    global vm_inv
    global zone_inv
    global cluster_inv
    global host_inv
    global bs_inv
    global image_inv
    global vmoffering_inv
    global l2_inv
    global l3_inv
    global l3_uuid
    global image_uuid
    global vmoffering_uuid
    global image_uuid
    global vm_ip

    test_util.test_dsc('Create test vm to test zstack upgrade on centos72 mini iso with zstack 2.2.2 by -u.')

    image_name = os.environ.get('imageNameBase_c72_222_mn')
    iso_path = os.environ.get('iso_path')
    zstack_latest_version = os.environ.get('zstackLatestVersion')
    zstack_latest_path = os.environ.get('zstackLatestInstaller')
    vm_name = os.environ.get('vmName')
    upgrade_script_path = os.environ.get('upgradeScript')

    vm_inv = test_stub.create_vm_scenario(image_name, vm_name)
    vm_ip = vm_inv.vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, 22)

    test_stub.make_ssh_no_password(vm_ip, tmp_file)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = vm_ip

    test_util.test_logger('Update MN IP')
    test_stub.update_mn_hostname(vm_ip, tmp_file)
    test_stub.update_mn_ip(vm_ip, tmp_file)
    test_stub.start_mn(vm_ip, tmp_file)
    #test_stub.check_installation(vm_ip, tmp_file)

    test_util.test_dsc('create zone names is zone1')
    zone_inv = test_stub.create_zone1(vm_ip, tmp_file)
    zone_uuid = zone_inv.uuid

    test_util.test_dsc('create cluster names is clsuter1')
    cluster_name = 'Cluster1'
    cluster_inv = test_stub.create_cluster1(vm_ip, cluster_name, zone_uuid, tmp_file)
    cluster_uuid = cluster_inv.uuid

    test_util.test_dsc('add HOST names is HOST1')
    host_name = 'host1'
    host_ip = vm_ip
    host_inv = test_stub.add_kvm_host1(vm_ip, host_ip, host_name,  cluster_uuid, tmp_file)
    host_uuid = host_inv.uuid

    test_util.test_dsc('add ps names is PS1')
    ps_inv = test_stub.create_local_ps(vm_ip, zone_uuid, tmp_file)
    ps_uuid = ps_inv.uuid

    test_stub.attach_ps(vm_ip, ps_uuid, cluster_uuid, tmp_file)

    test_util.test_dsc('add BS names is bs1')
    bs_inv = test_stub.create_sftp_backup_storage(vm_ip, tmp_file)
    bs_uuid = bs_inv.uuid

    test_stub.attach_bs(vm_ip, bs_uuid, zone_uuid, tmp_file)

    test_util.test_dsc('add image names is image1.4')
    image_inv = test_stub.add_image_local(vm_ip, bs_uuid, tmp_file)
    image_uuid = image_inv.uuid

    test_util.test_dsc('add vm instance offering names is 1-1G')
    vmoffering_inv = test_stub.create_vm_offering(vm_ip, tmp_file)
    vmoffering_uuid = vmoffering_inv.uuid

    test_util.test_dsc('create L2_vlan network  names is L2_vlan')
    l2_inv = sce_ops.create_l2_vlan(vm_ip, 'L2_vlan', 'eth0', '2200', zone_uuid)
    l2_uuid = l2_inv.inventory.uuid

    test_util.test_dsc('attach L2 netowrk to cluster')
    sce_ops.attach_l2(vm_ip, l2_uuid, cluster_uuid)

    test_util.test_dsc('create L3_flat_network names is L3_flat_network')
    l3_inv = sce_ops.create_l3(vm_ip, 'l3_flat_network', 'L3BasicNetwork', l2_uuid, 'local.com')
    l3_uuid = l3_inv.inventory.uuid

    l3_dns = '223.5.5.5'
    start_ip = '192.168.109.5'
    end_ip = '192.168.109.200'
    gateway = '192.168.109.1'
    netmask = '255.255.255.0'

    test_util.test_dsc('add DNS and IP_Range for L3_flat_network')
    sce_ops.add_dns_to_l3(vm_ip, l3_uuid, l3_dns)
    sce_ops.add_ip_range(vm_ip,'IP_range', l3_uuid, start_ip, end_ip, gateway, netmask)

    test_util.test_dsc('query flat provider and attach network service to  L3_flat_network')
    provider_name = 'Flat Network Service Provider'
    conditions = res_ops.gen_query_conditions('name', '=', provider_name)
    net_provider_list = sce_ops.query_resource(vm_ip, res_ops.NETWORK_SERVICE_PROVIDER, conditions).inventories[0]
    pro_uuid = net_provider_list.uuid
    sce_ops.attach_flat_network_service_to_l3network(vm_ip, l3_uuid, pro_uuid)

    test_util.test_dsc('create a vm with L3_flat_network')
    new_vm_inv = create_new_vm(image_inv)

    test_util.test_logger('Upgrade zstack to latest') 
    test_stub.update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path)
    test_stub.upgrade_zstack(vm_ip, zstack_latest_path, tmp_file) 
    test_stub.check_zstack_version(vm_ip, tmp_file, zstack_latest_version)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_mn_running(vm_ip, tmp_file)
    #test_stub.check_installation(vm_ip, tmp_file)

    os.system('rm -f %s' % tmp_file)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_util.test_pass('ZStack upgrade from centos72 mini iso 2.2.2 to the latest master zstack Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_inv
    global zone_inv
    global cluster_inv
    global host_inv
    global ps_inv
    global bs_inv
    global image_inv
    global vmoffering_inv
    global l2_inv
    global l3_inv

    os.system('rm -f %s' % tmp_file)
    if vm_inv:
        test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
