'''
create autoscaling with cloud router 


@author: Antony WeiJiang
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.autoscaling_operations as autoscaling
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_load_balancer as zstack_lb_header
import os
import time
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
maxvm_number = 6
minvm_number = 2
initvm_number = 3

def test():
        test_util.test_dsc("create autoscaling group")

        test_util.test_dsc("create alarm")
	alarm_1Uuid = autoscaling.create_alarm('GreaterThan', 60, 99, 'ZStack/VM', 'MemoryUsedInPercent').uuid
	alarm_2Uuid = autoscaling.create_alarm('LessThan', 60, 1, 'ZStack/VM', 'MemoryUsedInPercent').uuid

	test_util.test_dsc("get l3 network uuid")
	l3_public_name = os.environ.get('l3NoVlanNetworkName2')
	l3NetworkUuids = test_lib.lib_get_l3_by_name(l3_public_name).uuid
	test_util.test_logger("%s" %(l3NetworkUuids))

	test_util.test_dsc("attache loadbalance service to l3 network")
	test_stub.attach_networkService_toL3Network(l3NetworkUuids)


	test_util.test_dsc("create load balance")
	l3_public_name = os.environ.get('l3PublicNetworkName')
	l3_net_uuid = test_lib.lib_get_l3_by_name(l3_public_name).uuid

	vip = test_stub.create_vip('vip_for_lb_test', l3_net_uuid)
	test_obj_dict.add_vip(vip)

	lb = zstack_lb_header.ZstackTestLoadBalancer()
	lb.create('autoscaling lb test debug', vip.get_vip().uuid)
	test_util.test_logger("%s" %(lb.get_load_balancer().uuid))
	test_obj_dict.add_load_balancer(lb)
	
	lb_creation_option = test_lib.lib_create_lb_listener_option('check vm http healthy','tcp',22,80)
	lbl = lb.create_listener(lb_creation_option)

        test_util.test_logger("get vm InstanceOffer uuid")
        vmInstanceOfferingUuid = res_ops.get_resource(res_ops.INSTANCE_OFFERING,None,None,os.environ.get('instanceOfferingName_s'))[0].uuid
        test_util.test_logger("%s" %(vmInstanceOfferingUuid))

        test_util.test_logger("get vm Image uuid")
        imageUuid = res_ops.get_resource(res_ops.IMAGE,None,None,os.environ.get('imageName3'))[0].uuid
        test_util.test_logger("%s" %(imageUuid))

        test_util.test_logger("get vm template uuid")
        listerUuid = lbl.get_load_balancer_listener().uuid
        vm_templateUuid = autoscaling.create_autoScaling_vmTemplate([l3NetworkUuids],vmInstanceOfferingUuid,imageUuid,l3NetworkUuids,["loadBalancerListenerUuids::"+listerUuid]).uuid
        test_util.test_logger("%s" %(vm_templateUuid))

        test_util.test_logger("get autoscaling group uuid")
        autoscaling_groupUuid = autoscaling.create_autoScaling_group(maxvm_number,minvm_number,["initialInstanceNumber::3","vmInstanceHealthStrategy::LoadBalanceBackendStatus","vmNicLoadbalancerListenerHealthCheckGraceTimeSeconds::120","automaticallyRemoveUnhealthyInstance::true"]).uuid
        test_util.test_logger("%s" %(autoscaling_groupUuid))

        test_util.test_logger("attach vm template to autoscaling group")
        autoscaling.attach_autoScaling_templateToGroup(autoscaling_groupUuid,vm_templateUuid)

        test_util.test_logger("add removal rule to autoscaling group")
        groupremovalinstanceruleUuid = autoscaling.create_autoScaling_group_removalInstanceRule(1,30,autoscaling_groupUuid).uuid
        autoscaling.create_autoScaling_ruleAlarmTrigger(alarm_2Uuid,groupremovalinstanceruleUuid)

	test_util.test_logger("add new instance rule to autoscaling group")
	groupnewinstanceruleUuid = autoscaling.create_autoScaling_group_addingNewInstanceRule(1,autoscaling_groupUuid,30).uuid
        autoscaling.create_autoScaling_ruleAlarmTrigger(alarm_1Uuid,groupnewinstanceruleUuid)
        
	test_util.test_logger("check vmm instance number")
        test_stub.check_autoscaling_init_vmm_number(initvm_number,autoscaling_groupUuid)

	time.sleep(200)	
        test_util.test_logger("check vmm instance numkber")
        test_stub.check_autoscaling_init_vmm_number(minvm_number,autoscaling_groupUuid)

        test_util.test_dsc("Delete autoscaling group")
        autoscaling.delete_autoScaling_group(autoscaling_groupUuid)
	autoscaling.deltet_loadbalancer(lb.get_load_balancer().uuid)
        test_util.test_pass("Test AutoScaling Group Successfully")


def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

