import os
import random
import time
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
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.header.host as host_header
import zstackwoodpecker.header.volume as volume_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

Path = [[]]
index = 0
tag = "VM_TEST_REBOOT"
utility_vm = None
backup = None
backup_list = []

case_flavor = dict(snapshot_running=                dict(vm_op=['DVOL_TEST_SNAPSHOT'], state_op=['VM_TEST_NONE']),
                   create_img_running=              dict(vm_op=['DVOL_TEST_CREATE_IMG'], state_op=['VM_TEST_NONE']),
                   resize_running=                  dict(vm_op=['DVOL_TEST_RESIZE'], state_op=['VM_TEST_NONE']),
                   create_img_from_backup_running=  dict(vm_op=['VM_TEST_BACKUP_IMAGE'], state_op=['VM_TEST_NONE']),
                   delete_snapshot_running=         dict(vm_op=['DVOL_DEL_SNAPSHOT'], state_op=['VM_TEST_NONE']),
                   snapshot_stopped=                dict(vm_op=['DVOL_TEST_SNAPSHOT'], state_op=['VM_TEST_STOP']),
                   create_img_stopped=              dict(vm_op=['DVOL_TEST_CREATE_IMG'], state_op=['VM_TEST_STOP']),
                   resize_stopped=                  dict(vm_op=['DVOL_TEST_RESIZE'], state_op=['VM_TEST_STOP']),
                   create_img_from_backup_stopped=  dict(vm_op=['VM_TEST_BACKUP_IMAGE'], state_op=['VM_TEST_STOP']),
                   delete_snapshot_stopped=         dict(vm_op=['DVOL_DEL_SNAPSHOT'], state_op=['VM_TEST_STOP']),
                   revert_backup_stopped=           dict(vm_op=['VM_TEST_REVERT_BACKUP'], state_op=['VM_TEST_STOP']),
                   )


def record(fun):
    def recorder(vm, dvol, op):
        global index
        if op != tag:
            Path[index].append(op)
        elif op == tag:
            Path.append([op])
            Path[index].append(op)
            index += 1
        return fun(vm, dvol, op)

    return recorder


VOL_OPS = [
    "DVOL_TEST_CREATE_IMG",
    "DVOL_TEST_SNAPSHOT",
    "DVOL_DEL_SNAPSHOT",
    "DVOL_TEST_RESIZE",
    "VM_TEST_BACKUP_IMAGE"
    "VM_TEST_REVERT_BACKUP"
]

VM_STATE_OPS = [
    "VM_TEST_STOP",
    "VM_TEST_REBOOT",
    "VM_TEST_NONE"
]


@record
def vm_op_test(vm, dvol, op):
    test_util.test_logger(vm.vm.name + "-------" + op)
    ops = {
        "VM_TEST_STOP": stop,
        "VM_TEST_REBOOT": reboot,
        "VM_TEST_NONE": do_nothing,
        "DVOL_TEST_SNAPSHOT": create_snapshot,
        "DVOL_DEL_SNAPSHOT": delete_snapshot,
        "DVOL_TEST_CREATE_IMG": create_image,
        "DVOL_TEST_RESIZE": resize_dvol,
	"DVOL_BACKUP": back_up,
        "VM_TEST_REVERT_BACKUP": revert_backup,
        "VM_TEST_BACKUP_IMAGE": backup_image
    }
    ops[op](vm, dvol)


def stop(vm, dvol):
    vm.stop()


def reboot(vm, dvol):
    vm.reboot()


def do_nothing(vm, dvol):
    pass


def create_snapshot(vm_obj, dvol):
    global utility_vm
    snapshots_root = zstack_sp_header.ZstackVolumeSnapshot()
    snapshots_root.set_utility_vm(utility_vm)
    snapshots_root.set_target_volume(dvol)
    snapshots_root.create_snapshot('create_data_snapshot1')

def delete_snapshot(vm_obj, dvol):
    global utility_vm
    snapshots_root = zstack_sp_header.ZstackVolumeSnapshot()
    snapshots_root.set_utility_vm(utility_vm)
    snapshots_root.set_target_volume(dvol)
    sp_list = snapshots_root.get_snapshot_list()
    if sp_list:
        snapshots_root.delete_snapshot(random.choice(sp_list))

def create_image(vm_obj, dvol):
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

def revert_backup(vm_obj, dvol):
    backup_uuid = backup_list.pop(random.randint(0, len(backup_list)-1)).uuid
    vol_ops.revert_volume_from_backup(backup_uuid)

def backup_image(vm_obj, dvol):
    cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0]
    backup = random.choice(backup_list)
    image = img_ops.create_data_template_from_backup(bs.uuid, backup.uuid)

def resize_dvol(vm_obj, dvol):
    vol_size = dvol.volume.size
    volume_uuid = dvol.volume.uuid
    set_size = 1024 * 1024 * 1024 + int(vol_size)
    vol_ops.resize_data_volume(volume_uuid, set_size)
    vm_obj.update()
    # if set_size/vol_size_after > 0.9:
    #     test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)
    #vm_obj.check()
    #test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)


def back_up(vm_obj, dvol):
    global backup
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
    global test_obj_dict, VOL_OPS, VM_STATE_OPS, utility_vm, backup
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]

    DVOL_OP = flavor['vm_op']
    STATE_OP = flavor['state_op']

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]
    if ps.type == "AliyunNAS":
        test_util.test_skip("VolumeBackup does not support AliyunNAS for now")

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

    if "VM_TEST_BACKUP_IMAGE" in DVOL_OP or "VM_TEST_REVERT_BACKUP" in DVOL_OP:
        vm_op_test(vm, dvol, "DVOL_BACKUP")

    if "DVOL_DEL_SNAPSHOT" in DVOL_OP:
        vm_op_test(vm, dvol, "DVOL_TEST_SNAPSHOT")

    for i in DVOL_OP:
        vm_op_test(vm, dvol, random.choice(STATE_OP))
        if not backup_list and "VM_TEST_BACKUP_IMAGE" == i:
            i = "VM_TEST_NONE"

        vm_op_test(vm, dvol, i)

        if vm.state == "Stopped":
            vm.start()
            vm.check()

	if test_lib.lib_is_vm_l3_has_vr(vm.vm):
            test_lib.TestHarness = test_lib.TestHarnessVR
        
        cmd = "dd if=/dev/urandom of=/dev/vdb bs=512k count=1" 
	test_lib.lib_execute_command_in_vm(vm.vm,cmd)

        vm.suspend()
        vm_op_test(vm, dvol, "DVOL_BACKUP")
        if ps.type != inventory.CEPH_PRIMARY_STORAGE_TYPE:
            compare(ps, vm, dvol, backup)

        vm.resume()
        print_path(Path)
        test_lib.lib_error_cleanup(test_obj_dict)


def error_cleanup():
    global test_obj_dict
    print_path(Path)
    test_lib.lib_error_cleanup(test_obj_dict)


def compare(ps, vm, dvol, backup):
    test_util.test_logger("-----------------compare----------------")
    # find vm_host
    host = test_lib.lib_find_host_by_vm(vm.vm)
    cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0]

    cond = res_ops.gen_query_conditions("uuid", '=', dvol.volume.uuid)
    current_volume = res_ops.query_resource(res_ops.VOLUME, cond)[0]

    vol_path = current_volume.installPath
    if ps.type == "SharedBlock":
        vol_path = "/dev/" + current_volume.installPath.split("/")[2] + "/" + current_volume.installPath.split("/")[3]
    test_util.test_logger(vol_path)

    name = backup.backupStorageRefs[0].installPath.split("/")[2]
    id = backup.backupStorageRefs[0].installPath.split("/")[3]
    # compare vm_root_volume & image
    cmd = "mkdir /root/%s;" \
          "/usr/local/zstack/imagestore/bin/zstcli " \
          "-rootca=/var/lib/zstack/imagestorebackupstorage/package/certs/ca.pem " \
          "-url=%s:8000 " \
          "pull -installpath /root/%s/old.qcow2 %s:%s;" \
          "qemu-img compare %s /root/%s/old.qcow2;" % (id, bs.hostname, id, name, id, vol_path, id)
    # clean image
    result = test_lib.lib_execute_ssh_cmd(host.managementIp, "root", "password", cmd, timeout=300)
    if result != "Images are identical.\n":
        test_util.test_fail("compare vm_root_volume & image created by backup")

