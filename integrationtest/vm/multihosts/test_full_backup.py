import os
import time
import random
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.header.host as host_header
import zstackwoodpecker.header.volume as volume_header


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

Path = [[]]
index = 0
tag = "VM_TEST_REBOOT"
backup = []
backup_list = []
dvol = None

#case_flavor = dict(snapshot_running=                dict(vm_op=['VM_TEST_SNAPSHOT'], state_op=['VM_TEST_NONE']),
#                   create_img_running=              dict(vm_op=['VM_TEST_CREATE_IMG'], state_op=['VM_TEST_NONE']),
#                   resize_running=                  dict(vm_op=['VM_TEST_RESIZE_RVOL'], state_op=['VM_TEST_NONE']),
#                   del_snapshot_running=            dict(vm_op=['RVOL_DEL_SNAPSHOT'], state_op=['VM_TEST_NONE']),
#                   create_img_from_backup_running=  dict(vm_op=['VM_TEST_BACKUP_IMAGE'], state_op=['VM_TEST_NONE']),
#                   migrate_running=                 dict(vm_op=['VM_TEST_MIGRATE'], state_op=['VM_TEST_NONE']),
#                   snapshot_stopped=                dict(vm_op=['VM_TEST_SNAPSHOT'], state_op=['VM_TEST_STOP']),
#                   create_img_stopped=              dict(vm_op=['VM_TEST_CREATE_IMG'], state_op=['VM_TEST_STOP']),
#                   resize_stopped=                  dict(vm_op=['VM_TEST_RESIZE_RVOL'], state_op=['VM_TEST_STOP']),
#                   del_snapshot_stopped=            dict(vm_op=['RVOL_DEL_SNAPSHOT'], state_op=['VM_TEST_STOP']),
#                   change_os_stopped=               dict(vm_op=['VM_TEST_CHANGE_OS'], state_op=['VM_TEST_STOP']),
#                   reset_stopped=                   dict(vm_op=['VM_TEST_RESET'], state_op=['VM_TEST_STOP']),
#                   revert_backup_stopped=           dict(vm_op=['VM_TEST_REVERT_BACKUP'], state_op=['VM_TEST_STOP']),
#                   create_img_from_backup_stopped=  dict(vm_op=['VM_TEST_BACKUP_IMAGE'], state_op=['VM_TEST_STOP']),
#                   migrate_stopped=                 dict(vm_op=['VM_TEST_MIGRATE'], state_op=['VM_TEST_STOP']),
#                   change_os_snapshot_stopped=      dict(vm_op=['VM_TEST_CHANGE_OS', 'VM_TEST_SNAPSHOT'], state_op=['VM_TEST_STOP']),
#                   backup_reboot=                   dict(vm_op=['VM_TEST_NONE', 'VM_TEST_SNAPSHOT'], state_op=['VM_TEST_NONE', 'VM_TEST_REBOOT']),
#                   )


def record(fun):
    def recorder(vm, op):
        global index
        if op != tag:
            Path[index].append(op)
        alif op == tag:
            Path.append([op])
            Path[index].append(op)
            index += 1
        return fun(vm, op)

    return recorder


VM_RUNNING_OPS = [
    "VM_TEST_SNAPSHOT",
    "VM_TEST_CREATE_IMG",
    "VM_TEST_RESIZE_RVOL",
    "RVOL_DEL_SNAPSHOT",
    "VM_TEST_NONE",
    "VM_TEST_BACKUP_IMAGE",
    "DVOL_TEST_CREATE_IMG",
    "DVOL_TEST_SNAPSHOT",
    "DVOL_DEL_SNAPSHOT",
    "DVOL_TEST_RESIZE",
    "DVOL_TEST_BACKUP_IMAGE",
    "CREATE_ATTACH_VOLUME"
]

VM_STOPPED_OPS = [
    "VM_TEST_SNAPSHOT",
    "VM_TEST_CREATE_IMG",
    "VM_TEST_RESIZE_RVOL",
    "RVOL_DEL_SNAPSHOT",
    "VM_TEST_CHANGE_OS",
    "VM_TEST_RESET",
    "VM_TEST_NONE",
    "VM_TEST_REVERT_BACKUP",
    "VM_TEST_REVERT_VM_BACKUP",
    "VM_TEST_BACKUP_IMAGE",
    "DVOL_TEST_CREATE_IMG",
    "DVOL_TEST_SNAPSHOT",
    "DVOL_DEL_SNAPSHOT",
    "DVOL_TEST_RESIZE",
    "DVOL_TEST_BACKUP_IMAGE",
    "DVOL_TEST_REVERT_BACKUP",
    "CREATE_ATTACH_VOLUME"
]

VM_STATE_OPS = [
    "VM_TEST_STOP",
    "VM_TEST_REBOOT",
    "VM_TEST_NONE"
]


@record
def vm_op_test(vm, op):
    test_util.test_logger(vm.vm.name + "-------" + op)
    ops = {
        "VM_TEST_STOP": stop,
        "VM_TEST_REBOOT": reboot,
        "VM_TEST_NONE": do_nothing,
        "VM_TEST_MIGRATE": migrate,
        "VM_TEST_SNAPSHOT": create_snapshot,
        "VM_TEST_CREATE_IMG": create_image,
        "VM_TEST_RESIZE_RVOL": resize_rvol,
        "RVOL_DEL_SNAPSHOT": delete_snapshot,
        "VM_TEST_CHANGE_OS": change_os,
        "VM_TEST_RESET": reset,
        "VM_TEST_BACKUP": back_up,
        "VM_TEST_REVERT_BACKUP": revert_backup,
        "VM_TEST_REVERT_VM_BACKUP": revert_vm_backup,
        "VM_TEST_BACKUP_IMAGE": backup_image 
        "DVOL_TEST_SNAPSHOT": create_dvol_snapshot,
        "DVOL_DEL_SNAPSHOT": delete_dvol_snapshot,
        "DVOL_TEST_CREATE_IMG": create_dvol_image,
        "DVOL_TEST_RESIZE": resize_dvol,
        "DVOL_BACKUP": dvol_back_up,
        "DVOL_TEST_BACKUP_IMAGE": dvol_backup_image,
        "CREATE_ATTACH_VOLUME": create_attach_volume

    }
    ops[op](vm)


def stop(vm):
    vm.stop()


def reboot(vm):
    vm.reboot()


def do_nothing(vm):
    pass


def reset(vm):
    vm.reinit()


def migrate(vm_obj):
    ps = test_lib.lib_get_primary_storage_by_vm(vm_obj.get_vm())
    if vm_obj.vm.state == "Running" and ps.type in [inventory.CEPH_PRIMARY_STORAGE_TYPE, 'SharedMountPoint', inventory.NFS_PRIMARY_STORAGE_TYPE,
                   'SharedBlock', inventory.LOCAL_STORAGE_TYPE]:
        target_host = test_lib.lib_find_random_host(vm_obj.vm)
        vm_obj.migrate(target_host.uuid)
    elif ps.type in [inventory.LOCAL_STORAGE_TYPE]:
        vm_obj.check()
        target_host = test_lib.lib_find_random_host(vm_obj.vm)
        vol_ops.migrate_volume(vm_obj.get_vm().allVolumes[0].uuid, target_host.uuid)
        vm_obj.start()
        test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)
    else:
        test_util.test_fail("FOUND NEW STORAGTE TYPE. FAILED")


def create_snapshot(vm_obj):
    vol_obj = zstack_volume_header.ZstackTestVolume()
    vol_obj.set_volume(test_lib.lib_get_root_volume(vm_obj.get_vm()))
    snapshots_root = zstack_sp_header.ZstackVolumeSnapshot()
    snapshots_root.set_utility_vm(vm_obj)
    snapshots_root.set_target_volume(vol_obj)
    snapshots_root.create_snapshot('create_data_snapshot1')
    snapshots_root.check()
    sp1 = snapshots_root.get_current_snapshot()
    #vm_obj.stop()
    #vm_obj.check()
    #snapshots_root.use_snapshot(sp1)
    #vm_obj.start()
    #test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)

def delete_snapshot(vm_obj):
    vol_obj = zstack_volume_header.ZstackTestVolume()
    vol_obj.set_volume(test_lib.lib_get_root_volume(vm_obj.get_vm()))
    snapshots_root = zstack_sp_header.ZstackVolumeSnapshot()
    snapshots_root.set_utility_vm(vm_obj)
    snapshots_root.set_target_volume(vol_obj)
    sp_list = snapshots_root.get_snapshot_list()
    if sp_list:
        snapshots_root.delete_snapshot(random.choice(sp_list))

def create_image(vm_obj):
    volume_uuid = test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid
    bs_list = test_lib.lib_get_backup_storage_list_by_vm(vm_obj.vm)
    image_option = test_util.ImageOption()
    image_option.set_root_volume_uuid(volume_uuid)
    image_option.set_name('image_resize_template')
    image_option.set_backup_storage_uuid_list([bs_list[0].uuid])
    image = img_ops.create_root_volume_template(image_option)
    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)
    new_image.set_image(image)
    new_image.check()
    new_image.clean()

def resize_rvol(vm_obj):
    vol_size = test_lib.lib_get_root_volume(vm_obj.get_vm()).size
    volume_uuid = test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid
    set_size = 1024 * 1024 * 1024 + int(vol_size)
    vol_ops.resize_volume(volume_uuid, set_size)
    vm_obj.update()
    vol_size_after = test_lib.lib_get_root_volume(vm_obj.get_vm()).size
    # if set_size != vol_size_after:
    #     test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)
    # vm_obj.check()
    test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)


def change_os(vm_obj):
    vm_uuid = vm_obj.get_vm().uuid
    last_l3network_uuid = test_lib.lib_get_l3s_uuid_by_vm(vm_obj.get_vm())
    last_ps_uuid = test_lib.lib_get_root_volume(vm_obj.get_vm()).primaryStorageUuid
    cond = res_ops.gen_query_conditions("system", '=', "false")
    cond = res_ops.gen_query_conditions("mediaType", '=', "RootVolumeTemplate", cond)
    cond = res_ops.gen_query_conditions("platform", '=', "Linux", cond)
    image_uuid = random.choice(res_ops.query_resource(res_ops.IMAGE, cond)).uuid
    vm_ops.change_vm_image(vm_uuid, image_uuid)
    vm_obj.start()
    vm_obj.update()
    # check whether the vm is running successfully
    test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)
    # check whether the network config has changed
    l3network_uuid_after = test_lib.lib_get_l3s_uuid_by_vm(vm_obj.get_vm())
    if l3network_uuid_after != last_l3network_uuid:
        test_util.test_fail('Change VM Image Failed.The Network config has changed.')
    # check whether primarystorage has changed
    ps_uuid_after = test_lib.lib_get_root_volume(vm_obj.get_vm()).primaryStorageUuid
    if ps_uuid_after != last_ps_uuid:
        test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')


def back_up(vm_obj):
     global backup
     cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
     bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0]
     backup_option = test_util.BackupOption()
     backup_option.set_name("test_compare")
     backup_option.set_volume_uuid(test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid)
     backup_option.set_backupStorage_uuid(bs.uuid)
     backup = vol_ops.create_vm_backup(backup_option)
     backup_list.append(backup)

def revert_backup(vm_obj):
    backup_uuid = random.choice(backup_list.pop(random.randint(0, len(backup_list)-1))).uuid
    vol_ops.revert_volume_from_backup(backup_uuid)

def revert_vm_backup(vm_obj):
    group_uuid = backup[0].groupUuid
    vol_ops.revert_vm_from_backup(group_uuid) 

def backup_image(vm_obj):
    cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0] 
    backup = random.choice(backup_list)
    image = img_ops.create_root_template_from_backup(bs.uuid, backup[0].uuid)

def create_attach_volume(vm_obj):
    global test_obj_dict
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume.attach(vm_obj)


def create_dvol_snapshot(vm_obj):
    global utility_vm, dvol
    snapshots_root = zstack_sp_header.ZstackVolumeSnapshot()
    snapshots_root.set_utility_vm(utility_vm)
    snapshots_root.set_target_volume(dvol)
    snapshots_root.create_snapshot('create_data_snapshot1')

def delete_dvol_snapshot(vm_obj):
    global utility_vm, dvol
    snapshots_root = zstack_sp_header.ZstackVolumeSnapshot()
    snapshots_root.set_utility_vm(utility_vm)
    snapshots_root.set_target_volume(dvol)
    sp_list = snapshots_root.get_snapshot_list()
    if sp_list:
        snapshots_root.delete_snapshot(random.choice(sp_list))

def create_dvol_image(vm_obj):
    global dvol
    volume_uuid = dvol.volume.uuid
    bs_list = test_lib.lib_get_backup_storage_list_by_vm(vm_obj.vm)
    image_option = test_util.ImageOption()
    image_option.set_data_volume_uuid(volume_uuid)
    image_option.set_name('image_resize_template')
    image_option.set_backup_storage_uuid_list([bs_list[0].uuid])
    image = img_ops.create_data_volume_template(image_option)
    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)
    new_image.set_image(image)
    new_image.check()
    new_image.delete()
    new_image.expunge()

def dvol_backup_image(vm_obj):
    cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0]
    backup = random.choice(backup_list)
    if type(backup) != list:
        image = img_ops.create_data_template_from_backup(bs.uuid, backup.uuid)
    else:
        image = img_ops.create_data_template_from_backup(bs.uuid, backup[1].uuid)

def resize_dvol(vm_obj):
    global dvol
    vol_size = dvol.volume.size
    volume_uuid = dvol.volume.uuid
    set_size = 1024 * 1024 * 1024 + int(vol_size)
    vol_ops.resize_data_volume(volume_uuid, set_size)
    vm_obj.update()


def dvol_back_up(vm_obj):
    global backup,dvol
    cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0]
    backup_option = test_util.BackupOption()
    backup_option.set_name("test_compare")
    backup_option.set_volume_uuid(dvol.volume.uuid)
    backup_option.set_backupStorage_uuid(bs.uuid)
    backup = vol_ops.create_backup(backup_option)
    backup_list.append(backup)


def print_path(Path):
    print("=" * 43 + "PATH" + "=" * 43)
    for i in range(len(Path)):
        path = ''
        for j in range(len(Path[i])):
            if j == len(Path[i]) - 1:
                path += Path[i][j]
            else:
                path += (Path[i][j] + " --> ")
        print(path)
    print("=" * 90)


def test():
    global test_obj_dict, VM_RUNNING_OPS, VM_STOPPED_OPS, VM_STATE_OPS, backup, dvol
    #flavor = case_flavor[os.environ.get('CASE_FLAVOR')]

    #VM_OP = flavor['vm_op']
    #STATE_OP = flavor['state_op']

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]
    if ps.type == "AliyunNAS":
        test_util.test_skip("VolumeBackup does not support AliyunNAS for now")
#    if ps.type != inventory.LOCAL_STORAGE_TYPE and 'VM_TEST_MIGRATE' in VM_OP and "VM_TEST_STOP" in STATE_OP:
#        test_util.test_skip("Shared Storage does not support migration")

    vm_name = "test_vm"
    utility_vm_name = "utility_vm"

    cond = res_ops.gen_query_conditions("system", '=', "false")
    cond = res_ops.gen_query_conditions("mediaType", '=', "RootVolumeTemplate", cond)
    cond = res_ops.gen_query_conditions("platform", '=', "Linux", cond)
    cond = res_ops.gen_query_conditions("name", '=', "image_for_sg_test", cond)
    img_name = res_ops.query_resource(res_ops.IMAGE, cond)[0].name
    cond = res_ops.gen_query_conditions("category", '=', "Private")
    l3_name = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].name
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    disk_offering_uuids = [disk_offering.uuid]
    vm = test_stub.create_vm(vm_name, img_name, l3_name, disk_offering_uuids=disk_offering_uuids)
    vm.check()
    test_obj_dict.add_vm(vm)
    hostuuid = vm.get_vm().hostUuid
    utility_vm = test_stub.create_vm(utility_vm_name, img_name, l3_name, host_uuid=hostuuid)
    utility_vm.check()
    test_obj_dict.add_vm(utility_vm)

    dvol = zstack_volume_header.ZstackTestVolume()
    dvol.set_volume(test_lib.lib_get_data_volumes(vm.get_vm())[0])
    dvol.set_state(volume_header.ATTACHED)
    dvol.set_target_vm(vm)
    test_obj_dict.add_volume(dvol)

    i = 0
    while True:
        if i == 10:
            vm_op_test(vm, "VM_TEST_STOP")
            vm_op_test(vm, "VM_TEST_RESET")
            vm.start()
            vm.check()
            i = 0
        vm_op_test(vm, random.choice(VM_STATE_OPS))
        if vm.state == "Running":
            VM_OPS = VM_RUNNING_OPS
            if not backup_list:
                VM_OPS.remove("VM_TEST_BACKUP_IMAGE")
        elif vm.state == "Stopped":
            VM_OPS = VM_STOPPED_OPS
            if not backup_list:
                VM_OPS.remove("VM_TEST_REVERT_BACKUP")
                VM_OPS.remove("VM_TEST_BACKUP_IMAGE")
                VM_OPS.remove("VM_TEST_REVERT_VM_BACKUP")


        vm_op_test(vm, random.choice(VM_OPS))

        if vm.state == "Stopped":
            vm.start()
            vm.check()

        if test_lib.lib_is_vm_l3_has_vr(vm.vm):
            test_lib.TestHarness = test_lib.TestHarnessVR
        cmd = "echo 111 > /home/" + str(int(time.time()))
        test_lib.lib_execute_command_in_vm(vm.vm,cmd)
        cmd = "dd if=/dev/urandom of=/dev/vdb bs=512k count=1"
        test_lib.lib_execute_command_in_vm(vm.vm,cmd)

        vm.suspend()
        # create_snapshot/backup
        vm_op_test(vm, "VM_TEST_BACKUP")
        # compare vm & image created by backup
        if ps.type != inventory.CEPH_PRIMARY_STORAGE_TYPE:
            compare(ps, vm, backup)

        vm.resume()
    print_path(Path)
    test_lib.lib_error_cleanup(test_obj_dict)

def error_cleanup():
    global test_obj_dict
    print_path(Path)
    #test_lib.lib_error_cleanup(test_obj_dict)

def compare(ps, vm, backup):
    test_util.test_logger("-----------------compare----------------")
    # find vm_host
    host = test_lib.lib_find_host_by_vm(vm.vm)
    cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0]

    root_volume = test_lib.lib_get_root_volume(vm.get_vm())
    data_volume = test_lib.lib_get_data_volumes(vm.get_vm())[0]
    vm_path = root_volume.installPath
    data_path = data_volume.installPath
    if ps.type == "SharedBlock":
        vm_path = "/dev/" + root_volume.installPath.split("/")[2] + "/" + root_volume.installPath.split("/")[3]
        data_path = "/dev/" + data_volume.installPath.split("/")[2] + "/" + data_volume.installPath.split("/")[3]
    test_util.test_logger(vm_path)
    test_util.test_logger(data_path)

    for i in backup:
        if i.type == "Root":
            name = i.backupStorageRefs[0].installPath.split("/")[2]
            id = i.backupStorageRefs[0].installPath.split("/")[3]
        if i.type == "Data":
            name1 = i.backupStorageRefs[0].installPath.split("/")[2]
            id1 = i.backupStorageRefs[0].installPath.split("/")[3]

    # compare vm_root_volume & image
    cmd = "mkdir /root/%s;" \
          "/usr/local/zstack/imagestore/bin/zstcli " \
          "-rootca=/var/lib/zstack/imagestorebackupstorage/package/certs/ca.pem " \
          "-url=%s:8000 " \
          "pull -installpath /root/%s/old.qcow2 %s:%s;" \
          "qemu-img compare %s /root/%s/old.qcow2;" % (id, bs.hostname, id, name, id, vm_path, id)
    cmd1 = "mkdir /root/%s;" \
          "/usr/local/zstack/imagestore/bin/zstcli " \
          "-rootca=/var/lib/zstack/imagestorebackupstorage/package/certs/ca.pem " \
          "-url=%s:8000 " \
          "pull -installpath /root/%s/old.qcow2 %s:%s;" \
          "qemu-img compare %s /root/%s/old.qcow2;" % (id1, bs.hostname, id1, name1, id1, data_path, id1)
    # clean image
    result = test_lib.lib_execute_ssh_cmd(host.managementIp, "root", "password", cmd, timeout=300)
    if result != "Images are identical.\n":
        test_util.test_fail("compare vm_root_volume & image created by backup")
    result = test_lib.lib_execute_ssh_cmd(host.managementIp, "root", "password", cmd1, timeout=300)
    if result != "Images are identical.\n":
        test_util.test_fail("compare vm_data_volume & image created by backup")
