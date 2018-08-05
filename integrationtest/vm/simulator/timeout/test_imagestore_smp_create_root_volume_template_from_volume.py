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
import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import threading
import uuid
import os
import time
import simplejson
import zstackwoodpecker.operations.deploy_operations as dep_ops

KVM_TAKE_VOLUME_SNAPSHOT_PATH = "/vm/volume/takesnapshot"
COMMIT_BITS_TO_IMAGESTORE_PATH = "/sharedmountpointprimarystorage/imagestore/commit"
UPLOAD_BITS_TO_IMAGESTORE_PATH = "/sharedmountpointprimarystorage/imagestore/upload"

_config_ = {
        'timeout' : 24*60*60+1200,
        'noparallel' : False,
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
agent_url = None
vm = None
image = None

case_flavor = dict(take_volume_snapshot_default=       dict(agent_url=KVM_TAKE_VOLUME_SNAPSHOT_PATH, agent_action=1),
                   commit_to_imagestore_default=       dict(agent_url=COMMIT_BITS_TO_IMAGESTORE_PATH, agent_action=1),
                   upload_to_imagestore_default=       dict(agent_url=UPLOAD_BITS_TO_IMAGESTORE_PATH, agent_action=1),
                   take_volume_snapshot_default_6min=  dict(agent_url=KVM_TAKE_VOLUME_SNAPSHOT_PATH, agent_action=2),
                   commit_to_imagestore_default_6min=  dict(agent_url=COMMIT_BITS_TO_IMAGESTORE_PATH, agent_action=2),
                   upload_to_imagestore_default_6min=  dict(agent_url=UPLOAD_BITS_TO_IMAGESTORE_PATH, agent_action=2),
                   )

def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    global agent_url
    global vm
    global image
    imagestore = test_lib.lib_get_image_store_backup_storage()
    if imagestore == None:
        test_util.test_skip('Required imagestore to test')
    image_uuid = test_stub.get_image_by_bs(imagestore.uuid)
    cond = res_ops.gen_query_conditions('type', '=', 'SharedMountPoint')
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    if len(pss) == 0:
        test_util.test_skip('Required smp ps to test')
    ps_uuid = pss[0].uuid
    vm = test_stub.create_vm(image_uuid=image_uuid, ps_uuid=ps_uuid)

    agent_url = flavor['agent_url']
    agent_action = flavor['agent_action']
    if agent_action == 1:
        agent_time = (24*60*60-60)*1000
    elif agent_action == 2:
        agent_time = 360 * 1000

    image_uuid = str(uuid.uuid4()).replace('-', '')
    if agent_url == KVM_TAKE_VOLUME_SNAPSHOT_PATH:
        rsp = dep_ops.json_post("http://127.0.0.1:8888/test/api/v1.0/store/create", simplejson.dumps({"key": vm.get_vm().rootVolumeUuid, "value": '{"%s":%s}' % (agent_url, agent_action)}))
    else:
        rsp = dep_ops.json_post("http://127.0.0.1:8888/test/api/v1.0/store/create", simplejson.dumps({"key": image_uuid, "value": '{"%s":%s}' % (agent_url, agent_action)}))

    image_creation_option = test_util.ImageOption()
    image_creation_option.set_uuid(image_uuid)
    image_creation_option.set_backup_storage_uuid_list([imagestore.uuid])
    image_creation_option.set_root_volume_uuid(vm.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_root_volume_template_timeout')
    image_creation_option.set_timeout(24*60*60*1000)

    image = zstack_image_header.ZstackTestImage()
    image.set_creation_option(image_creation_option)
    start = time.time()
    image.create()
    end = time.time()
    if end - start < agent_time / 2 / 1000:
        test_util.test_fail('execution time too short %s' % (end - start))


def env_recover():
    global agent_url
    dep_ops.remove_simulator_agent_script(agent_url)
    global vm
    if vm != None:
        vm.destroy()
        vm.expunge()
    global image
    if image != None:
        image.delete()
        image.expunge()
