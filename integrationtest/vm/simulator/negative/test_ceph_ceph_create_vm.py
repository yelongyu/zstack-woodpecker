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
import uuid
import os
import time
import MySQLdb

CHECK_BITS = "/ceph/primarystorage/snapshot/checkbits"
VOLUME_CLONE = "/ceph/primarystorage/volume/clone"
FLAT_DHCP_PREPARE = "/flatnetworkprovider/dhcp/prepare"
FLAT_DHCP_APPLY = "/flatnetworkprovider/dhcp/apply"
VM_START = "/vm/start"
FLAT_DHCP_RELEASE = "/flatnetworkprovider/dhcp/release"
NFS_DELETE = "/nfsprimarystorage/delete"

_config_ = {
        'timeout' : 60,
        'noparallel' : True,
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
agent_url = None
agent_url2 = None
vm = None

case_flavor = dict(normal=             dict(agent_url=None),
                   check_bits=         dict(agent_url=CHECK_BITS),
                   volume_clone=       dict(agent_url=VOLUME_CLONE),
                   dhcp_prepare=       dict(agent_url=FLAT_DHCP_PREPARE),
                   dhcp_apply=         dict(agent_url=FLAT_DHCP_APPLY),
                   vm_start=           dict(agent_url=VM_START),
                   dhcp_release=       dict(agent_url=FLAT_DHCP_RELEASE),
                   nfs_delete=         dict(agent_url=NFS_DELETE),
                   )

db_tables_white_list = ['VmInstanceSequenceNumberVO', 'TaskProgressVO', 'RootVolumeUsageVO', 'ImageCacheVO']
def get_db_stats():
    conn = MySQLdb.connect(host=os.getenv('DBServer'), user='root', passwd='zstack.mysql.password', db='zstack',port=3306)
    cur = conn.cursor()
    count = cur.execute('show tables;')
    all_tables = cur.fetchall()
    db_tables_stats = dict()
    for at in all_tables:
        if at[0].find('VO') >= 0:
        	count = cur.execute('select count(*) from %s;' % (at[0]))
        	db_tables_stats[at[0]] = cur.fetchone()[0]
        else:
                count = cur.execute('checksum table %s;' % (at[0]))
        	db_tables_stats[at[0]] = cur.fetchone()[1]
    return db_tables_stats

def test():
    global agent_url
    global agent_url2
    global vm
    saved_db_stats = get_db_stats()
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]

    agent_url = flavor['agent_url']
    script = '''
{ entity -> 
	throw new Exception("shuang")
}
'''
    deploy_operations.remove_all_simulator_agent_script()
    if agent_url != None:
        deploy_operations.deploy_simulator_agent_script(agent_url, script)

    if agent_url == FLAT_DHCP_RELEASE or agent_url == NFS_DELETE:
        agent_url2 = VOLUME_CLONE
        deploy_operations.deploy_simulator_agent_script(agent_url2, script)

    imagestore = test_lib.lib_get_image_store_backup_storage()
    if imagestore == None:
        test_util.test_skip('Required imagestore to test')
    image_uuid = test_stub.get_image_by_bs(imagestore.uuid)
    ceph_pss = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE, [])
    if len(ceph_pss) == 0:
        test_util.test_skip('Required ceph ps to test')
    ps_uuid = ceph_pss[0].uuid
    create_vm_failure = False
    try:
        vm = test_stub.create_vm(image_uuid=image_uuid, ps_uuid=ps_uuid)
    except:
        create_vm_failure = True

    if agent_url != None and not create_vm_failure:
        test_util.test_fail("Expect failure during creating VM while it passed. Test Exception handling for Create VM FAIL")

    if agent_url != None:
        saved_db_stats2 = get_db_stats()
        for key in saved_db_stats2:
            if saved_db_stats2[key] != saved_db_stats[key] and key not in db_tables_white_list:
                test_util.test_fail("DB Table %s changed %s -> %s" % (key, saved_db_stats[key], saved_db_stats2[key]))

def env_recover():
    global vm
    if vm != None:
        vm.destroy()
        vm.expunge()

    deploy_operations.remove_all_simulator_agent_script()
