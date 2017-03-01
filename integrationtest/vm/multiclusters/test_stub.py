'''

Create an unified test_stub to share test operations

@author: Quarkonics
'''
import os
import random
import zstackwoodpecker.test_util  as test_util
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.host as host_header
import threading
import time
import sys
#import traceback


def create_vm(vm_name, image_name, l3_name):
    vm_creation_option = test_util.VmOption()
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def migrate_vm_to_differnt_cluster(vm):
    test_util.test_dsc("migrate vm to different cluster")
    if not test_lib.lib_check_vm_live_migration_cap(vm.vm):
        test_util.test_skip('skip migrate if live migrate not supported')

    current_host = test_lib.lib_find_host_by_vm(vm.vm)
    conditions = res_ops.gen_query_conditions('clusterUuid', '!=', current_host.clusterUuid)
    candidate_hosts = res_ops.query_resource(res_ops.HOST, conditions, None)
    if len(candidate_hosts) == 0:
        test_util.test_fail('Not find available Hosts to do migration')

    vm.migrate(candidate_hosts[0].uuid)
