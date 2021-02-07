#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Create a vm by using vpc network.
Cover resource:VM,VR image,VR offering,l2vxlanpool,l2vxlannetwork,vpc network,vpc vrouter,vnirange

@author: Lei Liu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
    test_util.test_dsc("Test Resource template Apis")
    
    cond = res_ops.gen_query_conditions("category", '=', "Public")
    l3_pub_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    bs_queried = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    zone_queried = res_ops.query_resource(res_ops.ZONE, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cluster_queried = res_ops.query_resource(res_ops.CLUSTER, cond)

    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("Create_STACK-VPC")
    resource_stack_option.set_rollback("true")
    templateContent = '''
{
	"ZStackTemplateFormatVersion": "2018-06-18",
	"Description": "本示例会创建一个简单的VPC网络，需要用户提供下面正确的数据\n公有网络Uuid\n管理网络Uuid: 如果只有公有网络，则把公有网络当作管理网即可.\nVxlan网络的VTEP Cider",
	"Parameters": {
		"VrouterImageUrl": {
			"Type": "String",
            "Label":"云路由镜像链接地址",
			"Description":"云路由镜像链接地址",
			"DefaultValue": "http://cdn.zstack.io/product_downloads/vrouter/2.3/zstack-vrouter-2.3.2.qcow2"
		},
		"VmImageUrl": {
			"Type": "String",
            "Label": "云主机镜像链接地址",
			"Description":"测试云主机镜像，请确定ZStack 可以下载下面链接的镜像",
			"DefaultValue": "http://cdn.zstack.io/zstack_repo/latest/zstack-image-1.4.qcow2"
		},
		"BackupStorage":{
			"Type": "CommaDelimitedList",
            "Label": "镜像服务器",
			"Description":"镜像服务器Uuid"
		},
		"ManagementNetworkUuid":{
			"Type": "String",
            "Label": "管理网络",
			"Description":"管理网络Uuid,如果只有公有网络填入公有网络Uuid即可"
		},
		"PublicNetworkUuid":{
			"Type": "String",
            "Label": "公有网络",
			"Description":"公有网络Uuid"
		},
		"ZoneUuid":{
			"Type": "String",
            "Label": "区域",
			"Description":"区域Uuid"
		},
		"ClusterUuid":{
			"Type": "String",
            "Label": "集群",
			"Description":"集群Uuid"
		},
		"Cidr":{
			"Type": "String",
			"Description":"VTEP Cider",
			"DefaultValue":"{172.20.0.1/8}"
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
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"Vrouter-Image"]]},
				"url": {"Ref":"VrouterImageUrl"},
				"system": true,
				"format": "qcow2",
				"backupStorageUuids":{"Ref":"BackupStorage"}
			}
		},
		"VMImage": {
			"Type": "ZStack::Resource::Image",
			"Properties": {
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "VmImage"]]},
				"url": {"Ref":"VmImageUrl"},
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
				"cpuNum":1,
				"memorySize":1073741824
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
				"zoneUuid":{"Ref":"ZoneUuid"}
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
				"vni":{"Ref":"Vni"}
			}
		},
		"VpcL3Network":{
			"Type":"ZStack::Resource::L3Network",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "VPC-Network"]]},
				"l2NetworkUuid":{"Fn::GetAtt":["L2VxlanNetwork","uuid"]},
				"category":"Private",
				"type":"L3VpcNetwork",
				"systemTags":["networkservices::VRouter"]
			}
		},
		"InstanceOffering":{
			"Type":"ZStack::Resource::InstanceOffering",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "1cpu","1G"]]},
				"cpuNum": 1,
				"memorySize" : 1073741824
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
			"Type":"ZStack::Action::AttachL2NetworkToCluster",
			"Properties":{
				"l2NetworkUuid":{"Fn::GetAtt":["L2VxlanNetworkPool","uuid"]},
				"clusterUuid":{"Ref":"ClusterUuid"},
				"systemTags":[{"Fn::Join":["::",["l2NetworkUuid",{"Fn::GetAtt":["L2VxlanNetwork","uuid"]},"clusterUuid",{"Ref":"ClusterUuid"},"cidr",{"Ref":"Cidr"}]]}]
			}
		},
		"TestVm":{
			"Type":"ZStack::Resource::VmInstance",
			"Properties":{
				"name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "TestVm"]]},
				"instanceOfferingUuid": {"Fn::GetAtt":["InstanceOffering","uuid"]},
				"l3NetworkUuids": [{"Fn::GetAtt":["VpcL3Network","uuid"]}],
				"imageUuid": {"Fn::GetAtt":["VMImage", "uuid"]}
			},
			"DependsOn":[{"Ref":"AttachL3ToVm"}]
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
    #1.create resource stack 
    #test_util.test_logger('{"PrivateNetworkUuid":"%s","ImageUuid":"%s","InstanceOfferingUuid":"%s"}' % (l3_pri_queried[0].uuid, image_queried[0].uuid, instance_offering_queried[0].uuid))
    parameter = '{"PublicNetworkUuid":"%s","ManagementNetworkUuid":"%s","BackupStorage":"%s","ZoneUuid":"%s","ClusterUuid":"%s"}' % (l3_pub_queried[0].uuid, l3_pub_queried[0].uuid, bs_queried[0].uuid, zone_queried[0].uuid, cluster_queried[0].uuid)
    
    resource_stack_option.set_templateContent(templateContent)
    resource_stack_option.set_parameters(parameter)
    preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)
    resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)
    

    #2.query resource stack
    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-Vrouter-Image')
    vr_image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-Vrouter-Offering')
    vr_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-VPC-Router')
    vpc_router_queried = res_ops.query_resource(res_ops.VIRTUALROUTER_VM, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-L2VxlanNetwotkPool')
    l2_vxlan_pool_queried = res_ops.query_resource(res_ops.L2_VXLAN_NETWORK_POOL, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-L2VxlanNetwotk')
    l2_vxlan_queried = res_ops.query_resource(res_ops.L2_VXLAN_NETWORK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-VniRange')
    vni_range_queried = res_ops.query_resource(res_ops.VNI_RANGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-VPC-Network')
    vpc_network_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)

    if len(resource_stack_queried) == 0:
        test_util.test_fail("Fail to query resource stack")

    if resource_stack_queried[0].status == 'Created':
        if len(vr_image_queried) == 0 or len(vr_offering_queried) == 0 or len(vpc_router_queried) == 0 or len(l2_vxlan_pool_queried) == 0 or len(l2_vxlan_queried) == 0 or len(vni_range_queried) == 0 or len(vpc_network_queried) == 0:
            test_util.test_fail("Fail to create all resource when resource stack status is Created")
    
    
    
    #3.get resource from resource stack
    resource = resource_stack_ops.get_resource_from_resource_stack(resource_stack.uuid)
    if resource == None or len(resource) != 10:
        test_util.test_fail("Fail to get resource from resource_stack")
    
    #4.query event from resource stack
    cond = res_ops.gen_query_conditions('stackUuid', '=', resource_stack.uuid)
    event = res_ops.query_event_from_resource_stack(cond)
    if event == None or len(event) != 26:
        test_util.test_fail("Fail to get event from resource_stack")

    #5.delete resource stack
    resource_stack_ops.delete_resource_stack(resource_stack.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-Vrouter-Image')
    vr_image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-Vrouter-Offering')
    vr_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-VPC-Router')
    vpc_router_queried = res_ops.query_resource(res_ops.VIRTUALROUTER_VM, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-L2VxlanNetwotkPool')
    l2_vxlan_pool_queried = res_ops.query_resource(res_ops.L2_VXLAN_NETWORK_POOL, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-L2VxlanNetwotk')
    l2_vxlan_queried = res_ops.query_resource(res_ops.L2_VXLAN_NETWORK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-VniRange')
    vni_range_queried = res_ops.query_resource(res_ops.VNI_RANGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VPC-VPC-Network')
    vpc_network_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)

    if len(resource_stack_queried) != 0 :
        test_util.test_fail("Fail to delete resource stack") 
    elif len(vr_image_queried) != 0 or len(vr_offering_queried) != 0 or len(vpc_router_queried) != 0 or len(l2_vxlan_pool_queried) != 0 or len(l2_vxlan_queried) != 0 or len(vni_range_queried) != 0 or len(vpc_network_queried) != 0:
        test_util.test_fail("Fail to delete resource when resource stack is deleted")   
   

    test_util.test_pass('Create Resource Stack Test Success')




#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"

