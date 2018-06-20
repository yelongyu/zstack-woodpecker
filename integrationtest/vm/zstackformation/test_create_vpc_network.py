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
	resource_stack_option.set_name("Create_VPC_Network")
	templateContent = '''
{
	"ZStackTemplateFormatVersion": "2018-06-18",
	"Description": "本示例会创建一个简单的VPC网络，需要用户提供下面正确的数据i\n公有网络Uuid\n管理网络Uuid: 如果只有公有网络，则把公有网络当作管理网即可.\n",
	"Parameters": {
		"VrouterImageUrl": {
			"Type": "String",
			"Description":"云路由镜像链接地址"
		},
		"BackupStorage":{
			"Type": "CommaDelimitedList",
			"Description":"镜像服务器Uuid"
		},
		"ManagementNetworkUuid":{
			"Type": "String",
			"Description":"管理网络Uuid,如果只有共有网络填入共有网络Uuid即可"
		},
		"PublicNetworkUuid":{
			"Type": "String",
			"Description":"公有网络Uuid"
		},
		"ZoneUuid":{
			"Type": "String",
			"Description":"区域Uuid"
		},
		"ClusterUuid":{
			"Type": "String",
			"Description":"集群Uuid"
		},
		"Cidr":{
			"Type": "String"
			"Description":"VTEP Cider"
		},
		"Vni":{
			"Type": "Number",
			"DefaultValue":222
		},
		"StartVni":{
			"Type": "Number",
			"DefaultValue":100
		},
		"EndVni":{
			"Type": "Number",
			"DefaultValue":300
		},
		"PhysicalInterface":{
			"Type": "String"
		},
		"StartIp":{
			"Type": "String",
			"DefaultValue":"192.168.20.2"
		},
		"EndIp":{
			"Type": "String",
			"DefaultValue":"192.168.20.200"
		},
		"Netmask":{
			"Type": "String",
			"DefaultValue":"255.255.255.0"
		},
		"Gateway":{
			"Type": "String",
			"DefaultValue":"192.168.20.1"
		}
	},
	"Resources": {
		"VrouterImage": {
			"Type": "ZStack::Resource::Image",
			"Properties": {
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "Vrouter-Image"]]},
				"url": {"Ref":"VrouterImageUrl"},
				"system": true,
				"format": "qcow2",
				"backupStorageUuids":{"Ref":"BackupStorage"}
			}
		},
		"VirtualRouterOffering":{
			"Type":"ZStack::Resource::VirtualRouterOffering",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "Vrouter-Offering"]]},
				"zoneUuid":{"Ref":"ZoneUuid"},
				"managementNetworkUuid":{"Ref":"ManagementNetworkUuid"},
				"publicNetworkUuid":{"Ref":"PublicNetworkUuid"},
				"imageUuid":{"Fn::GetAtt":["VrouterImage", "uuid"]},
				"cpuNum":2,
				"memorySize":2147483648
			}
		},
		"VpcVRouter":{
			"Type":"ZStack::Resource::VpcVRouter",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "VPC-Router"]]},
				"virtualRouterOfferingUuid":{"Fn::GetAtt":["VirtualRouterOffering","uuid"]}
			}
		},
		"L2VxlanNetworkPool":{
			"Type":"ZStack::Resource::L2VxlanNetworkPool",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "L2VxlanNetworkPool"]]},
				"zoneUuid":{"Ref":"ZoneUuid"},
				"physicalInterface":{"Ref":"PhysicalInterface"}
			}
		},
		"VniRange":{
			"Type":"ZStack::Resource::VniRange",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "VniRange"]]},
				"startVni":{"Ref":"StartVni"},
				"endVni":{"Ref":"EndVni"},
				"l2NetworkUuid":{"Fn::GetAtt":["L2VxlanNetworkPool","uuid"]}
			}
		},
		"L2VxlanNetwork":{
			"Type":"ZStack::Resource::L2VxlanNetwork",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "L2VxlanNetwork"]]},
				"poolUuid":{"Fn::GetAtt":["L2VxlanNetworkPool","uuid"]},
				"zoneUuid":{"Ref":"ZoneUuid"},
				"vni":{"Ref":"Vni"},
				"physicalInterface":{"Ref":"PhysicalInterface"}
			}
		},
		"VpcL3Network":{
			"Type":"ZStack::Resource::L3Network",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "VPC-Network"]]},
				"l2NetworkUuid":{"Fn::GetAtt":["L2VxlanNetwork","uuid"]},
				"category":"Private",
				"type":"L3VpcNetwork"
			}
		},

		"AttachL3ToVm":{
			"Type":"ZStack::Action::AttachL3NetworkToVm",
			"Properties":{
				"vmInstanceUuid": {"Fn::GetAtt":["VpcVRouter","uuid"]},
				"l3NetworkUuid":{"Fn::GetAtt":["VpcL3Network","uuid"]}
			},
			"DependsOn":[{"Ref":"AddIpRange"}]
		},
		"AddIpRange" :{
			"Type":"ZStack::Action::AddIpRange",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "iprange"]]},
				"l3NetworkUuid":{"Fn::GetAtt":["VpcL3Network","uuid"]},
				"startIp":{"Ref":"StartIp"},
				"endIp":{"Ref":"EndIp"},
				"netmask":{"Ref":"Netmask"},
				"gateway":{"Ref":"Gateway"}
			}
		},
		"AttachL2NetworkToCluster":{
			"Type":"ZStack::Action::AddIpRange",
			"Properties":{
				"l2NetworkUuid":{"Fn::GetAtt":["L2VxlanNetwork","uuid"]},
				"clusterUuid":{"Ref":"ClusterUuid"},
				"systemTags":{"Fn::Join":["::",["l2NetworkUuid",{"Fn::GetAtt":["L2VxlanNetwork","uuid"]},"clusterUuid",{"Ref":"ClusterUuid"},"cidr",{"Ref":"Cidr"}]]}
			}
		}
	},
	"Outputs": {
		"vpc": {
			"Value": {
				"Ref": "VpcL3Network"
			}
		}
	}
}
'''
	parameter = '''
{
	"VrouterImageUrl": "http://172.20.198.234/mirror/zstack_vyos_image/176/zstack-vrouter-180528-176.qcow2",
	"BackupStorage":"e7f5ea3d546547d892c16e16187591ae",
	"ManagementNetworkUuid":"f6f17ccd25694b3992bf8172246bd16d",
	"PublicNetworkUuid":"f6f17ccd25694b3992bf8172246bd16d",
	"ZoneUuid":"b5ba5c34bcfe4bb0917b7587de25295b",
	"ClusterUuid":"d919bab269c94f67a1cdf9017d68f813",
	"Cidr":"172.20.78.0/16",
	"Vni":222,
	"StartVni":100,
	"EndVni":300,
	"PhysicalInterface":"eth0",
	"StartIp":"192.168.78.2",
	"EndIp":"192.168.78.120",
	"Netmask":"255.255.255.0",
	"Gateway":"192.168.78.1",
	"InstanceOfferingUuid": "8e1fb8ceed434829a892f32142d3cfd9",
	"ImageUuid":"ca0778d072a41bc39d5257493c025e71",
	"L3NetworkUuid":"27d87b240aab411890059715e08ed092"
}
'''
	resource_stack_option.set_templateContent(templateContent)
	resource_stack_option.set_parameters(parameter)
	resource_stack_option.set_rollback("true")

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
