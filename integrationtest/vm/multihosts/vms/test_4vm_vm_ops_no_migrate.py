'''

@author: Youyk
'''
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import os

_config_ = {
        'timeout' : 10000,
        'noparallel' : False
        }

test_stub = test_lib.lib_get_test_stub()
test_dict = test_state.TestStateDict()
    
def test():
    test_util.test_dsc('''
        Will doing random test Security Group operations, including SG create/delete, rule add/remove, vm nics attach/detach. If reach max 4 coexisting running vm, testing will success and quit.  Volume actions and Image actions are removed in this robot test.
        VM resources: Since SG testing will create target test vm, there might be max 12 running VMs: 4 VR VMs, 4 SG target test VMs and 4 test VMs.
    ''')
    target_running_vm = 4

    vm_create_option = test_util.VmOption()

    test_util.test_dsc('Random Test Begin. Test target: 4 coexisting running VM (not include VR and SG target test VMs.).')
    robot_test_obj = test_util.Robot_Test_Object()
    robot_test_obj.set_test_dict(test_dict)
    robot_test_obj.set_vm_creation_option(vm_create_option)
    priority_actions = [test_state.TestAction.sg_rule_operations]*2
    priority_action_obj = action_select.ActionPriority()
    priority_action_obj.add_priority_action_list(priority_actions)
    robot_test_obj.set_priority_actions(priority_action_obj)
    exclusive_actions_list = test_state.TestAction.volume_actions \
            + test_state.TestAction.image_actions \
            + test_state.TestAction.vip_actions \
            + test_state.TestAction.sg_actions \
            + test_state.TestAction.snapshot_actions

    exclusive_actions_list.append(test_state.TestAction.migrate_vm)
    robot_test_obj.set_exclusive_actions_list(exclusive_actions_list)
    rounds = 1
    while len(test_dict.get_vm_list(vm_header.RUNNING)) < target_running_vm:
        test_util.test_dsc('New round %s starts: random operation pickup.' % rounds)
        test_lib.lib_vm_random_operation(robot_test_obj)
        test_util.test_dsc('===============Round %s finished. Begin status checking.================' % rounds)
        rounds += 1
        test_lib.lib_robot_status_check(test_dict)

    test_util.test_dsc('Reach test pass exit criterial.')
    test_lib.lib_robot_cleanup(test_dict)
    test_util.test_pass('Create random VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_robot_cleanup(test_dict)
