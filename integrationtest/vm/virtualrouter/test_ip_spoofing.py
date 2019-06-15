'''
@author: MengLai
'''
import os
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.config_operations as con_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

node_ip = os.environ.get('node1Ip')
test_file_src = "/home/%s/zstack-woodpecker/integrationtest/vm/virtualrouter/change_ip_test_template.sh" % node_ip
test_file_des = "/home/%s/zstack-woodpecker/integrationtest/vm/virtualrouter/change_ip_test.sh" % node_ip
ct_original = None

def test():
    global test_obj_dict
    global test_file_src
    global test_file_des
    global ct_original

    if con_ops.get_global_config_value('vm', 'cleanTraffic') == 'false' :
        ct_original='false'
        con_ops.change_global_config('vm', 'cleanTraffic', 'true')  
    else:
        ct_original='true'

    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip

    new_vm_ip = '172.24.1.1'
    if new_vm_ip == vm_ip:
        new_vm_ip = '172.24.1.2'

    test_util.test_dsc("Prepare Test File")
    cmd = "cp %s %s" % (test_file_src, test_file_des)
    os.system(cmd)
    cmd = "sed -i \"s/TemplateNodeIP/%s/g\" %s" % (node_ip, test_file_des)
    os.system(cmd)
    cmd = "sed -i \"s/TemplateOriginalIP/%s/g\" %s" % (vm_ip, test_file_des)
    os.system(cmd)
    cmd = "sed -i \"s/TemplateTestIP/%s/g\" %s" % (new_vm_ip, test_file_des)
    os.system(cmd)

    target_file = "/home/change_ip_test.sh"
    test_stub.scp_file_to_vm(vm_inv, test_file_des, target_file)

    cmd = "chmod +x %s" % target_file
    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 180)
    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', target_file, 180)

    time.sleep(60)

    cmd = "cat /home/ip_spoofing_result"
    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 180)
    if rsp[0] != "1":
        test_util.test_fail(rsp)
    
    vm.destroy()
    test_obj_dict.rm_vm(vm)
    con_ops.change_global_config('vm', 'cleanTraffic', ct_original)
    os.system('rm -f %s' % test_file_des)
    test_util.test_pass('IP Spoofing Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    global test_file_des
    global ct_original
    con_ops.change_global_config('vm', 'cleanTraffic', ct_original)
    os.system('rm -f %s' % test_file_des) 
    test_lib.lib_error_cleanup(test_obj_dict)
