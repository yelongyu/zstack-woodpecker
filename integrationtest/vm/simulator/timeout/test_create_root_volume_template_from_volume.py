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

CREATE_TEMPLATE_FROM_VOLUME_PATH = "/nfsprimarystorage/sftp/createtemplatefromvolume"
UPLOAD_TO_SFTP_PATH = "/nfsprimarystorage/uploadtosftpbackupstorage"

_config_ = {
        'timeout' : 12000,
        'noparallel' : False,
        'noparallelkey': [ CREATE_TEMPLATE_FROM_VOLUME_PATH, UPLOAD_TO_SFTP_PATH ]
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None
image = None

def test():
    global vm
    global image
    vm = test_stub.create_vm()

    script = '{entity -> sleep(3000)}'
    dep_ops.deploy_simulator_agent_script(CREATE_TEMPLATE_FROM_VOLUME_PATH, script)
    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
    image_creation_option.set_root_volume_uuid(vm.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_root_volume_template_timeout')
    bs_type = backup_storage_list[0].type

    image = zstack_image_header.ZstackTestImage()
    image.set_creation_option(image_creation_option)
    image.create()


def env_recover():
    dep_ops.remove_simulator_agent_script(CREATE_TEMPLATE_FROM_VOLUME_PATH)
    global vm
    if vm != None:
        vm.destroy()
        vm.expunge()
    global image
    if image != None:
        image.delete()
        image.expunge()
