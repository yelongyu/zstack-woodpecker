'''

New Integration Test for data protect under hybrid.

@author: Glody 
'''

import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

def test():
    vm_res = hyb_ops.get_data_protect_image_store_vm_ip(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
    hostname = vm_res[0]
    url = vm_res[1]
    username = vm_res[2]
    password = vm_res[3]
    sshport = vm_res[4]
    name = "BS-public"
    #end_point = 
    #attach_point = 
    #hyb_ops.add_disaster_image_store_bs(name, url, hostname, username, password, sshport, name, )
    test_util.test_pass('Setup data protect bs image store success, the ip is %s' %dpbs_imagestore_ip)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
