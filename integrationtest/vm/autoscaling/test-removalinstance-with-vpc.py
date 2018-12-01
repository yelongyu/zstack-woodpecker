'''
create autoscaling with vpc router ,and verify expansion strategy


@author: Antony WeiJiang
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.autoscaling_operations as autoscaling
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import os
import time
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
maxvm_number = 6
minvm_number = 2
initvm_number = 3
adjustment_number = 4
cooldown_time = 120
memory_threshold =99
period = 20

def test():
        test_util.test_dsc("create autoscaling group")

        test_util.test_dsc("create alarm")
        alarm_1Uuid = autoscaling.create_alarm('GreaterThan', 60, 99, 'ZStack/VM', 'MemoryUsedInPercent').uuid
        alarm_2Uuid = autoscaling.create_alarm('LessThan', 60, 1, 'ZStack/VM', 'MemoryUsedInPercent').uuid

        test_util.test_dsc("get l3 network uuid")
        l3_public_name = os.environ.get(test_stub.L3_SYSTEM_NAME_LIST[0])
	test_util.test_logger("%s" %(l3_public_name))
        l3NetworkUuids = test_lib.lib_get_l3_by_name(l3_public_name).uuid
        test_util.test_logger("%s" %(l3NetworkUuids))

        test_util.test_logger("get vm InstanceOffer uuid")
        vmInstanceOfferingUuid = res_ops.get_resource(res_ops.INSTANCE_OFFERING,None,None,os.environ.get('instanceOfferingName_s'))[0].uuid
        test_util.test_logger("%s" %(vmInstanceOfferingUuid))

        test_util.test_logger("get vm Image uuid")
        imageUuid = res_ops.get_resource(res_ops.IMAGE,None,None,os.environ.get('imageName3'))[0].uuid
        test_util.test_logger("%s" %(imageUuid))

        test_util.test_logger("get vm template uuid")
        listerUuid = res_ops.get_resource(res_ops.LOAD_BALANCER_LISTENER)[0].uuid
        vm_templateUuid = autoscaling.create_autoScaling_vmTemplate([l3NetworkUuids],vmInstanceOfferingUuid,imageUuid,l3NetworkUuids,["loadBalancerListenerUuids::"+listerUuid]).uuid
        test_util.test_logger("%s" %(vm_templateUuid))

        test_util.test_logger("get autoscaling group uuid")
        autoscaling_groupUuid = autoscaling.create_autoScaling_group(maxvm_number,minvm_number,["initialInstanceNumber::3"]).uuid
        test_util.test_logger("%s" %(autoscaling_groupUuid))

        test_util.test_logger("attach vm template to autoscaling group")
        autoscaling.attach_autoScaling_templateToGroup(autoscaling_groupUuid,vm_templateUuid)

        test_util.test_logger("add removal rule to autoscaling group")
        groupremovalinstanceruleUuid = autoscaling.create_autoScaling_group_removalInstanceRule(1,30,autoscaling_groupUuid).uuid
        autoscaling.create_autoScaling_ruleAlarmTrigger(alarm_2Uuid,groupremovalinstanceruleUuid)


        test_util.test_logger("add new instance rule to autoscaling group")
        groupnewinstanceruleUuid = autoscaling.create_autoScaling_group_addingNewInstanceRule(1,autoscaling_groupUuid,30).uuid
        autoscaling.create_autoScaling_ruleAlarmTrigger(alarm_1Uuid,groupnewinstanceruleUuid)
	
	test_util.test_logger("check autoscaling init")
	test_stub.check_autoscaling_init_vmm_number(initvm_number,autoscaling_groupUuid)

	test_util.test_logger("update memory percent")
	autoscaling.update_alarm(alarm_1Uuid,period,memory_threshold)
	autoscaling.update_alarm(alarm_2Uuid,period,memory_threshold)
	
	test_util.test_logger("update modify removal instance number")
	autoscaling.update_autoscalinggroup_removalinstance(groupremovalinstanceruleUuid,adjustment_number,cooldown_time)
	time.sleep(120)
	test_util.test_logger("check removal instance number")
	test_stub.check_removalinstance_vmm_number(minvm_number,minvm_number,autoscaling_groupUuid)
	
	test_util.test_dsc("Delete autoscaling group")
        autoscaling.delete_autoScaling_group(autoscaling_groupUuid)
        test_stub.check_deleteautoscaling_vmm_number()
        test_util.test_pass("Test AutoScaling Group Successfully")

def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

