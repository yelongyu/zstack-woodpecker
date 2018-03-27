'''
Test create volume from sftp backupstorage template and attach it to vm with vm'status on/off and detach it

@author ronghao.Zhou
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import apibinding.inventory as inventory

import zstackwoodpecker.operations.resource_operations as res_ops
import os

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()


def test():

    test_lib.skip_test_when_bs_type_not_in_list([inventory.SFTP_BACKUP_STORAGE_TYPE])

    global test_obj_dict
    image_name = os.environ.get('imageName_s')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm_name='multihost_basic_vm'
    vm = test_stub.create_vm(vm_name,image_name,l3_name)
    test_obj_dict.add_vm(vm)

    volume = test_stub.create_volume()
    test_obj_dict.add_volume(volume)
    volume.attach(vm)

    bss = res_ops.query_resource_fields(res_ops.SFTP_BACKUP_STORAGE, fields=["uuid"])
    sftp_uuid_list = []
    for bs in bss:
        sftp_uuid_list.append(bs.uuid)
    volume_template = volume.create_template(sftp_uuid_list)
    test_obj_dict.add_image(volume_template)


    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]
    ps_uuid = ps.uuid
    host_uuid=None
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        host_uuid=test_lib.lib_get_local_storage_volume_host(volume.get_volume().uuid).uuid

    new_volume_01 = volume_template.create_data_volume(ps_uuid,"new volume 01",host_uuid)
    test_obj_dict.add_volume(new_volume_01)
    new_volume_02 = volume_template.create_data_volume(ps_uuid,"new volume 02",host_uuid)
    test_obj_dict.add_volume(new_volume_02)

    volume.detach()

    # test volume attach to vm with vm on
    new_volume_01.attach(vm)
    new_volume_01.detach()

    # test volume attach to vm with vm off
    vm.stop()
    new_volume_02.attach(vm)
    vm.start()
    new_volume_02.detach()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create volume from volume template in sftp bs and attach it to vm success')

# Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
