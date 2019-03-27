'''
New Integration Test for detaching iso under PS maintain mode.

@author: SyZhao
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import os
import time

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
ps_uuid = None
host_uuid = None
vr_uuid = None

def test():
    global test_obj_dict
    global ps_uuid
    global host_uuid
    global vr_uuid
    test_util.test_dsc('Create test vm and check')
    l3_1_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vlan_vm(l3_name=l3_1_name)
    #l3_1 = test_lib.lib_get_l3_by_name(l3_1_name)
    #vr = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)[0]
    #vr_uuid = vr.uuid
    
    host = test_lib.lib_get_vm_host(vm.get_vm())
    host_uuid = host.uuid
    test_obj_dict.add_vm(vm)
    vm.check()

    test_util.test_dsc('Add ISO Image')
    cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid
    img_option = test_util.ImageOption()
    img_option.set_name('iso')
    img_option.set_backup_storage_uuid_list([bs_uuid])
    command = "echo fake iso for test only >  %s/apache-tomcat/webapps/zstack/static/zstack-repo/7/x86_64/os/test.iso" % os.environ.get('zstackInstallPath')
    test_lib.lib_execute_ssh_cmd(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], 'root', 'password', command)
    img_option.set_url('http://%s:8080/zstack/static/zstack-repo/7/x86_64/os/test.iso' % (os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']))
    image_inv = img_ops.add_iso_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    test_obj_dict.add_image(image)

    test_util.test_dsc('Attach ISO to VM')
    cond = res_ops.gen_query_conditions('name', '=', 'iso')
    iso_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    img_ops.attach_iso(iso_uuid, vm.vm.uuid)

    #ps = test_lib.lib_get_primary_storage_by_vm(vm.get_vm())
    #ps_uuid = ps.uuid
    #ps_ops.change_primary_storage_state(ps_uuid, 'maintain')
    test_stub.maintain_all_pss()
    if not test_lib.lib_wait_target_down(vm.get_vm().vmNics[0].ip, '22', 90):
        test_util.test_fail('VM is expected to stop when PS change to maintain state')
    vm.set_state(vm_header.STOPPED)
    vm.check()

    test_util.test_dsc('Detach ISO to VM')
    img_ops.detach_iso(vm.vm.uuid)

    #ps_ops.change_primary_storage_state(ps_uuid, 'enable')
    test_stub.enable_all_pss()
    host_ops.reconnect_host(host_uuid)
    #vm_ops.reconnect_vr(vr_uuid)
    test_stub.ensure_pss_connected()
    vrs = test_lib.lib_get_all_vrs()
    for vr in vrs:
        vr_cond = res_ops.gen_query_conditions('uuid', '=', vr.uuid)
        vr_inv = res_ops.query_resource(res_ops.VM_INSTANCE, vr_cond)[0]
        if vr_inv.state == 'Stopped':
            vm_ops.start_vm(vr.uuid)
        else:
            test_lib.lib_wait_target_up(vr_inv.vmNics[0].ip, '22', 360)
            for _ in xrange(100):
                if res_ops.query_resource(res_ops.VM_INSTANCE, vr_cond)[0].state != 'Running':
                    time.sleep(3)
                else:
                    break

    vm.start()
    vm.check()
    vm.destroy()
    #vm.check()
    #vm.expunge()
    vm.check()
    test_util.test_pass('PS maintain mode Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global ps_uuid
    if ps_uuid != None:
        ps_ops.change_primary_storage_state(ps_uuid, 'enable')
    global host_uuid
    if host_uuid != None:
        host_ops.reconnect_host(host_uuid)
    vrs = test_lib.lib_get_all_vrs()
    for vr in vrs:
        vm_ops.start_vm(vr.uuid)  
    #global vr_uuid
    #if vr_uuid != None:
    #    vm_ops.reconnect_vr(vr_uuid)
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
