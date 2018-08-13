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

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

Path = [[]]
index = 0
tag = "VM_TEST_REBOOT"
backup = None
backup_list = []

case_flavor = dict(snapshot_running=                dict(vm_op=['VM_TEST_SNAPSHOT'], state_op=['VM_TEST_NONE']),
                   create_img_running=              dict(vm_op=['VM_TEST_CREATE_IMG'], state_op=['VM_TEST_NONE']),
                   resize_running=                  dict(vm_op=['VM_TEST_RESIZE_RVOL'], state_op=['VM_TEST_NONE']),
                   del_snapshot_running=            dict(vm_op=['RVOL_DEL_SNAPSHOT'], state_op=['VM_TEST_NONE']),
                   create_img_from_backup_running=  dict(vm_op=['VM_TEST_BACKUP_IMAGE'], state_op=['VM_TEST_NONE']),
                   migrate_running=                 dict(vm_op=['VM_TEST_MIGRATE'], state_op=['VM_TEST_NONE']),
                   snapshot_stopped=                dict(vm_op=['VM_TEST_SNAPSHOT'], state_op=['VM_TEST_STOP']),
                   create_img_stopped=              dict(vm_op=['VM_TEST_CREATE_IMG'], state_op=['VM_TEST_STOP']),
                   resize_stopped=                  dict(vm_op=['VM_TEST_RESIZE_RVOL'], state_op=['VM_TEST_STOP']),
                   del_snapshot_stopped=            dict(vm_op=['RVOL_DEL_SNAPSHOT'], state_op=['VM_TEST_STOP']),
                   change_os_stopped=               dict(vm_op=['VM_TEST_CHANGE_OS'], state_op=['VM_TEST_STOP']),
                   reset_stopped=                   dict(vm_op=['VM_TEST_RESET'], state_op=['VM_TEST_STOP']),
                   revert_backup_stopped=           dict(vm_op=['VM_TEST_REVERT_BACKUP'], state_op=['VM_TEST_STOP']),
                   create_img_from_backup_stopped=  dict(vm_op=['VM_TEST_BACKUP_IMAGE'], state_op=['VM_TEST_STOP']),
                   migrate_stopped=                 dict(vm_op=['VM_TEST_MIGRATE'], state_op=['VM_TEST_STOP']),
                   change_os_snapshot_stopped=      dict(vm_op=['VM_TEST_CHANGE_OS', 'VM_TEST_SNAPSHOT'], state_op=['VM_TEST_STOP']),
                   backup_reboot=                   dict(vm_op=['VM_TEST_NONE', 'VM_TEST_SNAPSHOT'], state_op=['VM_TEST_NONE', 'VM_TEST_REBOOT']),
                   )


def record(fun):
    def recorder(vm, op):
        global index
        if op != tag:
            Path[index].append(op)
        elif op == tag:
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
    "VM_TEST_BACKUP_IMAGE"
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
    "VM_TEST_BACKUP_IMAGE"
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
        "VM_TEST_BACKUP_IMAGE": backup_image 
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
    snapshots_root.set_utility_vm(utility_vm)
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
     bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
     backup_option = test_util.BackupOption()
     backup_option.set_name("test_compare")
     backup_option.set_volume_uuid(test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid)
     backup_option.set_backupStorage_uuid(bs.uuid)
     backup = vol_ops.create_backup(backup_option)
     backup_list.append(backup)

def revert_backup(vm_obj):
    backup_uuid = backup_list.pop(random.randint(0, len(backup_list)-1)).uuid
    vol_ops.revert_volume_from_backup(backup_uuid) 

def backup_image(vm_obj):
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0] 
    backup = random.choice(backup_list)
    image = img_ops.create_root_template_from_backup(bs.uuid, backup.uuid)

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
    global test_obj_dict, VM_RUNNING_OPS, VM_STOPPED_OPS, VM_STATE_OPS, backup
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]

    VM_OP = flavor['vm_op']
    STATE_OP = flavor['state_op']

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]
    if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE or ps.type == "AliyunNAS":
        test_util.test_skip("VolumeBackup does not support Ceph and AliyunNAS for now")
    if ps.type != inventory.LOCAL_STORAGE_TYPE and 'VM_TEST_MIGRATE' in VM_OP and "VM_TEST_STOP" in STATE_OP:
        test_util.test_skip("Shared Storage does not support migration")

    vm_name = "test_vm"
    cond = res_ops.gen_query_conditions("system", '=', "false")
    cond = res_ops.gen_query_conditions("mediaType", '=', "RootVolumeTemplate", cond)
    cond = res_ops.gen_query_conditions("platform", '=', "Linux", cond)
    img_name = res_ops.query_resource(res_ops.IMAGE, cond)[0].name
    cond = res_ops.gen_query_conditions("category", '=', "Private")
    l3_name = res_ops.query_resource(res_ops.L3_NETWORK,cond)[0].name
    vm = test_stub.create_vm(vm_name, img_name, l3_name)
    vm.check()
    test_obj_dict.add_vm(vm)

    if "VM_TEST_BACKUP_IMAGE" in VM_OP or "VM_TEST_REVERT_BACKUP" in VM_OP:
        vm_op_test(vm, "VM_TEST_BACKUP")

    if "RVOL_DEL_SNAPSHOT" in VM_OP:
        vm_op_test(vm, "VM_TEST_SNAPSHOT")

    for i,j in VM_OP,STATE_OP:
        vm_op_test(vm, j)
        if vm.state == "Running":
            if not backup_list and "VM_TEST_BACKUP_IMAGE" == i:
                i = "VM_TEST_NONE"
        elif vm.state == "Stopped":
            if not backup_list and ("VM_TEST_BACKUP_IMAGE" == i or "VM_TEST_REVERT_BACKUP" == i):
                i = "VM_TEST_NONE"

        vm_op_test(vm, i)

        if vm.state == "Stopped":
            vm.start()
            vm.check()

        if test_lib.lib_is_vm_l3_has_vr(vm.vm):
            test_lib.TestHarness = test_lib.TestHarnessVR
        cmd = "echo 111 > /home/" + str(int(time.time()))
        test_lib.lib_execute_command_in_vm(vm.vm,cmd)
        vm.suspend()
        # create_snapshot/backup
        vm_op_test(vm, "VM_TEST_BACKUP")
        # compare vm & image created by backup
        compare(ps, vm, backup)

        vm.resume()
    print_path(Path)
    test_lib.lib_error_cleanup(test_obj_dict)

def error_cleanup():
    global test_obj_dict
    print_path(Path)
    test_lib.lib_error_cleanup(test_obj_dict)

def compare(ps, vm, backup):
    test_util.test_logger("-----------------compare----------------")
    # find vm_host
    host = test_lib.lib_find_host_by_vm(vm.vm)
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]

    root_volume = test_lib.lib_get_root_volume(vm.get_vm())
    vm_path = root_volume.installPath
    if ps.type == "SharedBlock":
        vm_path = "/dev/" + root_volume.installPath.split("/")[2] + "/" + root_volume.installPath.split("/")[3]
    test_util.test_logger(vm_path)

    name = backup.backupStorageRefs[0].installPath.split("/")[2]
    id = backup.backupStorageRefs[0].installPath.split("/")[3]
    # compare vm_root_volume & image
    cmd = "mkdir /root/%s;" \
          "/usr/local/zstack/imagestore/bin/zstcli " \
          "-rootca=/var/lib/zstack/imagestorebackupstorage/package/certs/ca.pem " \
          "-url=%s:8000 " \
          "pull -installpath /root/%s/old.qcow2 %s:%s;" \
          "qemu-img compare %s /root/%s/old.qcow2;" % (id, bs.hostname, id, name, id, vm_path, id)
    # clean image
    result = test_lib.lib_execute_ssh_cmd(host.managementIp, "root", "password", cmd, timeout=300)
    if result != "Images are identical.\n":
        test_util.test_fail("compare vm_root_volume & image created by backup")
