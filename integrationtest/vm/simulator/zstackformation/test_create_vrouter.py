#coding:utf-8
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
    test_util.test_dsc("Test Resource template Apis")

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    bs_queried = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    zone_queried = res_ops.query_resource(res_ops.ZONE, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cluster_queried = res_ops.query_resource(res_ops.CLUSTER, cond)

    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("Create_STACK")
    resource_stack_option.set_rollback("true")
    templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "本示例会创建一个云路由云主机，需要用户提供下面正确的数据i\n公有网络Uuid\n私有网络Uuid: 如果只有公有网络，则把公有网络当作管理网即可.\n",
    "Parameters": {
        "VrouterImageUrl": {
            "Type": "String",
            "Description":"云路由镜像链接地址",
            "DefaultValue": "http://cdn.zstack.io/product_downloads/vrouter/2.3/zstack-vrouter-2.3.2.qcow2"
        },
        "VmImageUrl": {
            "Type": "String",
            "Description":"测试云主机镜像，请确定ZStack 可以下载下面链接的镜像",
            "DefaultValue": "http://cdn.zstack.io/zstack_repo/latest/zstack-image-1.4.qcow2"
        },
        "BackupStorage":{
            "Type": "CommaDelimitedList",
            "Description":"镜像服务器Uuid",
            "DefaultValue": "a61d132738494a11a7cb8fb95a7d00b0"
        },
        "ZoneUuid":{
            "Type": "String",
            "Description":"区域Uuid",
            "DefaultValue": "7c01dc3e9f594b4aac731e5af9cc6653"
        },
        "ClusterUuid":{
            "Type": "String",
            "Description":"集群Uuid",
            "DefaultValue": "9c57b47e547f47569a227e03985203c1"
        },
        "physicalInterface":{
            "Type": "String",
            "DefaultValue":"eth0"
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
            "DefaultValue":"255.255.0.0"
        },
        "Gateway":{
            "Type": "String",
            "DefaultValue":"192.168.0.1"
        },
        "networkCidr":{
            "Type":"String",
            "DefaultValue":"172.20.0.1/8"
        }
    },
    "Resources": {
        "InstanceOffering":{
            "Type":"ZStack::Resource::InstanceOffering",
            "Properties":{
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "1cpu","256M"]]},
                "cpuNum": 1,
                "memorySize" : 268435456
            }
        },
        "L2NoVlanNetwork":{
            "Type":"ZStack::Resource::L2NoVlanNetwork",
            "Properties":{
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "L2NoVlanNetwork"]]},
                "zoneUuid":{"Ref":"ZoneUuid"},
                "physicalInterface":{"Ref":"physicalInterface"}
            }
        },
        "L2VlanNetwork":{
            "Type":"ZStack::Resource::L2VlanNetwork",
            "Properties":{
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "L2VlanNetwork"]]},
                "zoneUuid":{"Ref":"ZoneUuid"},
                "physicalInterface":{"Ref":"physicalInterface"},
                "vlan":1101
            }
        },
        "PublicNetwork":{
            "Type":"ZStack::Resource::L3Network",
            "Properties":{
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "Public-Network"]]},
                "l2NetworkUuid":{"Fn::GetAtt":["L2NoVlanNetwork","uuid"]},
                "category":"Public",
                "type":"L3BasicNetwork"
            }
        },
        "AddIpRange":{
            "Type":"ZStack::Action::AddIpRange",
            "Properties":{
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "iprange"]]},
                "l3NetworkUuid":{"Fn::GetAtt":["PublicNetwork","uuid"]},
                "startIp":{"Ref":"StartIp"},
                "endIp":{"Ref":"EndIp"},
                "netmask":{"Ref":"Netmask"},
                "gateway":{"Ref":"Gateway"}
            }
        },
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
        "VMImage": {
            "Type": "ZStack::Resource::Image",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "VmImage"]]},
                "url": {"Ref":"VmImageUrl"},
                "format": "qcow2",
                "backupStorageUuids":{"Ref":"BackupStorage"}
            }
        },
        "PrivateNetwork":{
            "Type":"ZStack::Resource::L3Network",
            "Properties":{
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "Private-Network"]]},
                "l2NetworkUuid":{"Fn::GetAtt":["L2VlanNetwork","uuid"]},
                "category":"Private",
                "type":"L3BasicNetwork",
                "systemTags":["networkservices::VRouter"]
            }
        },
        "AddIpRangeByNetworkCidr" :{
            "Type":"ZStack::Action::AddIpRangeByNetworkCidr",
            "Properties":{
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "iprange"]]},
                "l3NetworkUuid":{"Fn::GetAtt":["PrivateNetwork","uuid"]},
                "networkCidr":{"Ref":"networkCidr"}
            }
        },
        "VirtualRouterOffering":{
            "Type":"ZStack::Resource::VirtualRouterOffering",
            "Properties":{
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "Vrouter-Offering"]]},
                "zoneUuid":{"Ref":"ZoneUuid"},
                "managementNetworkUuid":{"Fn::GetAtt":["PublicNetwork","uuid"]},
                "publicNetworkUuid":{"Fn::GetAtt":["PublicNetwork","uuid"]},
                "imageUuid":{"Fn::GetAtt":["VrouterImage", "uuid"]},
                "cpuNum":2,
                "memorySize":2147483648,
                "systemTags":[{"Fn::Join": ["::", ["guestL3Network", {"Fn::GetAtt":["PrivateNetwork","uuid"]}]]}]
            }
        },
        "AttachNoVlanNetworkToCluster":{
            "Type":"ZStack::Action::AttachL2NetworkToCluster",
            "Properties":{
                "l2NetworkUuid":{"Fn::GetAtt":["L2NoVlanNetwork","uuid"]},
                "clusterUuid":{"Ref":"ClusterUuid"},
                "systemTags":[{"Fn::Join":["::",["l2NoVlanNetworkUuid",{"Fn::GetAtt":["L2NoVlanNetwork","uuid"]},"clusterUuid",{"Ref":"ClusterUuid"}]]}]
            }
        },
        "AttachVlanNetworkToCluster":{
            "Type":"ZStack::Action::AttachL2NetworkToCluster",
            "Properties":{
                "l2NetworkUuid":{"Fn::GetAtt":["L2VlanNetwork","uuid"]},
                "clusterUuid":{"Ref":"ClusterUuid"},
                "systemTags":[{"Fn::Join":["::",["l2VlanNetworkUuid",{"Fn::GetAtt":["L2VlanNetwork","uuid"]},"clusterUuid",{"Ref":"ClusterUuid"}]]}]
            }
        },
        "TestVm":{
            "Type":"ZStack::Resource::VmInstance",
            "Properties":{
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "TestVm"]]},
                "instanceOfferingUuid": {"Fn::GetAtt":["InstanceOffering","uuid"]},
                "l3NetworkUuids": [{"Fn::GetAtt":["PrivateNetwork","uuid"]}],
                "imageUuid": {"Fn::GetAtt":["VMImage", "uuid"]}
            }
        }
    },
    "Outputs": {
        "vyos": {
            "Value": {
                "Ref": "TestVm"
            }
        }
    }
}
'''
    #1.create resource stack
    parameter = '{"BackupStorage":"%s","ZoneUuid":"%s","ClusterUuid":"%s"}' % (bs_queried[0].uuid, zone_queried[0].uuid, cluster_queried[0].uuid)
    resource_stack_option.set_templateContent(templateContent)
    resource_stack_option.set_parameters(parameter)
    preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)
    resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)

    #2.query resource stack
    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Vrouter-Image')
    vr_image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Vrouter-Offering')
    vr_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)

    cond = res_ops.gen_query_conditions('applianceVmType', '=', 'vrouter')
    vrouter_queried = res_ops.query_resource(res_ops.VIRTUALROUTER_VM, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-L2VlanNetwork')
    l2_vlan_queried = res_ops.query_resource(res_ops.L2_VLAN_NETWORK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-L2NoVlanNetwork')
    l2_queried = res_ops.query_resource(res_ops.L2_NETWORK, cond)

    if len(resource_stack_queried) == 0:
        test_util.test_fail("Fail to query resource stack")

    if resource_stack_queried[0].status == 'Created':
        if len(vr_image_queried) == 0 or len(vr_offering_queried) == 0 or len(vrouter_queried) == 0 or len(l2_queried) == 0 or len(l2_vlan_queried) == 0:
            test_util.test_fail("Fail to create all resource when resource stack status is Created")

    #3.get resource from resource stack
    resource = resource_stack_ops.get_resource_from_resource_stack(resource_stack.uuid)
    if resource == None or len(resource) != 9:
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

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Vrouter-Image')
    vr_image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Vrouter-Offering')
    vr_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)

    cond = res_ops.gen_query_conditions('applianceVmType', '=', 'vrouter')
    vrouter_queried = res_ops.query_resource(res_ops.VIRTUALROUTER_VM, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-L2NoVlanNetwork')
    l2_queried = res_ops.query_resource(res_ops.L2_NETWORK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-L2VlanNetwork')
    l2_vlan_queried = res_ops.query_resource(res_ops.L2_VLAN_NETWORK, cond)

    if len(resource_stack_queried) != 0 :
        test_util.test_fail("Fail to delete resource stack") 
    elif len(vr_image_queried) != 0 or len(vr_offering_queried) != 0 or len(vrouter_queried) != 0 or len(l2_queried) != 0 or len(l2_vlan_queried) != 0:
        test_util.test_fail("Fail to delete resource when resource stack is deleted")   
   

    test_util.test_pass('Create Resource Stack Test Success')




#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"



