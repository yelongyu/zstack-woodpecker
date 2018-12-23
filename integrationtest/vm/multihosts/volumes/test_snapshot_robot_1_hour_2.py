'''

Robot Test only includes Vm operations, Volume operations and Snapshot operations

Case will run 1 hour with fair strategy. 

@author: Youyk
'''
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.test_state as ts_header
import os
import time

#Will sent 4000s as timeout, since case need to run at least ~3700s
_config_ = {
        'timeout' : 4600,
        'noparallel' : False
        }

test_dict = test_state.TestStateDict()
TestAction = ts_header.TestAction

case_flavor = dict(create_stop_start_attach_detach_destory_expunge_vm=           dict(path_list=[TestAction.create_vm, TestAction.stop_vm, TestAction.start_vm, TestAction.attach_volume, TestAction.detach_volume, TestAction.destroy_vm, TestAction.expunge_vm]),
                   create_reboot_attach_detach_destory_expunge_vm=               dict(path_list=[TestAction.create_vm, TestAction.reboot_vm, TestAction.attach_volume, TestAction.detach_volume, TestAction.destroy_vm, TestAction.expunge_vm]),
                  )
    
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    path_list = flavor['path_list']
    test_util.test_dsc('''Will mainly doing random test for all kinds of snapshot operations. VM, Volume and Image operations will also be tested. If reach 1 hour successful running condition, testing will success and quit.  SG actions, and VIP actions are removed in this robot test.
        VM resources: a special Utility vm is required to do volume attach/detach operation. 
        ''')
    target_running_vm = 4

    public_l3 = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName'))

    vm_create_option = test_util.VmOption()
    #image has to use virtual router image, as it needs to do port checking
    vm_create_option.set_image_uuid(test_lib.lib_get_image_by_name(img_name=os.environ.get('imageName_net')).uuid)

    utility_vm_create_option = test_util.VmOption()
    utility_vm_create_option.set_image_uuid(test_lib.lib_get_image_by_name(img_name=os.environ.get('imageName_net')).uuid)
    l3_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetworkName1')).uuid
    utility_vm_create_option.set_l3_uuids([l3_uuid])

    priority_actions = test_state.TestAction.snapshot_actions * 4
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
    robot_test_obj.set_random_type(action_select.resource_path_strategy)
    #path_list = [TestAction.create_vm, TestAction.stop_vm, TestAction.start_vm, TestAction.attach_volume, TestAction.detach_volume, TestAction.destroy_vm, TestAction.expunge_vm]
    robot_test_obj.set_required_path_list(path_list)

    rounds = 1
    current_time = time.time()
    timeout_time = current_time + 3600
    while time.time() <= timeout_time:
        test_util.test_dsc('New round %s starts: random operation pickup.' % rounds)
        test_lib.lib_vm_random_operation(robot_test_obj)
        test_util.test_dsc('===============Round %s finished. Begin status checking.================' % rounds)
        rounds += 1
        test_lib.lib_robot_status_check(test_dict)
        if not robot_test_obj.get_required_path_list():
            test_util.test_dsc('Reach test pass exit criterial: Required path executed %s' % (path_list))
            break

    test_lib.lib_robot_cleanup(test_dict)
    test_util.test_pass('Snapshots Robot Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_robot_cleanup(test_dict)
