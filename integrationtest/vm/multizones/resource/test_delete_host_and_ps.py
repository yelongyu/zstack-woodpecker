'''

New Integration Test from a regress issue: after delete Host, delete Hosts' 
primary storage will fail and report can not find host ...

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
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import time
import os

_config_ = {
        'timeout' : 300,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
host_config = test_util.HostOption()
host1_name = os.environ.get('hostName2')
ps_inv = None

def recover_ps():
    global ps_inv
    ps_config = test_util.PrimaryStorageOption()

    ps_config.set_name(ps_inv.name)
    ps_config.set_description(ps_inv.description)
    ps_config.set_zone_uuid(ps_inv.zoneUuid)
    ps_config.set_type(ps_inv.type)
    ps_config.set_url(ps_inv.url)

    #avoid of ps is already created successfully. 
    cond = res_ops.gen_query_conditions('zoneUuid', '=', ps_inv.zoneUuid)
    cond = res_ops.gen_query_conditions('url', '=', ps_inv.url, cond)
    curr_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    if curr_ps:
        ps = curr_ps[0]
    else:
        ps = ps_ops.create_nfs_primary_storage(ps_config)

    for cluster_uuid in ps_inv.attachedClusterUuids:
        ps_ops.attach_primary_storage(ps.uuid, cluster_uuid)

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
    ps_name = os.environ.get('nfsPrimaryStorageName1')
    ps_inv = res_ops.get_resource(res_ops.PRIMARY_STORAGE, name = ps_name)[0]
    ps_ops.delete_primary_storage(ps_inv.uuid)

    test_util.test_dsc("Recover Primary Storage")
    recover_ps()
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
            recover_ps()
        except Exception as e:
            test_util.test_warn('Fail to recover all primary storage %s resource. It might impact later test case.' % ps_inv.name)
        try:
            host_ops.add_kvm_host(host_config)
        except Exception as e:
            test_util.test_warn('Fail to recover all [host:] %s resource. It will impact later test case.' % host1_name)
            raise e
