'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os
import sys
import time
import threading

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.hybrid_operations as hyb_ops

Port = test_state.Port

rule1_ports = Port.get_ports(Port.rule1_ports)
rule2_ports = Port.get_ports(Port.rule2_ports)
rule3_ports = Port.get_ports(Port.rule3_ports)
rule4_ports = Port.get_ports(Port.rule4_ports)
rule5_ports = Port.get_ports(Port.rule5_ports)
denied_ports = Port.get_denied_ports()
#rule1_ports = [1, 22, 100]
#rule2_ports = [9000, 9499, 10000]
#rule3_ports = [60000, 60010, 65535]
#rule4_ports = [5000, 5501, 6000]
#rule5_ports = [20000, 28999, 30000]
#test_stub.denied_ports = [101, 4999, 8990, 15000, 30001, 49999]
target_ports = rule1_ports + rule2_ports + rule3_ports + rule4_ports + rule5_ports + denied_ports


def create_ecs_instance(datacenter_type, datacenter_uuid, region_id, allocate_public_ip=False):
    iz_list = hyb_ops.get_identity_zone_from_remote(datacenter_type, region_id)
    for i in range(len(iz_list)):
        zone_id = iz_list[i].zoneId
        iz_inv = hyb_ops.add_identity_zone_from_remote(datacenter_type, datacenter_uuid, zone_id)
        ecs_instance_type = hyb_ops.get_ecs_instance_type_from_remote(iz_inv.uuid)
        if ecs_instance_type:
            break
#     cond_offering = res_ops.gen_query_conditions('name', '=', os.environ.get('instanceOfferingName_m'))
#     instance_offering = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond_offering)[0]
    # Create ECS VPC
    hyb_ops.sync_ecs_vpc_from_remote(datacenter_uuid)
    vpc_all = hyb_ops.query_ecs_vpc_local()
    ecs_vpc = [vpc for vpc in vpc_all if vpc.status.lower() == 'available']
    if ecs_vpc:
        vpc_inv = ecs_vpc[0]
    else:
        vpc_inv = hyb_ops.create_ecs_vpc_remote(datacenter_uuid, 'zstack-test-vpc', 'zstack-test-vpc-vrouter', '172.16.0.0/12')
    time.sleep(5)
    # Create ECS vSwitch
    hyb_ops.sync_ecs_vswitch_from_remote(datacenter_uuid)
    vswitch_all = hyb_ops.query_ecs_vswitch_local()
    vswitch = [vs for vs in vswitch_all if vs.ecsVpcUuid == vpc_inv.uuid and vs.status.lower() == 'available']
    if vswitch:
        vswitch_inv = vswitch[0]
    else:
        vpc_cidr_list = vpc_inv.cidrBlock.split('.')
        vpc_cidr_list[2] = '252'
        vpc_cidr_list[3] = '0/24'
        vswitch_cidr = '.'.join(vpc_cidr_list)
        vswitch_inv = hyb_ops.create_ecs_vswtich_remote(vpc_inv.uuid, iz_inv.uuid, 'zstack-test-vswitch', vswitch_cidr)
    # Create ECS Security Group
    hyb_ops.sync_ecs_security_group_from_remote(vpc_inv.uuid)
    time.sleep(5)
    sg_all = hyb_ops.query_ecs_security_group_local()
    ecs_security_group = [ sg for sg in sg_all if sg.ecsVpcUuid == vpc_inv.uuid and sg.name == 'zstack-test-ecs-security-group']
    if ecs_security_group:
        sg_inv = ecs_security_group[0]
    else:
        sg_inv = hyb_ops.create_ecs_security_group_remote('zstack-test-ecs-security-group', vpc_inv.uuid)
    hyb_ops.sync_ecs_security_group_rule_from_remote(sg_inv.uuid)
    time.sleep(5)
    cond_sg_rule = res_ops.gen_query_conditions('ecsSecurityGroupUuid', '=', sg_inv.uuid)
    sg_rule = hyb_ops.query_ecs_security_group_rule_local(cond_sg_rule)
    if not sg_rule:
        hyb_ops.create_ecs_security_group_rule_remote(sg_inv.uuid, 'ingress', 'ALL', '-1/-1', '0.0.0.0/0', 'accept', 'intranet', '10')
        hyb_ops.create_ecs_security_group_rule_remote(sg_inv.uuid, 'egress', 'ALL', '-1/-1', '0.0.0.0/0', 'accept', 'intranet', '10')
    # Get ECS Image
    hyb_ops.sync_ecs_image_from_remote(datacenter_uuid)
    hyb_ops.sync_ecs_image_from_remote(datacenter_uuid, image_type='system')
    cond_image_centos = res_ops.gen_query_conditions('platform', '=', 'CentOS')
    cond_image_self = cond_image_centos[:]
    cond_image_system = cond_image_centos[:]
    cond_image_self.extend(res_ops.gen_query_conditions('type', '=', 'self'))
    cond_image_system.extend(res_ops.gen_query_conditions('type', '=', 'system'))
    ecs_image_centos = hyb_ops.query_ecs_image_local(cond_image_centos)
    ecs_image_self = hyb_ops.query_ecs_image_local(cond_image_self)
    ecs_image_system = hyb_ops.query_ecs_image_local(cond_image_system)
    if not allocate_public_ip:
        image = ecs_image_self[-1] if ecs_image_self else ecs_image_centos[-1]
        ecs_inv = hyb_ops.create_ecs_instance_from_ecs_image('Password123', image.uuid, vswitch_inv.uuid, ecs_bandwidth=1, ecs_security_group_uuid=sg_inv.uuid, 
                                                             instance_type=ecs_instance_type[0].typeId, name='zstack-test-ecs-instance', ecs_console_password='A1B2c3')
    else:
        image = ecs_image_system[-1]
        ecs_inv = hyb_ops.create_ecs_instance_from_ecs_image('Password123', image.uuid, vswitch_inv.uuid, ecs_bandwidth=1, ecs_security_group_uuid=sg_inv.uuid, 
                                                             instance_type=ecs_instance_type[0].typeId, allocate_public_ip='true', name='zstack-test-ecs-instance', ecs_console_password='a1B2c3')
    time.sleep(10)
    return ecs_inv

def delete_ecs_instance(datacenter_inv, ecs_inv):
    hyb_ops.stop_ecs_instance(ecs_inv.uuid)
    for _ in xrange(600):
        hyb_ops.sync_ecs_instance_from_remote(datacenter_inv.uuid)
        ecs = [e for e in hyb_ops.query_ecs_instance_local() if e.ecsInstanceId == ecs_inv.ecsInstanceId][0]
        if ecs.ecsStatus.lower() == "stopped":
            break
        else:
            time.sleep(1)
    hyb_ops.del_ecs_instance(ecs.uuid)

def create_vlan_vm(l3_name=None, disk_offering_uuids=None, system_tags=None, session_uuid = None, instance_offering_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'vlan_vm', \
            disk_offering_uuids, system_tags=system_tags, \
            instance_offering_uuid = instance_offering_uuid,
            session_uuid = session_uuid)

# parameter: vmname; l3_net: l3_net_description, or [l3_net_uuid,]; image_uuid:
def create_vm(l3_uuid_list, image_uuid, vm_name = None, \
        disk_offering_uuids = None, default_l3_uuid = None, \
        system_tags = None, instance_offering_uuid = None, session_uuid = None, ps_uuid=None):
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    if not instance_offering_uuid:
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_session_uuid(session_uuid)
    vm_creation_option.set_ps_uuid(ps_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vr_vm(test_obj_dict, l3_name, session_uuid = None):
    '''
    '''
    vr_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr_l3_uuid)
    temp_vm = None
    if not vrs:
        #create temp_vm1 for getting vlan1's vr for test pf_vm portforwarding
        temp_vm = create_vlan_vm(l3_name, session_uuid = session_uuid)
        test_obj_dict.add_vm(temp_vm)
        vr = test_lib.lib_find_vr_by_vm(temp_vm.vm)[0]
        temp_vm.destroy(session_uuid)
        test_obj_dict.rm_vm(temp_vm)
    else:
        vr = vrs[0]
        if not test_lib.lib_is_vm_running(vr):
            test_lib.lib_robot_cleanup(test_obj_dict)
            test_util.test_skip('vr: %s is not running. Will skip test.' % vr.uuid)

    return vr

def create_vip(vip_name=None, l3_uuid=None, session_uuid = None):
    if not vip_name:
        vip_name = 'test vip'
    if not l3_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vip_creation_option = test_util.VipOption()
    vip_creation_option.set_name(vip_name)
    vip_creation_option.set_l3_uuid(l3_uuid)
    vip_creation_option.set_session_uuid(session_uuid)

    vip = zstack_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_creation_option)
    vip.create()

    return vip
