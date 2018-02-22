'''

All vcenter operations for test.

@author: SyZhao
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.resource_operations as res_ops



def add_vcenter(name, domain_name, username, password, https, zone_uuid, timeout=240000, session_uuid=None):
    action = api_actions.AddVCenterAction()
    action.name = name
    action.domainName = domain_name
    action.username = username
    action.password = password
    action.https = https
    action.zoneUuid = zone_uuid
    action.timeout = timeout
    test_util.action_logger('Add VCenter')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory


def delete_vcenter(vcenter_uuid, timeout=240000, session_uuid=None):
    action = api_actions.DeleteVCenterAction()
    action.uuid = vcenter_uuid
    action.timeout = timeout
    test_util.action_logger('Delete VCenter [uuid:] %s' % vcenter_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def lib_get_vcenter_primary_storage_by_name(ps_name):
    cond = res_ops.gen_query_conditions("name", '=', ps_name)
    vcps_inv = res_ops.query_resource(res_ops.VCENTER_PRIMARY_STORAGE, cond)
    if vcps_inv:
        return vcps_inv[0]
    
def lib_get_vcenter_backup_storage_by_name(bs_name):
    cond = res_ops.gen_query_conditions("name", '=', bs_name)
    vcbs_inv = res_ops.query_resource(res_ops.VCENTER_BACKUP_STORAGE, cond)
    if vcbs_inv:
        return vcbs_inv[0]

def lib_get_vcenter_cluster_by_name(cl_name):
    cond = res_ops.gen_query_conditions("name", '=', cl_name)
    cluster_inv = res_ops.query_resource(res_ops.VCENTER_CLUSTER, cond)
    if cluster_inv:
        return cluster_inv[0]


