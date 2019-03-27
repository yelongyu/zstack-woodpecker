'''
Test for deleting vm image check vm attach.
@author: SyZhao
'''

import os
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
image1 = None

def test():
    #skip ceph in c74
    cmd = "cat /etc/redhat-release | grep '7.4'"
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    rsp = test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
    if rsp != False:
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
        for i in ps:
            if i.type == 'Ceph':
                test_util.test_skip('cannot hotplug iso to the vm in ceph,it is a libvirt bug:https://bugzilla.redhat.com/show_bug.cgi?id=1541702.')

    global image1

    hosts = res_ops.query_resource(res_ops.HOST)
    if len(hosts) <= 1:
        test_util.test_skip("skip for host_num is not satisfy condition host_num>1")

    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])

    image_name1 = 'image1_a'
    image_option = test_util.ImageOption()
    image_option.set_format('qcow2')
    image_option.set_name(image_name1)
    #image_option.set_system_tags('qemuga')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url(os.environ.get('imageUrl_s'))
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(3600*1000)

    image1 = zstack_image_header.ZstackTestImage()
    image1.set_creation_option(image_option)
    image1.add_root_volume_template()
    image1.check()

    image_name = os.environ.get('imageName_net')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm1 = test_stub.create_vm(image_name1, image_name, l3_name)
    test_obj_dict.add_vm(vm1)

    image1.delete()
    image1.expunge()

    #target_host = test_lib.lib_find_random_host(vm1.vm)
    #vm1.migrate(target_host.uuid)
    test_stub.vm_ops_test(vm1, "VM_TEST_ATTACH")

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create VM Image in Image Store Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global image1
    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        image1.delete()
    except:
        pass
