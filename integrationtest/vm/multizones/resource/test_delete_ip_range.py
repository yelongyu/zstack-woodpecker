'''

New Integration Test for testing deleting IP range.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header

import zstacklib.utils.ip as ip_header

import time
import os

_config_ = {
        'timeout' : 1200,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
ir_option = test_util.IpRangeOption()
ir1_name = os.environ.get('vlanIpRangeNameMulti1')

def test():
    global ir_option

    vm_creation_option = test_util.VmOption()
    l3_name = os.environ.get('l3VlanNetworkNameMultiRange')
    l3 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name)[0]
    vm_creation_option.set_l3_uuids([l3.uuid])

    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_delete_ip_range')

    ir1 = res_ops.get_resource(res_ops.IP_RANGE, name = ir1_name)[0]

    ir_option.set_name(ir1_name)
    ir_option.set_description(ir1.description)
    ir_option.set_netmask(ir1.netmask)
    ir_option.set_gateway(ir1.gateway)
    ir_option.set_l3_uuid(ir1.l3NetworkUuid)
    ir_option.set_startIp(ir1.startIp)
    ir_option.set_endIp(ir1.endIp)

    ir_start_ip = ip_header.IpAddress(ir1.startIp)
    ir_end_ip = ip_header.IpAddress(ir1.endIp)

    #test_util.test_dsc('create vms')
    #vm1 = test_lib.lib_create_vm(vm_creation_option)
    #test_obj_dict.add_vm(vm1)
    #vm1_ip = ip_header.IpAddress(vm1.get_vm().vmNics[0].ip)
    #test_util.test_logger('ip address: %s' % vm1_ip)

    #vm2 = test_lib.lib_create_vm(vm_creation_option)
    #test_obj_dict.add_vm(vm2)
    #vm2_ip = ip_header.IpAddress(vm2.get_vm().vmNics[0].ip)
    #test_util.test_logger('ip address: %s' % vm2_ip)

    #vm3 = test_lib.lib_create_vm(vm_creation_option)
    #test_obj_dict.add_vm(vm3)
    #vm3_ip = ip_header.IpAddress(vm3.get_vm().vmNics[0].ip)
    #test_util.test_logger('ip address: %s' % vm3_ip)

    #vm4 = test_lib.lib_create_vm(vm_creation_option)
    #test_obj_dict.add_vm(vm4)
    #vm4_ip = ip_header.IpAddress(vm4.get_vm().vmNics[0].ip)
    #test_util.test_logger('ip address: %s' % vm4_ip)

    test_util.test_dsc('create vm and make sure vm ip range is in ir1.')
    ip_range_flag = False
    try_times = 0
    while not ip_range_flag and try_times < 10:
        vm1 = test_lib.lib_create_vm(vm_creation_option)
        test_obj_dict.add_vm(vm1)
        vm1_ip = ip_header.IpAddress(vm1.get_vm().vmNics[0].ip)
        test_util.test_logger('ip address: %s' % vm1_ip)
        if vm1_ip <= ir_end_ip and vm1_ip >= ir_start_ip:
            ip_range_flag = True
            break
        vm1.destroy()
        test_obj_dict.rm_vm(vm1)
        try_times += 1

    if not ip_range_flag:
        test_util.test_fail('Can not deply IP address on [l3:] %s in [IP Range:] %s for %s times VMs creation. It might means the VM IP address allocation method has bug.' % (l3.uuid, ir1.uuid, try_times))

    test_util.test_dsc('delete ip range')
    net_ops.delete_ip_range(ir1.uuid)

    #vm1_flag = False
    #vm2_flag = False

    #if vm1_ip <= ir_end_ip and vm1_ip >= ir_start_ip:
    #    test_obj_dict.mv_vm(vm1, vm_header.RUNNING, vm_header.STOPPED)
    #    vm1.set_state(vm_header.STOPPED)
    #    vm1.update()
    #    vm1_flag = True

    #vm1.check()

    test_util.test_dsc('start vm with other ip range.')
    vm1.start()

    vm1_new_ip = ip_header.IpAddress(vm1.get_vm().vmNics[0].ip)
    if vm1_ip == vm1_new_ip:
        test_util.test_fail('VM still get origianl [IP:] %s , after delete the IP Range.' % vm1_ip)

    if vm1_new_ip <= ir_end_ip and vm1_new_ip >= ir_start_ip:
        test_util.test_fail('VM still get unexpected [IP:] %s , after delete the IP Range: [%s] ~ [%s].' % (vm1_ip, ir_start_ip, ir_end_ip))

    #The new start vm's IP address need to refresh (restart network srevice)
    vm1.check()

    net_ops.add_ip_range(ir_option)

    vm1.destroy()
    test_util.test_pass('Delete IP Range Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global ir_option
    test_lib.lib_error_cleanup(test_obj_dict)
    ir = res_ops.get_resource(res_ops.IP_RANGE, name = ir1_name)
    if not ir:
        try:
            net_ops.add_ip_range(ir_option)
        except Exception as e:
            test_util.test_warn('Fail to recover [ip range:] %s resource. It will impact later test case.' % ir1_name)
            raise e
