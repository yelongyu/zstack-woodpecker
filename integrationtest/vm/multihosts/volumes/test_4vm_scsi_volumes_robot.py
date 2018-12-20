'''

Robot test for volume actions

@author: Youyk
'''
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header

_config_ = {
        'timeout' : 10000,
        'noparallel' : False
        }

test_stub = test_lib.lib_get_test_stub()
test_dict = test_state.TestStateDict()
    
def test():
    test_util.test_dsc('''
        Will doing random test operations, including vm create/stop/start/reboot
        /destroy, volume create/attach/detach/delete. It doesn't include SG 
        VIP and snapshots operations. If reach max 4 coexisting running vm, 
        testing will success and quit. 
    ''')
    target_running_vm = 4

    test_util.test_dsc('Random Test Begin. Test target: 4 coexisting running VM (not include VR).')
    robot_test_obj = test_util.Robot_Test_Object()
    robot_test_obj.set_test_dict(test_dict)
    extra_exclusive_actions = []
    if test_lib.lib_get_image_store_backup_storage() != None:
        extra_exclusive_actions = [test_state.TestAction.create_data_vol_template_from_volume,
                                   test_state.TestAction.create_image_from_volume]

    robot_test_obj.set_exclusive_actions_list(\
            test_state.TestAction.sg_actions \
            + test_state.TestAction.vip_actions \
            + test_state.TestAction.snapshot_actions \
            + [ test_state.TestAction.create_volume ] \
            + extra_exclusive_actions)
    priority_actions = test_state.TestAction.volume_actions * 4
    priority_action_obj = action_select.ActionPriority()
    priority_action_obj.add_priority_action_list(priority_actions)
    robot_test_obj.set_priority_actions(priority_action_obj)

    rounds = 1
    while len(test_dict.get_vm_list(vm_header.RUNNING)) < target_running_vm:
        print "test_dict: %s" % test_dict
        test_util.test_dsc('New round %s starts: random operation pickup.' % rounds)
        test_lib.lib_vm_random_operation(robot_test_obj)
        test_util.test_dsc('Round %s finished. Begin status checking.' % rounds)
        rounds += 1
        test_lib.lib_robot_status_check(test_dict)

    test_util.test_dsc('Reach test pass exit criterial.')
    test_lib.lib_robot_cleanup(test_dict)
    test_util.test_pass('Create random VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_dict)
