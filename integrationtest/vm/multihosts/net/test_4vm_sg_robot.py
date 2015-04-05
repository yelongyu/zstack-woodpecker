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
        'timeout' : 12000,
        'noparallel' : False
        }

test_dict = test_state.TestStateDict()
    
def test():
    test_util.test_dsc('''
        Will doing random test Security Group operations, including SG create/delete, rule add/remove, vm nics attach/detach. If reach max 4 coexisting running vm, testing will success and quit.  Volume actions and Image actions are removed in this robot test.
        VM resources: Since SG testing will create target test vm, there might be max 12 running VMs: 4 VR VMs, 4 SG target test VMs and 4 test VMs.
    ''')
    target_running_vm = 4

    target_l3s = test_lib.lib_get_limited_l3_network(2, 5)

    vr_num = 0
    for target_l3 in target_l3s:
        vr_l3_uuid = target_l3.uuid
        vrs = test_lib.lib_find_vr_by_l3_uuid(vr_l3_uuid)
        temp_vm = None
        if not vrs:
            #create temp_vm for getting its vr for test pf_vm portforwarding
            vm_create_option = test_util.VmOption()
            vm_create_option.set_l3_uuids([vr_l3_uuid])
            temp_vm = test_lib.lib_create_vm(vm_create_option)
            test_dict.add_vm(temp_vm)

            #we only need temp_vm's VR
            temp_vm.destroy()
            test_dict.rm_vm(temp_vm)

        vr_num += 1
        #VIP testing need 3 VRs
        if vr_num > 2:
            break 

    vm_create_option = test_util.VmOption()
    #image has to use network test image, as it needs to do port checking
    vm_create_option.set_image_uuid(test_lib.lib_get_image_by_name(img_name=os.environ.get('imageName_net')).uuid)

    priority_actions = [test_state.TestAction.sg_rule_operations]*2
    priority_action_obj = action_select.ActionPriority()
    priority_action_obj.add_priority_action_list(priority_actions)
    test_util.test_dsc('Random Test Begin. Test target: 4 coexisting running VM (not include VR and SG target test VMs.).')
    robot_test_obj = test_util.Robot_Test_Object()
    robot_test_obj.set_test_dict(test_dict)
    robot_test_obj.set_vm_creation_option(vm_create_option)
    robot_test_obj.set_priority_actions(priority_action_obj)
    robot_test_obj.set_exclusive_actions_list(\
            test_state.TestAction.volume_actions \
            + test_state.TestAction.image_actions \
            + test_state.TestAction.vip_actions \
            + test_state.TestAction.snapshot_actions)

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
