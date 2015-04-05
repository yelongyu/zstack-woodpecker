'''

New Integration Test for testing deleting Host, when there is already a stopped
vm

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

#This case can not be parallel, since it will delete host, which will impact
# other test case
_config_ = {
        'timeout' : 1800,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
host_config = test_util.HostOption()
host1_name = os.environ.get('hostName')

def test():
    global host_config
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #pick up host1
    host1 = res_ops.get_resource(res_ops.HOST, name = host1_name)[0]

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_basic_vm')
    vm_creation_option.set_host_uuid(host1.uuid)
    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    vm1.stop()

    host_config.set_name(host1_name)
    host_config.set_cluster_uuid(host1.clusterUuid)
    host_config.set_management_ip(host1.managementIp)
    host_config.set_username(os.environ.get('hostUsername'))
    host_config.set_password(os.environ.get('hostPassword'))

    test_util.test_dsc('delete host')
    host_ops.delete_host(host1.uuid)
    test_obj_dict.mv_vm(vm1, vm_header.RUNNING, vm_header.STOPPED)
    vm1.update()
    vm1.check()

    host_ops.add_kvm_host(host_config)
    test_util.test_dsc('start vm on host, after readd it.')
    vm1.start()
    vm1.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Delete Host Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global host_config
    test_lib.lib_error_cleanup(test_obj_dict)
    host1 = res_ops.get_resource(res_ops.HOST, name = host1_name)
    if not host1:
        try:
            host_ops.add_kvm_host(host_config)
        except Exception as e:
            test_util.test_warn('Fail to recover all [host:] %s resource. It will impact later test case.' % host1_name)
            raise e
