#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Create a Basic vm with eip.
Cover resource:VM,VIP,EIP

@author: Lei Liu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
    test_util.test_dsc("Test Resource template Apis")
    
    cond = res_ops.gen_query_conditions('status', '=', 'Ready')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled', cond)
    cond = res_ops.gen_query_conditions('system', '=', 'false', cond)
    image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions("category", '=', "Public")
    l3_pub_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    
    cond = res_ops.gen_query_conditions("category", '=', "Private")
    cond = res_ops.gen_query_conditions('networkServices.networkServiceType', '=', 'EIP')
    l3_pri_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('type', '=', 'UserVm', cond)
    instance_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)  

    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("Create_STACK")
    resource_stack_option.set_rollback("true")
    templateContent = '''
{
	"ZStackTemplateFormatVersion": "2018-06-18",
	"Description": "Just create a VM with eip",
	"Parameters": {
		"InstanceOfferingUuid": {
			"Type": "String",
			"Label": "vm instance offering"
		},
		"ImageUuid":{
			"Type": "String"
		},
		"PrivateNetworkUuid":{
			"Type": "String"
		},
		"PublicNetworkUuid":{
			"Type": "String"
		}
	},
	"Resources": {
		"VmInstance": {
			"Type": "ZStack::Resource::VmInstance",
			"Properties": {
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"VM"]]},
				"instanceOfferingUuid": {"Ref":"InstanceOfferingUuid"},
				"imageUuid":{"Ref":"ImageUuid"},
				"l3NetworkUuids":[{"Ref":"PrivateNetworkUuid"}]
			}
		},
		"VIP": {
			"Type": "ZStack::Resource::Vip",
			"Properties": {
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"VIP"]]},
				"l3NetworkUuid":{"Ref":"PublicNetworkUuid"}
			}
		},
		"EIP":{
			"Type": "ZStack::Resource::Eip",
			"Properties": {
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"EIP"]]},
				"vipUuid":{"Fn::GetAtt":["VIP","uuid"]},
				"vmNicUuid":{"Fn::GetAtt":[{"Fn::Select":[0,{"Fn::GetAtt":["VmInstance","vmNics"]}]},"uuid"]}
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
    #1.create resource stack 
    test_util.test_logger('{"PrivateNetworkUuid":"%s","PublicNetworkUuid":"%s","ImageUuid":"%s","InstanceOfferingUuid":"%s"}' % (l3_pri_queried[0].uuid, l3_pub_queried[0].uuid, image_queried[0].uuid, instance_offering_queried[0].uuid))
    parameter = '{"PrivateNetworkUuid":"%s","PublicNetworkUuid":"%s","ImageUuid":"%s","InstanceOfferingUuid":"%s"}' % (l3_pri_queried[0].uuid, l3_pub_queried[0].uuid, image_queried[0].uuid, instance_offering_queried[0].uuid)
    
    resource_stack_option.set_templateContent(templateContent)
    resource_stack_option.set_parameters(parameter)
    preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)
    resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)
    

    #2.query resource stack
    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VM')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VIP')
    vip_queried = res_ops.query_resource(res_ops.VIP, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-EIP')
    eip_queried = res_ops.query_resource(res_ops.EIP, cond)

    if len(resource_stack_queried) == 0:
        test_util.test_fail("Fail to query resource stack")

    if resource_stack_queried[0].status == 'Created':
        if len(vm_queried) == 0 or len(vip_queried) == 0 or len(eip_queried) == 0:
            test_util.test_fail("Fail to create all resource when resource stack status is Created")
    elif len(vm_queried) != 0 or len(vip_queried) != 0 or len(eip_queried) != 0:
        test_util.test_fail("Fail to delete all resource when resource stack status is Rollbacked or Deleted")
    
    
    #3.get resource from resource stack
    resource = resource_stack_ops.get_resource_from_resource_stack(resource_stack.uuid)
    cond = res_ops.gen_query_conditions('name', '=', "vrouter")
    vrouter_provider = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)
    cond = res_ops.gen_query_conditions('name', '=', "virtualrouter")
    virtualrouter_provider = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)

    networkServiceProviderUuid = map(lambda x: x.networkServiceProviderUuid, l3_pri_queried[0].networkServices)
    if vrouter_provider[0].uuid in networkServiceProviderUuid or virtualrouter_provider[0].uuid in networkServiceProviderUuid:
        resource_num = 4
    else:
        resource_num = 3
    if resource == None or len(resource) != resource_num:
        test_util.test_fail("Fail to get resource from resource_stack")
    
    #4.query event from resource stack
    cond = res_ops.gen_query_conditions('stackUuid', '=', resource_stack.uuid)
    event = res_ops.query_event_from_resource_stack(cond)
    if event == None or len(event) != 6:
        test_util.test_fail("Fail to get event from resource_stack")

    #5.delete resource stack
    resource_stack_ops.delete_resource_stack(resource_stack.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VM')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VIP')
    vip_queried = res_ops.query_resource(res_ops.VIP, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-EIP')
    eip_queried = res_ops.query_resource(res_ops.EIP, cond)


    if len(resource_stack_queried) != 0 :
        test_util.test_fail("Fail to delete resource stack") 
    elif len(vm_queried) != 0 or len(vip_queried) != 0 or len(eip_queried) != 0:
        test_util.test_fail("Fail to delete resource when resource stack is deleted")   
   

    test_util.test_pass('Create Resource Stack Test Success')




#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"

