'''

New Test For Operations Timeout

@author: Quarkonics
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops 
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.console_operations as console_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.config_operations as config_ops
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_snapshot_header
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.header.vm as vm_header
import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import threading
import uuid
import os
import time
import json
import simplejson
import zstackwoodpecker.operations.deploy_operations as dep_ops

KVM_MIGRATE_VM_PATH = "/vm/migrate"

_config_ = {
        'timeout' : 24*60*60+1200,
        'noparallel' : True,
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
agent_url = None
vm = None


def test():
    global agent_url
    global vm
    imagestore = test_lib.lib_get_image_store_backup_storage()
    if imagestore == None:
        test_util.test_skip('Required imagestore to test')
    image_uuid = test_stub.get_image_by_bs(imagestore.uuid)
    cond = res_ops.gen_query_conditions('type', '=', 'SharedMountPoint')
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)

    if len(pss) == 0:
        test_util.test_skip('Required %s ps to test' % (ps_type))
    ps_uuid = pss[0].uuid
    vm = test_stub.create_vm(image_uuid=image_uuid, ps_uuid=ps_uuid)
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid,'NeverStop')

    agent_url = KVM_MIGRATE_VM_PATH
    script = '''
{ entity -> 
        throw new Exception(\"shuang\")
}
'''
    deploy_operations.remove_simulator_agent_script(agent_url)
    deploy_operations.deploy_simulator_agent_script(agent_url, script)

    candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm.get_vm().uuid)
    start = time.time()
    no_exception = True
    if candidate_hosts != None and test_lib.lib_check_vm_live_migration_cap(vm.get_vm()):
        try:
            vm_ops.migrate_vm(vm.get_vm().uuid, candidate_hosts.inventories[0].uuid)
            no_exception = True
        except:
            test_util.test_logger('Expected exception for VM migration')
            no_exception = False
    else:
        test_util.test_skip('Required migratable host to test')
    if no_exception:
        test_util.test_fail('Expect exception for migration while there is none')
    vm.stop()
    cond = res_ops.gen_query_conditions('uuid', '=', vm.get_vm().uuid)
    for i in range(5):
        time.sleep(1)
        try:
            if res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0].state == vm_header.RUNNING:
                break
        except:
            test_util.test_logger('Retry until VM change to running')

    if res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0].state == vm_header.RUNNING:
        test_util.test_pass('HA after migrate failure test pass')
    
    test_util.test_fail('HA after migrate failure test fail')

def env_recover():
    global agent_url
    deploy_operations.remove_simulator_agent_script(agent_url)
    global vm
    if vm != None:
        vm.destroy()
        vm.expunge()
