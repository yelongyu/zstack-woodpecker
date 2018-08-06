#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Create a public network and check the networkserives.
Cover bug13966

@author: chenyuan.xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
    test_util.test_dsc("Test Resource template Apis")

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
    "Description": "",
    "Parameters": {
        "ZoneUuid": {
            "Label":"区域",
            "Type": "String",
            "DefaultValue":""
        },
        "ClusterUuid": {
            "Label": "集群",
            "Type": "String",
            "DefaultValue": ""
        }
    },    
    "Resources": {
        "L2_NETWORK": {
            "Type": "ZStack::Resource::L2VlanNetwork",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "L2Network"]]},
                "type": "vlan",
                "zoneUuid": {"Ref":"ZoneUuid"},
                "physicalInterface": "eth0",
                "vlan": 66
            }
        },
        "AttachL2NetworkToCluster-L2_NETWORK": {
            "Type": "ZStack::Action::AttachL2NetworkToCluster",
            "Properties": {
                "l2NetworkUuid": {
                    "Fn::GetAtt": [
                        "L2_NETWORK",
                        "uuid"
                    ]
                },
                "clusterUuid": {"Ref":"ClusterUuid"}
            }
        },
        "PUBLIC_NETWORK": {
            "Type": "ZStack::Resource::L3Network",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"}, "PublicNetwork"]]},
                "type": "L3BasicNetwork",
                "l2NetworkUuid": {
                    "Fn::GetAtt": [
                        "L2_NETWORK",
                        "uuid"
                    ]
                },
                "system": false,
                "category": "Public",
                "systemTags": [
                    "networkservices::Public"
                ]
            },
            "DependsOn": [
                "AttachL2NetworkToCluster-L2_NETWORK"
            ]
        },
        "AddIpRangeByNetworkCidr-PUBLIC_NETWORK": {
            "Type": "ZStack::Action::AddIpRangeByNetworkCidr",
            "Properties": {
                "name": "Iprange",
                "networkCidr": "10.100.88.0/8",
                "l3NetworkUuid": {
                    "Fn::GetAtt": [
                        "PUBLIC_NETWORK",
                        "uuid"
                    ]
                }
            }
        }
    }
}
'''
    parameter = '{"ZoneUuid":"%s","ClusterUuid":"%s"}' % (zone_queried[0].uuid, cluster_queried[0].uuid)
    
    resource_stack_option.set_templateContent(templateContent)
    resource_stack_option.set_parameters(parameter)
    preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)
    resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)
    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-PublicNetwork')
    public_network_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    cond = res_ops.gen_query_conditions('l3NetworkUuid', '=', public_network_queried[0].uuid)
    networkservices_queried = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER_L3_REF, cond)
    if resource_stack_queried[0].status == 'Created':
    	if len(networkservices_queried) == 0:
    	    test_util.test_fail("Failed to attach networkservices to l3 network.")
        elif 'Userdata' not in [service.networkServiceType for service in public_network_queried[0].networkServices]:
            test_util.test_fail("Userdata services has not been added successfully.")
        elif 'DHCP' not in [service.networkServiceType for service in public_network_queried[0].networkServices]:
            test_util.test_fail("DHCP services has not been added successfully.")
        elif 'SecurityGroup' not in [service.networkServiceType for service in public_network_queried[0].networkServices]:
            test_util.test_fail("SecurityGroup services has not been added successfully.")
 
    test_util.test_pass('Create Resource Stack Test Success')




#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"




    
