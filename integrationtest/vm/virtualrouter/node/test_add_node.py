'''

Test multi nodes. This case might impact other cases' behavior, due node adding
and removing. So it should not be parallelly executed with other cases.

@author: Youyk
'''
import os
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_node as zstack_test_node

import zstacklib.utils.xmlobject as xmlobject

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    test_util.test_dsc('Add new reserved node and create VM to see if node is functional')
    node_option = test_util.NodeOption()
    if test_lib.deploy_config.has_element('nodes') and test_lib.deploy_config.nodes.has_element('node'):
        nodes = test_lib.deploy_config.nodes.get_child_node_as_list('node')
        for node in nodes:
            if node:
                if node.reserve__:
                    test_util.test_dsc('Find reserved node and will start it')
                    node_option.set_name(node.name_)
                    node_option.set_username(node.username_)
                    node_option.set_password(node.password_)
                    node_option.set_management_ip(node.ip_)
                    node_option.set_docker_image(node.dockerImage__)

                    test_node = zstack_test_node.ZstackTestNode()
                    test_node.set_node_option(node_option)
                    test_node.add(test_lib.setup_plan)
                    test_node.check()

                    test_util.test_dsc('Start new node finished. Try to create a VM.')
                    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
                    test_obj_dict.add_vm(vm1)
                    vm1.check()
                    vm1.destroy()
                    test_node.check()

                    test_util.test_dsc('Stop created Node and try to create another VM.')
                    test_node.stop()
                    time.sleep(10) #Need some time to identify node is stopped
                    test_node.check()
                    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
                    test_obj_dict.add_vm(vm1)
                    vm1.check()
                    vm1.destroy()
                    test_node.check()

                    test_util.test_pass('add a new node test pass')
                    return True

    test_util.test_skip('No avaiable reserved nodes')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
