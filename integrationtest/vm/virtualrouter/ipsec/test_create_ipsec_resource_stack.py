#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Create an IPsec by resource stack.

@author: chenyuan.xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.ipsec_operations as ipsec_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

def test():
    test_stub = test_lib.lib_get_test_stub()
    test_obj_dict1 = test_state.TestStateDict()
    test_obj_dict2 = test_state.TestStateDict()
    global mevoco1_ip
    global mevoco2_ip
    global ipsec1
    global ipsec2
    global templateContent
    mevoco1_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    mevoco2_ip = os.environ['secondZStackMnIp']
    test_util.test_dsc('Create test vip in mevoco1')   
    cond = res_ops.gen_query_conditions("category", '=', "Public")
    l3_pub1_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    cond = res_ops.gen_query_conditions("name", '=', os.environ.get('l3VlanNetworkName1'))
    l3_pri1_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    vip1 = test_stub.create_vip('ipsec1_vip', l3_pub1_queried[0].uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', l3_pri1_queried[0].uuid)
    first_zstack_cidrs = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Create test vip in mevoco2') 
    cond = res_ops.gen_query_conditions("category", '=', "Public")
    l3_pub2_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    cond = res_ops.gen_query_conditions("name", '=', os.environ.get('l3VlanDNATNetworkName'))
    l3_pri2_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanDNATNetworkName'))
    vip2 = test_stub.create_vip('ipsec2_vip', l3_pub2_queried[0].uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', l3_pri2_queried[0].uuid)
    second_zstack_cidrs = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr
    
    templateContent = '''
{
	"ZStackTemplateFormatVersion": "2018-06-18",
        "Description": "本示例会创建一个简单的IPsec通道，需要用户提供下面正确的数据\n已有的虚拟IP地址，\n本地子网Uuid，远端IP，远端CIDR，认证密钥",
	"Parameters": {
	    "VipUuid":{
                "Type": "String",
                "Label": "虚拟IP",
	        "Description":"已有的虚拟IP的Uuid"
	    },
	    "PrivateNetworkUuid":{
		"Type": "String",
                "Label": "本地网络",
		"Description":"本地网络Uuid"
	    },
	    "PeerAddress": {
		"Type": "String",
		"Description":"远端IP"
	    },
	    "PeerCidrs":{
		"Type": "CommaDelimitedList",
		"Description":"远端 Cidr"
	    },
	    "AuthKey":{
		"Type": "String",
		"DefaultValue":"Test1234"
	    }
	},
	"Resources": {
            "IPsecConnection":{
                "Type": "ZStack::Resource::IPsecConnection",
                "Properties": {
                    "name": "IPsec-STACK",
                    "vipUuid": {"Ref": "VipUuid"},
                    "l3NetworkUuid": {"Ref":"PrivateNetworkUuid"},
                    "peerAddress": {"Ref":"PeerAddress"},
                    "peerCidrs": {"Ref":"PeerCidrs"},
                    "authKey": {"Ref":"AuthKey"}
                }
            }
	},
	"Outputs": {
	    "IPsecConnection": {
	        "Value": {
		"Ref": "IPsecConnection"
		}
	    }
	}
}

'''
    #1.create resource stack 
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_util.test_dsc('Create ipsec in mevoco1')
    resource_stack1_option = test_util.ResourceStackOption()
    resource_stack1_option.set_name("Create_STACK-IPSEC1")
    resource_stack1_option.set_rollback("true")
    print ('aooo = %s is %s') % ([second_zstack_cidrs], type([second_zstack_cidrs]))
    parameter1 = '{"VipUuid":"%s","PrivateNetworkUuid":"%s","PeerAddress":"%s","PeerCidrs":"%s"}' % (vip1.get_vip().uuid, l3_pri1_queried[0].uuid, vip2.get_vip().ip, second_zstack_cidrs)   
    resource_stack1_option.set_templateContent(templateContent)
    resource_stack1_option.set_parameters(parameter1)
    preview_resource_stack1 = resource_stack_ops.preview_resource_stack(resource_stack1_option)
    resource_stack1 = resource_stack_ops.create_resource_stack(resource_stack1_option)
    
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Create ipsec in mevoco2')
    resource_stack2_option = test_util.ResourceStackOption()
    resource_stack2_option.set_name("Create_STACK-IPSEC2")
    resource_stack2_option.set_rollback("true")
    parameter2 = '{"VipUuid":"%s","PrivateNetworkUuid":"%s","PeerAddress":"%s","PeerCidrs":"%s"}' % (vip2.get_vip().uuid, l3_pri2_queried[0].uuid, vip1.get_vip().ip, first_zstack_cidrs)
    resource_stack2_option.set_templateContent(templateContent)
    resource_stack2_option.set_parameters(parameter2)
    preview_resource_stack2 = resource_stack_ops.preview_resource_stack(resource_stack2_option)
    resource_stack2 = resource_stack_ops.create_resource_stack(resource_stack2_option)

    #2.query resource stack
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_util.test_dsc('Query resource stack in mevoco1')
    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack1.uuid)
    resource_stack1_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'IPsec-STACK')
    ipsec1_queried = res_ops.query_resource(res_ops.IPSEC_CONNECTION, cond)

    if len(resource_stack1_queried) == 0:
        test_util.test_fail("Fail to query resource stack")

    if resource_stack1_queried[0].status == 'Created':
        if len(ipsec1_queried) == 0: 
            test_util.test_fail("Fail to create ipsec connection when resource stack status is Created")

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Query resource stack in mevoco2')
    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack2.uuid)
    resource_stack2_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'IPsec-STACK')
    ipsec2_queried = res_ops.query_resource(res_ops.IPSEC_CONNECTION, cond)

    if len(resource_stack2_queried) == 0:
        test_util.test_fail("Fail to query resource stack")

    if resource_stack2_queried[0].status == 'Created':
        if len(ipsec2_queried) == 0 :
            test_util.test_fail("Fail to create ipsec connection when resource stack status is Created")  
    
    #3.get resource from resource stack
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_util.test_dsc('Get resource from resource stack in mevoco1')
    resource1 = resource_stack_ops.get_resource_from_resource_stack(resource_stack1.uuid)
    if resource1 == None or len(resource1) != 1:
        test_util.test_fail("Fail to get resource from resource_stack")

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Get resource from resource stack in mevoco2')
    resource2 = resource_stack_ops.get_resource_from_resource_stack(resource_stack2.uuid)
    if resource2 == None or len(resource1) != 1:
        test_util.test_fail("Fail to get resource from resource_stack")
    
    #4.query event from resource stack
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_util.test_dsc('Get resource from resource stack in mevoco1')
    cond = res_ops.gen_query_conditions('stackUuid', '=', resource_stack1.uuid)
    event1 = res_ops.query_event_from_resource_stack(cond)
    if event1 == None or len(event1) != 2:
        test_util.test_fail("Fail to get event from resource_stack")

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Get resource from resource stack in mevoco2')
    cond = res_ops.gen_query_conditions('stackUuid', '=', resource_stack2.uuid)
    event2 = res_ops.query_event_from_resource_stack(cond)
    if event2 == None or len(event2) != 2:
        test_util.test_fail("Fail to get event from resource_stack")

    #5.delete resource stack
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_util.test_dsc('Delete resource stack in mevoco1')
    resource_stack_ops.delete_resource_stack(resource_stack1.uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack1.uuid)
    resource_stack1_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)
    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-IPSEC1')
    ipsec1_queried = res_ops.query_resource(res_ops.IPSEC_CONNECTION, cond)
    if len(resource_stack1_queried) != 0:
        test_util.test_fail("Fail to delete resource stack") 
    elif len(ipsec1_queried) != 0:
        test_util.test_fail("Fail to delete ipsec connection when resource stack is deleted")   
    
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Delete resource stack in mevoco2')
    resource_stack_ops.delete_resource_stack(resource_stack2.uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack2.uuid)
    resource_stack2_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)
    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-IPSEC2')
    ipsec2_queried = res_ops.query_resource(res_ops.IPSEC_CONNECTION, cond)
    if len(resource_stack2_queried) != 0:
        test_util.test_fail("Fail to delete resource stack") 
    elif len(ipsec2_queried) != 0:
        test_util.test_fail("Fail to delete ipsec connection when resource stack is deleted")
   

    test_util.test_pass('Create IPsec Resource Stack Test Success')




#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"


