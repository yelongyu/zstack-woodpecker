'''

New Integration Test from a regress issue: after delete Host, delete Hosts' 
primary storage will fail and report can not find host ...

@author: Youyk
'''
import time
import os

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.primarystorage_operations as ps_ops

_config_ = {
        'timeout' : 300,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
host_config = test_util.HostOption()
host1_name = os.environ.get('hostName2')
ps_inv = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global host_config
    global ps_inv
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)

    host1 = res_ops.get_resource(res_ops.HOST, name = host1_name)[0]

    host_config.set_name(host1_name)
    host_config.set_cluster_uuid(host1.clusterUuid)
    host_config.set_management_ip(host1.managementIp)
    host_config.set_username(os.environ.get('hostUsername'))
    host_config.set_password(os.environ.get('hostPassword'))

    test_util.test_dsc('delete host')
    host_ops.delete_host(host1.uuid)

    test_util.test_dsc('delete primary storage')
    zone_name = os.environ.get('zoneName1')
    zone_uuid = res_ops.get_resource(res_ops.ZONE, name = zone_name)[0].uuid
    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid)
    ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0]
    if ps_inv.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
        ps_name1 = os.environ.get('nfsPrimaryStorageName1')
    elif ps_inv.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
        ps_name1 = os.environ.get('cephPrimaryStorageName1')

    ps_inv = res_ops.get_resource(res_ops.PRIMARY_STORAGE, name = ps_name)[0]
    ps_ops.delete_primary_storage(ps_inv.uuid)

    test_util.test_dsc("Recover Primary Storage")
    test_stub.recover_ps(ps_inv)
    test_util.test_dsc("Recover Host")
    host_ops.add_kvm_host(host_config)

    host1 = res_ops.get_resource(res_ops.HOST, name = host1_name)[0]
    ps1 = res_ops.get_resource(res_ops.PRIMARY_STORAGE, name = ps_name)[0]

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Delete Host and Primary Storage Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global host_config
    global ps_inv
    test_lib.lib_error_cleanup(test_obj_dict)
    host1 = res_ops.get_resource(res_ops.HOST, name = host1_name)
    if not host1:
        try:
            test_stub.recover_ps(ps_inv)
        except Exception as e:
            test_util.test_warn('Fail to recover all primary storage %s resource. It might impact later test case.' % ps_inv.name)
        try:
            host_ops.add_kvm_host(host_config)
        except Exception as e:
            test_util.test_warn('Fail to recover all [host:] %s resource. It will impact later test case.' % host1_name)
            raise e
