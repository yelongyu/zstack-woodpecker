import Queue
import threading
import time

import zstackwoodpecker.operations.longjob_operations as longjob_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util

q = Queue.Queue(1)
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def create_image(target_vm, image_name):
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    root_volume = test_lib.lib_get_root_volume(target_vm.get_vm())
    job_name = "APICreateRootVolumeTemplateFromRootVolumeMsg"
    job_data = "{\"name\":\"%s\",\"description\":\"\",\"isSystem\":true,\"platform\":\"Linux\",\"backupStorageUuids\":[\"%s\"],\"vmUuid\":\"%s\",\"volumeUuid\":\"%s\",\"format\":\"qcow2\",\"rootVolumeUuid\":\"%s\",\"mediaType\":\"RootVolumeTemplate\"}" % (
    image_name, bs.uuid, target_vm.get_vm().uuid, root_volume.uuid, root_volume.uuid)
    api_id = longjob_ops.submit_longjob(job_name, job_data).apiId
    cond = res_ops.gen_query_conditions("apiId", "=", api_id)

    result = "runniing"
    time.sleep(1)

    while result != "Succeeded":
        long_job = res_ops.query_resource(res_ops.LONGJOB, cond)[0]
        result = long_job.jobResult
        time.sleep(1)

    cond = res_ops.gen_query_conditions("name", "=", image_name)
    image = res_ops.query_resource(res_ops.IMAGE, cond)[0]
    q.put(image.uuid)


def test():
    vm = test_stub.create_vm(vm_name='basic-test-vm')
    test_obj_dict.add_vm(vm)

    root_volume_inv = vm.get_vm().allVolumes[0]

    install_path = root_volume_inv.installPath.replace("sharedblock://", "/dev/")
    hostUuid = vm.get_vm().hostUuid

    cond = res_ops.gen_query_conditions("uuid", "=", hostUuid)
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    host_ip = host.managementIp

    convert_cmd = "qemu-img convert %s -O qcow2 -f qcow2 template.qcow2 ; du template.qcow2 | awk '{print $1}'" % (
        install_path)
    measure_cmd = "qemu-img measure -f qcow2 -O qcow2 %s" % install_path
    convert_size = int(test_lib.lib_execute_ssh_cmd(host_ip, "root", "password", convert_cmd, timeout=120)) * 1024
    measure_size = int(
        test_lib.lib_execute_ssh_cmd(host_ip, "root", "password", measure_cmd, timeout=120).split("\n")[0].split(": ")[
            1])

    if convert_size > measure_size:
        test_util.test_fail("convert_size must less than measure_size")

    cmd = "lvs -otags,name,lv_size --units B"
    result = test_lib.lib_execute_ssh_cmd(host_ip, "root", "password", cmd, timeout=120)
    old_result = result.split("\n")

    t = threading.Thread(target=create_image, args=(vm, "vm-image"))
    t.start()

    new_result = []
    image_lv_size = None
    while q.empty():
        result = test_lib.lib_execute_ssh_cmd(host_ip, "root", "password", cmd, timeout=120)
        temp = result.split("\n")
        for i in temp:
            if i not in (old_result + new_result):
                new_result.append(i)

    t.join()

    for i in new_result:
        test_util.test_logger(i)

    image_uuid = q.get()
    test_util.test_logger(image_uuid)

    for lv in new_result:
        if "meta" not in lv:
            image_lv_size = int(lv.split(" ")[-1][:-1])

    test_util.test_logger("convert_size  : " + str(convert_size))
    test_util.test_logger("measure_size  : " + str(measure_size))
    test_util.test_logger("lv_size       : " + str(image_lv_size))

    assert convert_size < measure_size and measure_size < image_lv_size

    test_util.test_pass('Check VM Create Image Success')
    test_lib.lib_error_cleanup(test_obj_dict)


# Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
