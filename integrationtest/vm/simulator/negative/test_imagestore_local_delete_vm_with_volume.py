'''

Test Exception handling for Create VM

@author: Quarkonics
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_snapshot_header
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.net_operations as net_ops
import uuid
import os
import time
import MySQLdb

VM_DESTROY = "/vm/destroy"

_config_ = {
        'timeout' : 720,
        'noparallel' : True,
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
agent_url = None
agent_url2 = None
vm = None

case_flavor = dict(normal=             dict(agent_url=None),
                   vm_destroy=         dict(agent_url=VM_DESTROY),
                   )

db_tables_white_list = ['VmInstanceSequenceNumberVO', 'TaskProgressVO', 'RootVolumeUsageVO', 'ImageCacheVO', 'SystemTagVO', 'UsedIpVO', 'SecurityGroupFailureHostVO', 'VmUsageVO']

def test():
    global agent_url
    global agent_url2
    global vm
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]

    agent_url = flavor['agent_url']
    script = '''
{ entity -> 
	throw new Exception("shuang")
}
'''
    if agent_url != None:
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)

    l3net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetworkName3')).uuid
    is_flat = test_lib.lib_get_flat_dhcp_by_l3_uuid(l3net_uuid)
    if is_flat:
        try:
            dhcp_ip = net_ops.get_l3network_dhcp_ip(l3net_uuid)
        except:
            dhcp_ip = None
    else:
        dhcp_ip = None

    imagestore = test_lib.lib_get_image_store_backup_storage()
    if imagestore == None:
        test_util.test_skip('Required imagestore to test')
    image_uuid = test_stub.get_image_by_bs(imagestore.uuid)
    cond = res_ops.gen_query_conditions('type', '=', 'LocalStorage')
    local_pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    if len(local_pss) == 0:
        test_util.test_skip('Required ceph ps to test')
    ps_uuid = local_pss[0].uuid
    image_creation_option = test_util.ImageOption()
    imagestore = test_lib.lib_get_image_store_backup_storage()
    bs_uuid = imagestore.uuid
    vm = test_stub.create_vm(image_uuid=image_uuid, ps_uuid=ps_uuid)
    saved_db_stats = test_stub.get_db_stats(dhcp_ip)
    old_ip_count = test_stub.get_table_stats('UsedIpVO')

    vm.destroy()
    new_ip_count = test_stub.get_table_stats('UsedIpVO')

    if agent_url != None:
        if is_flat:
            try:
                dhcp_ip = net_ops.get_l3network_dhcp_ip(l3net_uuid)
            except:
                dhcp_ip = None
        else:
            dhcp_ip = None

        saved_db_stats2 = test_stub.get_db_stats(dhcp_ip)
        test_stub.compare_db_stats(saved_db_stats, saved_db_stats2, db_tables_white_list)
        if int(new_ip_count) != int(old_ip_count)-1:
            test_util.test_fail("UsedIpVO is expected to -1, %s -> %s" % (old_ip_count, new_ip_count))

def env_recover():
    global agent_url
    global agent_url2
    global vm
    if vm != None:
        vm.destroy()
        vm.expunge()

    if agent_url != None:
        deploy_operations.remove_simulator_agent_script(agent_url)
    if agent_url2 != None:
        deploy_operations.remove_simulator_agent_script(agent_url2)

