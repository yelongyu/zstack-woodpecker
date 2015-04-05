'''

New Integration Test for testing deleting zone

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.zone_operations as zone_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

_config_ = {
        'timeout' : 1200,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
curr_deploy_conf = None
zone1_name = os.environ.get('zoneName1')

def test():
    #This conf should only be put in test(), since test_lib.deploy_config 
    # should be set by woodpecker. 
    global curr_deploy_conf
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #pick up zone1
    zone1 = res_ops.get_resource(res_ops.ZONE, name = zone1_name)[0]

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_basic_vm')
    vm_creation_option.set_zone_uuid(zone1.uuid)
    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)

    vm3 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm3)

    vm4 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm4)

    zone_ops.delete_zone(zone1.uuid)
    test_obj_dict.mv_vm(vm1, vm_header.RUNNING, vm_header.DESTROYED)
    test_obj_dict.mv_vm(vm2, vm_header.RUNNING, vm_header.DESTROYED)
    test_obj_dict.mv_vm(vm3, vm_header.RUNNING, vm_header.DESTROYED)
    test_obj_dict.mv_vm(vm4, vm_header.RUNNING, vm_header.DESTROYED)
    vm1.update()
    vm2.update()
    vm3.update()
    vm4.update()

    test_lib.lib_robot_status_check(test_obj_dict)
    zone_ops.add_zone_resource(curr_deploy_conf, zone1_name)

    zone1 = res_ops.get_resource(res_ops.ZONE, name = zone1_name)[0]
    vm_creation_option.set_zone_uuid(zone1.uuid)
    vm_creation_option.set_l3_uuids([])
    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)

    vm3 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm3)

    vm4 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm4)

    test_lib.lib_robot_status_check(test_obj_dict)
    #time.sleep(5)
    #vm.check()
    #vm.destroy()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Delete Zone Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global curr_deploy_conf
    zone1 = res_ops.get_resource(res_ops.ZONE, name = zone1_name)
    if not zone1:
        try:
            zone_ops.add_zone_resource(curr_deploy_conf, zone1_name)
        except Exception as e:
            test_util.test_warn('Fail to recover all [zone:] %s resource. It will impact later test case.' % zone1_name)
            raise e

    test_lib.lib_error_cleanup(test_obj_dict)
