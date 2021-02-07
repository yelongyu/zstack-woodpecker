#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Create a resource stack with the wrong parameters.
Cover bug13974

@author: chenyuan.xu
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
    cond = res_ops.gen_query_conditions('networkServices.networkServiceType', '=', 'LoadBalancer')
    l3_pri_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('type', '=', 'UserVm', cond)
    instance_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)

    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("Create_STACK")
    templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "",
    "Parameters": {
        "PrivateNetworkUuid": {
            "Type": "String",
            "Label": "私有网络"
        },
        "PublicNetworkUuid":{
            "Type": "String",
            "Label": "公有网络"
        },
        "InstanceOfferingUuid": {
            "Type": "String",
            "Label": "计算规格"
        },
        "ImageUuid": {
            "Type": "String",
            "Label": "镜像"
        }
    },
    "Resources": {
        "VM": {
            "Type": "ZStack::Resource::VmInstance",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"VM"]]},
                "description": "",
                "instanceOfferingUuid": {"Ref":"InstanceOfferingUuid"},
                "imageUuid": {"Ref":"ImageUuid"},
                "l3NetworkUuids": [
                    {"Ref":"PrivateNetworkUuid"}
                ],
                "defaultL3NetworkUuid": {"Ref":"PrivateNetworkUuid"},
                "dataDiskOfferingUuids": [],
                "systemTags": [
                    "usbRedirect::false",
                    "vmConsoleMode::vnc"
                ]
            }
        },
        "LOAD_BALANCER": {
            "Type": "ZStack::Resource::LoadBalancer",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"LB"]]},
                "vipUuid": {
                    "Fn::GetAtt": [
                        "LOAD_BALANCER",
                        "uuid"
                    ]
                }
            }
        },
        "VIP-LOAD_BALANCER": {
            "Type": "ZStack::Resource::Vip",
            "Properties": {
                "name": "{"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"VIP"]]}",
                "l3NetworkUuid": {"Ref":"PublicNetworkUuid"}
            }
        },
        "LISTENER": {
            "Type": "ZStack::Resource::LoadBalancerListener",
            "Properties": {
                "name": "{"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"LBL"]]}",
                "protocol": "tcp",
                "loadBalancerPort": 22,
                "instancePort": 22,
                "loadBalancerUuid": {
                    "Fn::GetAtt": [
                        "LOAD_BALANCER",
                        "uuid"
                    ]
                },
                "systemTags": [
                    "balancerAlgorithm::roundrobin",
                    "connectionIdleTimeout::60",
                    "healthyThreshold::2",
                    "unhealthyThreshold::2",
                    "healthCheckInterval::5",
                    "maxConnection::5000"
                ]
            }
        },
        "AddVmNicToLoadBalancer": {
            "Type": "ZStack::Action::AddVmNicToLoadBalancer",
            "Properties": {
                "vmNicUuids": [
                    {
                        "Fn::GetAtt": [
                            {
                                "Fn::Select": [
                                    0,
                                    {
                                        "Fn::GetAtt": [
                                            "VM",
                                            "vmNics"
                                        ]
                                    }
                                ]
                            },
                            "uuid"
                        ]
                    }
                ],
                "listenerUuid": {
                    "Fn::GetAtt": [
                        "LISTENER",
                        "uuid"
                    ]
                }
            }
        }
    }
}
'''
    #1.create resource stack 
    parameter = '{"PrivateNetworkUuid":"%s","PublicNetworkUuid":"%s","ImageUuid":"%s","InstanceOfferingUuid":"%s"}' % (l3_pri_queried[0].uuid, l3_pub_queried[0].uuid, image_queried[0].uuid, instance_offering_queried[0].uuid)
    resource_stack_option.set_templateContent(templateContent)
    resource_stack_option.set_parameters(parameter)
    try:
        preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)
    except:
        pass
    else:
        test_util.test_fail('Preview resource stack successfully with wrong parameter.')

    try:
        resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)
    except:
        pass
    else:
        test_util.test_fail('Create resource stack successfully with wrong parameter.')

    # 2.query resource stack
    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK')
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VM')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VIP')
    vip_queried = res_ops.query_resource(res_ops.VIP, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-LB')
    lb_queried = res_ops.query_resource(res_ops.LOAD_BALANCER, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-LBL')
    lbl_queried = res_ops.query_resource(res_ops.LOAD_BALANCER_LISTENER, cond)

    if len(resource_stack_queried) != 0:
        if len(vm_queried) == 0 or len(vip_queried) == 0 or len(lb_queried) == 0 or len(lbl_queried) == 0:
            test_util.test_fail("Fail to delete resources.")


#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"
