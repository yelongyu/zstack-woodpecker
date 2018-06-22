#coding:utf-8
'''

New Integration Test for zstack cloudformation.

@author: Lei Liu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
	test_util.test_dsc("Test Resource template Apis")
	
	resource_stack_option = test_util.ResourceStackOption()
	resource_stack_option.set_name("Create_EIP")
	templateContent = '''
{
	"ZStackTemplateFormatVersion": "2018-06-18",
	"Description": "Just create a flat network & VM",
	"Parameters": {
		"InstanceOfferingUuid": {
			"Type": "String",
			"Lable": "vm instance offering"
		},
		"ImageUuid":{
			"Type": "String"
		},
		"ImageUuid":{
			"Type": "String"
		},
		"PrivateNetworkUuid":{
			"Type": "String"
		},
		"PublicNetworkUuid":{
			"Type": "String"
		},
		"RootDiskOfferingUuid":{
			"Type": "String"
		}
	},
	"Resources": {
		"VmInstance": {
			"Type": "ZStack::Resource::VmInstance",
			"Properties": {
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, {"Ref":"ZStack::StackUuid"},{"Ref":"ZStack::AccountUuid"},{"Ref":"ZStack::AccountName"},"VM"]]},
				"instanceOfferingUuid": {"Ref":"InstanceOfferingUuid"},
				"imageUuid":{"Ref":"ImageUuid"},
				"l3NetworkUuids":[{"Ref":"PrivateNetworkUuid"}],
				"rootDiskOfferingUuid":{"Ref":"RootDiskOfferingUuid"}
			}
		},
		"VIP": {
			"Type": "ZStack::Resource::Vip",
			"Properties": {
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, {"Ref":"ZStack::StackUuid"},{"Ref":"ZStack::AccountUuid"},{"Ref":"ZStack::AccountName"},"VIP"]]},
				"l3NetworkUuid":{"Ref":"PublicNetworkUuid"}
			}
		},
		"EIP":{
			"Type": "ZStack::Resource::Eip",
			"Properties": {
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, {"Ref":"ZStack::StackUuid"},{"Ref":"ZStack::AccountUuid"},{"Ref":"ZStack::AccountName"},"EIP"]]},
				"vipUuid":{"Fn::GetAtt":["VIP","uuid"]},
				"vmNicUuid":{"Fn::GetAtt":[{"Fn::Select":["0",[{"Fn::GetAtt":["VmInstance","vmNics"]}]]},"uuid"]}
			}
		}
	},
	"Outputs": {
		"VmInstance": {
			"Value": {
				"Ref": "VmInstance"
			}
		}
	}
}
'''

	parameter = '''
{
	"InstanceOfferingUuid": "8e1fb8ceed434829a892f32142d3cfd9",
	"ImageUuid":"ca0778d072a41bc39d5257493c025e71",
	"PrivateNetworkUuid":"27d87b240aab411890059715e08ed092",
	"PublicNetworkUuid":"f6f17ccd25694b3992bf8172246bd16d",
	"RootDiskOfferingUuid":"cd8d228190304745a88b404c21c87d50"
}
'''
	resource_stack_option.set_templateContent(templateContent)
	resource_stack_option.set_parameters(parameter)

	preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)

	resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)

	cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
	resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

	if len(resource_stack_queried) == 0:
		test_util.test_fail("Fail to query stack template")
	#Add a template via text.

	resource = resource_stack_ops.get_resource_from_resource_stack(resource_stack.uuid)
	print resource
	if resource == None:
		test_util.test_fail("Fail to get resource from resource_stack")

	print resource_stack.uuid
	cond = res_ops.gen_query_conditions('stackUuid', '=', resource_stack.uuid)
	event = res_ops.query_event_from_resource_stack(cond)
	print event
	if event == None:
		test_util.test_fail("Fail to get event from resource_stack")
	test_util.test_pass('Create Stack Template Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
	print "Ignore cleanup"
