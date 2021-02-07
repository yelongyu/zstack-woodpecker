'''

Robot Test only includes Vm operations, Volume operations and Snapshot operations

@author: Youyk
'''
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import os

test_dict = test_state.TestStateDict()
    
def test():
    test_util.test_dsc('''
        Will doing random test for VIP operations, including VIP create/delete, PF create/attach/detach/remove, EIP create/attach/detach/remove. VM operations will also be tested. If reach max 4 coexisting running vm, testing will success and quit.  SG actions, Volume actions and Image actions are removed in this robot test.
        VM resources: VIP testing needs at least 3 VRs are running. 
        ''')
    target_running_vm = 4

    public_l3 = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName'))

    vm_create_option = test_util.VmOption()
    #image has to use virtual router image, as it needs to do port checking
    vm_create_option.set_image_uuid(test_lib.lib_get_image_by_name(img_name=os.environ.get('imageName_net')).uuid)

    priority_actions = test_state.TestAction.snapshot_actions * 4
    utility_vm_create_option = test_util.VmOption()
    utility_vm_create_option.set_image_uuid(test_lib.lib_get_image_by_name(img_name=os.environ.get('imageName_net')).uuid)
    l3_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetworkName1')).uuid
    utility_vm_create_option.set_l3_uuids([l3_uuid])
    utility_vm = test_lib.lib_create_vm(utility_vm_create_option)
    test_dict.add_utility_vm(utility_vm)
    if os.environ.get('ZSTACK_SIMULATOR') != "yes":
        utility_vm.check()

    test_util.test_dsc('Random Test Begin. Test target: 4 coexisting running VM (not include VR and SG target test VMs.).')
    robot_test_obj = test_util.Robot_Test_Object()
    robot_test_obj.set_test_dict(test_dict)
    robot_test_obj.set_vm_creation_option(vm_create_option)
    priority_action_obj = action_select.ActionPriority()
    priority_action_obj.add_priority_action_list(priority_actions)
    robot_test_obj.set_priority_actions(priority_action_obj)
    robot_test_obj.set_exclusive_actions_list(\
            test_state.TestAction.vip_actions + \
            test_state.TestAction.image_actions + \
            test_state.TestAction.sg_actions)
    robot_test_obj.set_public_l3(public_l3)
    robot_test_obj.set_utility_vm(utility_vm)

    rounds = 1
    while len(test_dict.get_vm_list(vm_header.RUNNING)) < target_running_vm:
        test_util.test_dsc('New round %s starts: random operation pickup.' % rounds)
        test_lib.lib_vm_random_operation(robot_test_obj)
        test_util.test_dsc('===============Round %s finished. Begin status checking.================' % rounds)
        rounds += 1
        test_lib.lib_robot_status_check(test_dict)

    test_util.test_dsc('Reach test pass exit criterial.')
    test_lib.lib_robot_cleanup(test_dict)
    test_util.test_pass('Snapshots Robot Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_robot_cleanup(test_dict)
