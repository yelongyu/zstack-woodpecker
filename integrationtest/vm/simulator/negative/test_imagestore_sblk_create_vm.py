'''

Test Exception handling for Create VM

@author: Quarkonics
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
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

DOWNLOAD_IMAGE = "/sharedblock/imagestore/download"
CREATE_VOLUME = "/sharedblock/createrootvolume"
ACTIVE_VOLUME = "/sharedblock/volume/active"
FLAT_DHCP_PREPARE = "/flatnetworkprovider/dhcp/prepare"
FLAT_DHCP_APPLY = "/flatnetworkprovider/dhcp/apply"
VM_START = "/vm/start"
FLAT_DHCP_RELEASE = "/flatnetworkprovider/dhcp/release"
SBLK_DELETE = "/sharedblock/bits/delete"

_config_ = {
        'timeout' : 120,
        'noparallel' : True,
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
agent_url = None
agent_url2 = None
vm = None

case_flavor = dict(normal=             dict(agent_url=None),
                   download_image=     dict(agent_url=DOWNLOAD_IMAGE),
                   create_volume=      dict(agent_url=CREATE_VOLUME),
                   active_volume=      dict(agent_url=ACTIVE_VOLUME),
                   dhcp_prepare=       dict(agent_url=FLAT_DHCP_PREPARE),
                   dhcp_apply=         dict(agent_url=FLAT_DHCP_APPLY),
                   vm_start=           dict(agent_url=VM_START),
                   dhcp_release=       dict(agent_url=FLAT_DHCP_RELEASE),
                   sblk_delete=        dict(agent_url=SBLK_DELETE),
                   )

db_tables_white_list = ['VmInstanceSequenceNumberVO', 'TaskProgressVO', 'RootVolumeUsageVO', 'ImageCacheVO', 'SystemTagVO', 'VtepVO', 'ResourceVO']

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

    if agent_url == FLAT_DHCP_RELEASE or agent_url == SBLK_DELETE:
        agent_url2 = CREATE_VOLUME
        deploy_operations.remove_simulator_agent_script(agent_url2)
        deploy_operations.deploy_simulator_agent_script(agent_url2, script)

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
    cond = res_ops.gen_query_conditions('type', '=', 'SharedBlock')
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    if len(pss) == 0:
        test_util.test_skip('Required smp ps to test')
    ps_uuid = pss[0].uuid

    saved_db_stats = test_stub.get_db_stats(dhcp_ip)
    create_vm_failure = False
    try:
        vm = test_stub.create_vm(image_uuid=image_uuid, ps_uuid=ps_uuid)
    except:
        create_vm_failure = True

    if agent_url != None and not create_vm_failure:
        test_util.test_fail("Expect failure during creating VM while it passed. Test Exception handling for Create VM FAIL")

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
