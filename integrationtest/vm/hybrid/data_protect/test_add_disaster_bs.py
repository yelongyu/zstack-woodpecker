'''

New Integration Test for add disaster backup storage.

@author: Glody 
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
disaster_bs_uuid = None

def test():
    global disaster_bs_uuid
    disaster_bs_dict = bs_ops.get_disaster_backup_storage_info(test_lib.deploy_config)
    name = disaster_bs_dict.name
    description = disaster_bs_dict.description
    hostname = disaster_bs_dict.hostname
    url = disaster_bs_dict.url
    username = disaster_bs_dict.username
    password = disaster_bs_dict.password
    sshport = disaster_bs_dict.port
    #AddDisasterImageStoreBackupStorage 
    disaster_backup_storage = bs_ops.add_disaster_image_store_bs(url, hostname, username, password, sshport, name, description)
    disaster_bs_uuid = disaster_backup_storage.uuid
    #AttachBackupStorageToZone
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    bs_ops.attach_backup_storage(disaster_bs_uuid, zone_uuid)
    #Check if the bs has 'remote' system tag
    cond = res_ops.gen_query_conditions('resourceUuid', '=', disaster_bs_uuid)
    system_tag =  res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0]
    if system_tag.tag != "remote":
        test_util.test_fail("Here isn't 'remote' system tag for disaster bs")
     
    bs_ops.delete_backup_storage(disaster_bs_uuid) 
    test_util.test_pass('Setup data protect bs image store success, the uuid is %s' %disaster_bs_uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global disaster_bs_uuid
    if disaster_bs_uuid != None:
        bs_ops.delete_backup_storage(disaster_bs_uuid)
