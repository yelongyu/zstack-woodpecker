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
import json
import simplejson
import zstackwoodpecker.operations.deploy_operations as dep_ops

IMAGESTORE_IMPORT = "/imagestore/import/"

_config_ = {
        'timeout' : 24*60*60+1200,
        'noparallel' : False,
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
agent_url = None
image = None

case_flavor = dict(import_default=         dict(agent_url=IMAGESTORE_IMPORT, agent_action=1),
                   import_default_6min=    dict(agent_url=IMAGESTORE_IMPORT, agent_action=2),
                   )

def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    global agent_url
    global image

    agent_url = flavor['agent_url']
    agent_action = flavor['agent_action']
    if agent_action == 1:
        agent_time = (24*60*60-60)*1000
    elif agent_action == 2:
        agent_time = 360 * 1000

    image_uuid = str(uuid.uuid4()).replace('-', '')
    rsp = dep_ops.json_post("http://127.0.0.1:8888/test/api/v1.0/store/create", simplejson.dumps({"key": image_uuid, "value": '{"%s":%s}' % (agent_url, agent_action)}))
    image_creation_option = test_util.ImageOption()
    imagestore = test_lib.lib_get_image_store_backup_storage()
    if imagestore == None:
        test_util.test_skip('Required imagestore to test')
    bs_uuid = imagestore.uuid

    image_option = test_util.ImageOption()
    image_option.set_uuid(image_uuid)
    image_option.set_name('fake_image')
    image_option.set_description('fake image')
    image_option.set_format('raw')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_backup_storage_uuid_list([bs_uuid])
    image_option.url = "http://fake/fake.raw"
    image_option.set_timeout(24*60*60*1000)

    start = time.time()
    image = img_ops.add_image(image_option)
    end = time.time()
    if end - start < agent_time / 2 / 1000:
        test_util.test_fail('execution time too short %s' % (end - start))

def env_recover():
    global image
    if image != None:
        image.delete()
        image.expunge()
