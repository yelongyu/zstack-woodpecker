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

CREATE_TEMPLATE_FROM_VOLUME_PATH = "/sharedmountpointprimarystorage/createtemplatefromvolume"
UPLOAD_BITS_TO_SFTP_BACKUPSTORAGE_PATH = "/sharedmountpointprimarystorage/sftp/upload"

_config_ = {
        'timeout' : 24*60*60+1200,
        'noparallel' : False,
        'noparallelkey': [ CREATE_TEMPLATE_FROM_VOLUME_PATH, UPLOAD_BITS_TO_SFTP_BACKUPSTORAGE_PATH ]
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
agent_url = None
vm = None
image = None

case_flavor = dict(create_tempate_default=                    dict(agent_url=CREATE_TEMPLATE_FROM_VOLUME_PATH, agent_time=(24*60*60-60)*1000),
                   upload_to_sftp_default=                    dict(agent_url=UPLOAD_BITS_TO_SFTP_BACKUPSTORAGE_PATH, agent_time=(24*60*60-60)*1000),
                   create_tempate_default_default_6min=       dict(agent_url=CREATE_TEMPLATE_FROM_VOLUME_PATH, agent_time=360*1000),
                   upload_to_sftp_default_6min=               dict(agent_url=UPLOAD_BITS_TO_SFTP_BACKUPSTORAGE_PATH, agent_time=360*1000),
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
    local_pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    if len(local_pss) == 0:
        test_util.test_skip('Required smp ps to test')
    ps_uuid = local_pss[0].uuid
    vm = test_stub.create_vm(image_uuid=image_uuid, ps_uuid=ps_uuid)

    agent_url = flavor['agent_url']
    agent_time = flavor['agent_time']
    script = '{entity -> sleep(%s)}' % (agent_time)
    dep_ops.remove_simulator_agent_script(agent_url)
    dep_ops.deploy_simulator_agent_script(agent_url, script)
    image_creation_option = test_util.ImageOption()
    bss = res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE, [])
    if len(bss) == 0:
        test_util.test_skip('Required sftp bs to test')
    bs_uuid = bss[0].uuid

    image_creation_option.set_backup_storage_uuid_list([bs_uuid])
    image_creation_option.set_root_volume_uuid(vm.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_root_volume_template_timeout')
    image_creation_option.set_timeout(24*60*60*1000)

    image = zstack_image_header.ZstackTestImage()
    image.set_creation_option(image_creation_option)
    image.create()


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
