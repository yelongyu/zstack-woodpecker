'''
cover ZSTAC-21097
Disable MN host 
1.create VM
2.restart VM & restart host libvirtd;
3.check error msg;
@author: Zhaohao
'''
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import traceback
import os
import time

test_stub = test_lib.lib_get_test_stub()
test_dict = test_state.TestStateDict()
err_msg_check_flag = 'invalid '
hosts = None


def test():
    global test_dict
    round = 10
    def restart_libvirtd(host_ip):
        cmd = "systemctl restart libvirtd.service"
        test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', cmd)
        test_util.test_logger("Restart libvirtd %s" % host_ip)

    def restart_vm(vm):
        vm_uuid = vm.get_vm().uuid
        vm_cond = res_ops.gen_query_conditions('uuid', '=', vm_uuid)
        vm_state = res_ops.query_resource(res_ops.VM_INSTANCE, vm_cond)[0].state
        if vm_state == "Stopped":
            vm.start()
        vm.reboot()

    MN_IP = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    mn_cond = res_ops.gen_query_conditions('managementIp', '=', MN_IP)
    mn_host = res_ops.query_resource(res_ops.HOST, mn_cond)
    if len(mn_host):
        #Disable MN Host
        mn_host_uuid = mn_host[0].uuid
        host_ops.change_host_state(mn_host_uuid, 'disable')
    #1.create VM
    image_name = os.environ.get('imageName_s')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm_name = "restart_test"
    vm = test_stub.create_vm(vm_name, image_name, l3_name) 
    test_dict.add_vm(vm)
    host_uuid = vm.get_vm().hostUuid
    host_cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host_ip = res_ops.query_resource(res_ops.HOST, host_cond)[0].managementIp
    #2.restart VM & restart host libvirtd;
    #3.check error msg;
    for i in range(round):
        libvirt_restart_thread = test_stub.ExcThread(target=restart_libvirtd,args=(host_ip,))
        restart_vm_thread = test_stub.ExcThread(target=restart_vm,args=(vm,))
        restart_vm_thread.start()
        libvirt_restart_thread.start()
        if restart_vm_thread.exitcode:
            if err_msg_check_flag in restart_vm_thread.exc_traceback:
                test_util.test_fail("Error check failed!Exception msg: %s" % restart_vm_thread.exc_traceback) 
        libvirt_restart_thread.join()
        restart_vm_thread.join()
        time.sleep(5) #service was attempted too often
    test_util.test_pass('Create VM successed!')

def env_recover():
    global test_dict
    test_lib.lib_robot_cleanup(test_dict)
    
def error_cleanup():
    global test_dict
    test_lib.lib_robot_cleanup(test_dict)
