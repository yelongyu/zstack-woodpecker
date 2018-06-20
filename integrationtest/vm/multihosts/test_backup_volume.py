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

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

Path = [[]]
index = 0
tag = "VM_TEST_REBOOT"
utility_vm = None
backup = None

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
    "DVOL_TEST_RESIZE"
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
        "DVOL_TEST_CREATE_IMG": create_image,
        "DVOL_TEST_RESIZE": resize_rvol,
	"DVOL_BACKUP": back_up,
    }
    ops[op](vm, dvol)


def stop(vm, dvol):
    vm.stop()


def reboot(vm, dvol):
    vm.reboot()


def do_nothing(vm, dvol):
    pass


def create_snapshot(vm_obj, dvol):
    snapshots_root = zstack_sp_header.ZstackVolumeSnapshot()
    snapshots_root.set_utility_vm(utility_vm)
    snapshots_root.set_target_volume(dvol)
    snapshots_root.create_snapshot('create_data_snapshot1')


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


def resize_rvol(vm_obj, dvol):
    vol_size = dvol.volume.size
    volume_uuid = dvol.volume.uuid
    set_size = 1024 * 1024 * 1024 + int(vol_size)
    vol_ops.resize_data_volume(volume_uuid, set_size)
    vm_obj.update()
    # if set_size/vol_size_after > 0.9:
    #     test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)
    vm_obj.check()
    test_lib.lib_wait_target_up(vm_obj.get_vm().vmNics[0].ip, 22, 300)


def back_up(vm_obj, dvol):
    global backup
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    backup_option = test_util.BackupOption()
    backup_option.set_name("test_compare")
    backup_option.set_volume_uuid(dvol.volume.uuid)
    backup_option.set_backupStorage_uuid(bs.uuid)
    backup = vol_ops.create_backup(backup_option) 


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

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]

    vm_name = "test_vm"
    utility_vm_name = "utility_vm"
    
    cond = res_ops.gen_query_conditions("system", '=', "false")
    cond = res_ops.gen_query_conditions("mediaType", '=', "RootVolumeTemplate", cond)
    cond = res_ops.gen_query_conditions("platform", '=', "Linux", cond)
    img_name = res_ops.query_resource(res_ops.IMAGE, cond)[0].name
    cond = res_ops.gen_query_conditions("category", '=', "Private")
    l3_name = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].name
    vm = test_stub.create_vm(vm_name, img_name, l3_name)
    utility_vm = test_stub.create_vm(utility_vm_name, img_name, l3_name)
    dvol = test_stub.create_volume()
    dvol.attach(vm)
 
    i = 0
    while True:
        OPS = VOL_OPS + VM_STATE_OPS

        vm_op_test(vm, dvol, random.choice(OPS))

        if vm.state == "Stopped":
            vm.start()

	if test_lib.lib_is_vm_l3_has_vr(vm.vm):
            test_lib.TestHarness = test_lib.TestHarnessVR
        time.sleep(60)
        
        cmd = "dd if=/dev/random of=/dev/vdb bs=512k count=1" 
	test_lib.lib_execute_command_in_vm(vm.vm,cmd)

        vm.suspend()
        vm_op_test(vm, dvol, "DVOL_BACKUP")
        compare(ps, vm, dvol, backup)

        vm.resume()


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
    print_path(Path)


def compare(ps, vm, dvol, backup):
    test_util.test_logger("-----------------compare----------------")
    # find vm_host
    host = test_lib.lib_find_host_by_vm(vm.vm)
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]

    current_volume = dvol.volume
    vol_path = current_volume.installPath
    if ps.type == "SharedBlock":
        vol_path = "/dev/" + current_volume.installPath.split("/")[2] + "/" + current_volume.installPath.split("/")[3]
    test_util.test_logger(vol_path)

    name = backup.installPath.split("/")[2]
    id = backup.installPath.split("/")[3]
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

