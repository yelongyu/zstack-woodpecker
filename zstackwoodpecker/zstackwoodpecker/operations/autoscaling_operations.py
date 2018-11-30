'''

All AutoScaling  operations for test.

@author: Antony WeiJiang
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
#import zstackwoodpecker.operations.zwatch_operations  as zwt_ops
import base64
import os


def create_alarm(comparisonOperator, period, threshold, namespace, metric_name, name=None, repeat_interval=None, labels=None, actions=None, resource_uuid=None, session_uuid=None):
	action = api_actions.CreateAlarmAction()
	test_util.test_logger("%s" %(comparisonOperator))
	action.timeout = 30000
	if name:
		action.name = name
	if not name:
		action.name = 'alarm_01'
	action.comparisonOperator = comparisonOperator
	action.period = period
	action.threshold = threshold
	action.namespace = namespace
	action.metricName = metric_name
	if actions:
		action.actions = actions
	if repeat_interval:
		action.repeatInterval = repeat_interval
	if labels:
		action.labels = labels
	if resource_uuid:
		action.resourceUuid = resource_uuid
	test_util.action_logger('Create Alarm: %s ' % name)
	evt = acc_ops.execute_action_with_session(action, session_uuid)
	return evt.inventory


def create_autoScaling_vmTemplate(l3NetworkUuids,vmInstanceOfferingUuid,imageUuid,defaultL3NetworkUuid,systemTags=None,vmTemplateName=None,vmInstanceName=None,session_uuid=None):
	action = api_actions.CreateAutoScalingVmTemplateAction()
	action.timeout = 30000
	if vmTemplateName:
		action.name = vmTemplateName
	if not vmTemplateName:
		action.name = 'vmTemplate_autoScaling'	
	test_util.test_logger("%s" %(action.name))
	if vmInstanceName:
		action.vmInstanceName = vmInstanceName
	if not vmInstanceName:
		action.vmInstanceName = 'vmm'
	test_util.test_logger("%s" %(action.vmInstanceName))	
	
	action.l3NetworkUuids = l3NetworkUuids
	test_util.test_logger("%s" %(action.l3NetworkUuids))

	action.vmInstanceOfferingUuid = vmInstanceOfferingUuid
	test_util.test_logger("%s" %(action.vmInstanceOfferingUuid))

	action.imageUuid = imageUuid
	test_util.test_logger("%s" %(action.imageUuid))
	
	action.defaultL3NetworkUuid = defaultL3NetworkUuid
	test_util.test_logger("%s" %(action.defaultL3NetworkUuid))

	if systemTags:
        	action.systemTags = systemTags
	#test_util.test_logger("%s" %(action.systemTags))
	test_util.action_logger('Create Vmm Template: %s ' % action.name)
	evt = acc_ops.execute_action_with_session(action, session_uuid)
	return evt.inventory

def create_autoScaling_group(maxResourceSize,minResourceSize,systemTags=None,autoScaling_group_name=None,session_uuid=None,removalPolicy="OldestInstance",defaultCooldown = 0,scalingResourceType="VmInstance",defaultEnable="true"):
	action = api_actions.CreateAutoScalingGroupAction()
	action.time = 3000
	action.removalPolicy = removalPolicy
	action.defaultCooldown = defaultCooldown
	action.maxResourceSize = maxResourceSize
	action.minResourceSize = minResourceSize
	action.scalingResourceType = scalingResourceType
	action.defaultEnable = defaultEnable
	if systemTags:
		action.systemTags = systemTags
	if autoScaling_group_name:
		action.name = autoScaling_group_name
	if not autoScaling_group_name:
		action.name = 'autoscaling-group'
	test_util.action_logger('Create AutoScaling Group  Template: %s ' % autoScaling_group_name)
	evt = acc_ops.execute_action_with_session(action, session_uuid)	
	return evt.inventory


def attach_autoScaling_templateToGroup(groupUuid,uuid,session_uuid=None):
	action = api_actions.AttachAutoScalingTemplateToGroupAction()
	action.time = 3000
	action.groupUuid = groupUuid
	action.uuid = uuid
	test_util.action_logger('attach vm template to autoscaling group')
	evt = acc_ops.execute_action_with_session(action, session_uuid)
	return evt.inventory

def create_autoScaling_group_removalInstanceRule(adjustmentValue,cooldown,autoScalingGroupUuid,removalInstanceRule_name=None,session_uuid=None,adjustmentType="QuantityChangeInCapacity",removalPolicy="OldestInstance"):
	action = api_actions.CreateAutoScalingGroupRemovalInstanceRuleAction()
	action.time = 3000
	action.adjustmentType = adjustmentType
	action.adjustmentValue = adjustmentValue
	action.removalPolicy = removalPolicy
	action.cooldown = cooldown
	action.autoScalingGroupUuid = autoScalingGroupUuid
	if removalInstanceRule_name:
		action.name = removalInstanceRule_name
	if not removalInstanceRule_name:
		action.name = 'removalInstanceRule'
	test_util.action_logger('create removal instance rule name:%s' % action.name)
	evt = acc_ops.execute_action_with_session(action, session_uuid)
	return evt.inventory

def create_autoScaling_group_addingNewInstanceRule(adjustmentValue,autoScalingGroupUuid,cooldown,addingNewInstanceRule_name=None,session_uuid=None,adjustmentType="QuantityChangeInCapacity"):
	action = api_actions.CreateAutoScalingGroupAddingNewInstanceRuleAction()
	action.time = 3000
	action.adjustmentType = adjustmentType
	action.adjustmentValue = adjustmentValue
	action.cooldown = cooldown
	action.autoScalingGroupUuid = autoScalingGroupUuid
	if addingNewInstanceRule_name:
		action.name = addingNewInstanceRule_name
	if not addingNewInstanceRule_name:
		action.name = 'addingNewInstanceRule'
	test_util.action_logger('create add new  instance rule name:%s' % action.name)
	evt = acc_ops.execute_action_with_session(action, session_uuid)
	return evt.inventory

def create_autoScaling_ruleAlarmTrigger(alarmUuid,ruleUuid,ruleAlarmTrigger_name=None,session_uuid=None):
	action = api_actions.CreateAutoScalingRuleAlarmTriggerAction()
	action.time = 3000
	action.alarmUuid = alarmUuid
	action.ruleUuid = ruleUuid
	if ruleAlarmTrigger_name:
		action.name = ruleAlarmTrigger_name
	if not ruleAlarmTrigger_name:
		action.name = 'ruleAlarmTrigger'
	test_util.action_logger('create rule alarm trigger :%s' % action.name)
	evt = acc_ops.execute_action_with_session(action, session_uuid)
	return evt.inventory

def delete_autoScaling_group(uuid,session_uuid=None):
	action = api_actions.DeleteAutoScalingGroupAction()
	action.time = 3000
	action.uuid = uuid
	test_util.action_logger('Delete autoscaling group :%s' % action.uuid)
	evt = acc_ops.execute_action_with_session(action, session_uuid)
	return evt.success	

def delete_autoScaling_template(uuid,session_uuid=None):
	action = api_actions.DeleteAutoScalingTemplateAction()
        action.time = 3000
        action.uuid = uuid
        test_util.action_logger('Delete autoscaling VM Template :%s' % action.uuid)
        evt = acc_ops.execute_action_with_session(action, session_uuid)
        return evt.success












  
	



	




