'''

Integration Test for creating KVM VM with all nodes shutdown and recovered.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

vm = None

def test():
    global vm
    cmd = "init 0"
    host_username = os.environ.get('nodeUserName')
    host_password = os.environ.get('nodePassword')
    zstack_ha_vip = os.environ.get('zstackHaVip')
    node1_ip = os.environ.get('node1Ip')
    test_util.test_logger("shutdown node: %s" % (node1_ip))
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    node2_ip = os.environ.get('node2Ip')
    test_util.test_logger("shutdown node: %s" % (node2_ip))
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)

    test_util.test_logger("recover node: %s" % (node1_ip))
    os.system('bash -ex %s %s' % (os.environ.get('nodeRecoverScript'), node1_ip))
    test_util.test_logger("recover node: %s" % (node2_ip))
    os.system('bash -ex %s %s' % (os.environ.get('nodeRecoverScript'), node2_ip))

    cmd = "service mysql bootstrap"
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    cmd = "service mysql restart"
    rsp = test_lib.lib_execute_ssh_cmd(node2_ip, host_username, host_password, cmd, 180)
    cmd = "service mysql start"
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)
    cmd = "zstack-ctl install_ha --host1-info %s:%s@%s --host2-info %s:%s@%s --vip %s --recovery-from-this-host" % \
            (host_username, host_password, node1_ip, host_username, host_password, node2_ip, zstack_ha_vip)
    rsp = test_lib.lib_execute_ssh_cmd(node1_ip, host_username, host_password, cmd, 180)

    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('ha_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)

    vm.create()
    #time.sleep(5)
    vm.check()
    vm.destroy()

    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
