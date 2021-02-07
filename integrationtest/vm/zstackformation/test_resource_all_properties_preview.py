#coding:utf-8
'''

New Integration Test for creating KVM VM.

@author: Lei Liu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.stack_template as stack_template_ops
#import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations
#import time

def test():
    test_util.test_dsc("Test Stack template Apis")
    
    cond = res_ops.gen_query_conditions('name', '=', "test")
    stack_template_queried = res_ops.query_resource(res_ops.STACK_TEMPLATE, cond)
    if len(stack_template_queried) !=0:
      stack_template_ops.delete_stack_template(stack_template_queried[0].uuid)

    stack_template_option = test_util.StackTemplateOption()
    stack_template_option.set_name("test")
    templateContent = '''
{
  "ZStackTemplateFormatVersion": "2018-06-18",
  "Description": "Test ZStack formation functions",
  "Parameters": {
    "4TestBoolean2": {
      "Type": "Boolean",
      "Description": "测试boolean ",
      "DefaultValue": false
    },
    "ZoneUuid": {
      "Type": "String",
      "Description": "测试boolean ",
      "DefaultValue": "zoneuuid"
    },
    "ClusterUuid": {
      "Type": "String",
      "DefaultValue": "clusteruuid"
    },
    "PrimaryStorageUuidForRootVolume": {
      "Type": "String",
      "Description": "主存储Uuid ",
      "DefaultValue": "primarystorageuuidforrootvolume"
    },
    "ImageUrl": {
      "Type": "String",
      "Description": "镜像地址",
      "DefaultValue": "http://test.zss.com/testimage.qcow2"
    },
    "BackupStorages": {
      "Type": "CommaDelimitedList",
      "Description": "所有镜像服务器",
      "DefaultValue": "BS1,BS2,BS3"
    },
    "Vlan": {
      "Type": "Number",
      "Description": "Vlan id",
      "DefaultValue": 1000
    },
    "VipPortStart": {
      "Type": "Number",
      "Description": "Vip port start num",
      "DefaultValue": 22
    },
    "LoadBalancerPort": {
      "Type": "Number",
      "Description": "load balancer port",
      "DefaultValue": 443
    },
    "PeerAddress": {
      "Type": "String",
      "DefaultValue": "192.168.200.100"
    },
    "AuthKey": {
      "Type": "String",
      "DefaultValue": "testAuthKey"
    },
    "L2Interface": {
      "Type": "String",
      "DefaultValue": "eth0"
    },
    "StartIp":{
      "Type":"String",
      "DefaultValue":"192.168.200.2"
    },
    "EndIp":{
      "Type":"String",
      "DefaultValue":"192.168.200.200"
    },
    "Netmask":{
      "Type":"String",
      "DefaultValue":"255.255.255.0"
    },
    "Gateway":{
      "Type":"String",
      "DefaultValue":"192.268.200.1"
    },
    "Dns":{
      "Type":"String",
      "DefaultValue":"114.114.114.114"
    },
    "NetworkCidr":{
      "Type":"String",
      "DefaultValue":"192.168.10.0/24"
    },
    "Destination":{
      "Type":"String",
      "DefaultValue":"192.168.2.0/24"
    },
    "Prefix":{
      "Type":"String",
      "DefaultValue":"169.254.169.254/32"
    },
    "Nexthop":{
      "Type":"String",
      "DefaultValue":"192.168.1.254"
    },
    "UsbDeviceUuid":{
      "Type":"String",
      "DefaultValue":"usbDeviceUuid"
    },
    "PciDeviceUuid":{
      "Type":"String",
      "DefaultValue":"pciDeviceUuid"
    }
  },
  "Mappings": {
    "names": {
      "instanceOffering": {
        "name1": "test-just-t",
        "name2": "test2"
      }
    },
    "JustForTest": {
      "test": "I am valid!"
    },
    "JustForTest2": {
      "test": "I am valid!",
      "test2": "I am valid too!"
    }
  },
  "Resources": {
    "InstanceOffering": {
      "Type": "ZStack::Resource::InstanceOffering",
      "Properties": {
        "name": {
          "Fn::Join": [
            "-",
            [
              "a",
              "b",
              "ccc"
            ]
          ]
        },
        "description":"测试创建计算规格",
        "cpuNum": 8,
        "memorySize": 8589934592,
        "allocatorStrategy":"Mevoco",
        "resourceUuid":"testuuid",
        "sortKey":0,
        "systemTags": [
          "userdata"
        ],
        "userTags": [
          "中文",
          "testinstanceofferingusertag"
        ],
        "type":"UserVm",
        "timeout":600
      }
    },
    "DiskOffering": {
      "Type": "ZStack::Resource::DiskOffering",
      "Properties": {
        "name": "diskoffering",
        "diskSize": 1124774006935781000,
        "sortKey": 1,
        "allocationStrategy": "DefaultPrimaryStorageAllocationStrategy",
        "resourceUuid": "DefaultDiskOfferingType",
        "type": "DefaultDiskOfferingType",
        "timeout":100,
        "systemTags": [
          "test",
          "ttt"
        ],
        "userTags": [
          "中文",
          "testdiskofferingusertag"
        ]
      }
    },
    "VM": {
      "Type": "ZStack::Resource::VmInstance",
      "Properties": {
        "name": {
          "Fn::Base64": "kubernetes-Node-1"
        },
        "instanceOfferingUuid": {
          "Fn::GetAtt": [
            "InstanceOffering",
            "uuid"
          ]
        },
        "imageUuid": {
          "Fn::FindInMap": [
            "names",
            "instanceOffering",
            "name1"
          ]
        },
        "l3NetworkUuids": ["1","2"],
        "rootDiskOfferingUuid": {
          "Fn::GetAtt": [
            "DiskOffering",
            "uuid"
          ]
        },
        "dataDiskOfferingUuids": [
          "uuid1",
          "uuid2"
        ],
        "zoneUuid": {
          "Ref": "ZoneUuid"
        },
        "clusterUuid": {
          "Ref": "ClusterUuid"
        },
        "hostUuid": "hostuuid",
        "primaryStorageUuidForRootVolume": {
          "Ref": "PrimaryStorageUuidForRootVolume"
        },
        "description": "创建一个云主机··‘’“''、$# $?",
        "defaultL3NetworkUuid": "uuid",
        "strategy":"InstantStart",
        "timeout":300,
        "systemTags": [
          "userdata"
        ],
        "userTags": [
          "Test",
          "test2",
          "中文试一下;"
        ]
      },
      "DependsOn": [
        {
          "Ref": "InstanceOffering"
        }
      ],
      "DeletionPolicy": "Retain"
    },
   "DataVolume": {
    "Type": "ZStack::Resource::DataVolume",
    "Properties": {
        "name": "testDataVolume",
        "description": "创建一个云盘！！！",
        "diskOfferingUuid": {
            "Fn::GetAtt": [
                "DiskOffering",
                "uuid"
            ]
        },
        "primaryStorageUuid": {
            "Ref": "PrimaryStorageUuidForRootVolume"
        },
        "resourceUuid": "uuid",
        "timeout": 100,
        "systemTags": [
            "test",
            "ttt"
        ],
        "userTags": [
            "Test",
            "test2",
            "中文试一下;"
        ]
      }
    },
    "Image": {
      "Type": "ZStack::Resource::Image",
      "Properties": {
        "name": "testimage",
        "description": "添加镜像，‘’‘’“”",
        "url": {
          "Ref": "ImageUrl"
        },
        "mediaType": "ISO",
        "guestOsType": "Linux",
        "system": false,
        "format": "qcow2",
        "platform": "Linux",
        "mediaType": "RootVolumeTemplate",
        "backupStorageUuids": {
          "Ref": "BackupStorages"
        },
        "resourceUuid": "testuuid",
        "timeout":600,
        "systemTags": [
          "imagesystemtags",
          "imagestsytemtages2"
        ],
        "userTags": [
          "imageusertages1",
          "imageusertages2",
          "中文试一下"
        ]
      }
    },
    "AffinityGroup": {
      "Type": "ZStack::Resource::AffinityGroup",
      "Properties": {
        "name": "testAffinityGroup",
        "description":"create one 亲和组 ",
        "policy": "antiSoft",
        "type": "host",
        "resourceUuid": "affinitygroupuuid",
        "timeout": 100,
        "systemTags": ["testsystemTags"],
        "userTags": ["用户标签"]
      }
    },
    "L2VxlanNetworkPool": {
      "Type": "ZStack::Resource::L2VxlanNetworkPool",
      "Properties": {
        "name": "testl2vxlannetworkpool",
        "description":"一个vxlanpool",
        "type":"test",
        "zoneUuid": {
          "Ref": "ZoneUuid"
        },
        "physicalInterface": {
          "Ref": "L2Interface"
        },
        "timeout":100,
        "resourceUuid": "testl2vxlannetworkpooluuid",
        "systemTags": [
          "l2vxlanpoolsystemtags",
          "l2vxlanpoolsystemtages2"
        ],
        "userTags": [
          "l2vxlanpoolsertages1",
          "l2vxlanpoolertages2",
          "中文试一下;"
        ]
      }
    },
    "L2NoVlanNetwork": {
      "Type": "ZStack::Resource::L2NoVlanNetwork",
      "Properties": {
        "name": "testl2novlannetwork",
        "description": "Novlan 二层网络",
        "resourceUuid":"testuuid",
        "zoneUuid": {
          "Ref": "ZoneUuid"
        },
        "physicalInterface": "eth0",
        "type":"test",
        "timeout":200,
        "systemTags": [
          "l2novlansystemtags",
          "l2novlansystemtages2"
        ],
        "userTags": [
          "l2novlansertages1",
          "l2novlanpoolertages2",
          "中文试一下;"
        ]
      }
    },
    "L2VlanNetwork": {
      "Type": "ZStack::Resource::L2VlanNetwork",
      "Properties": {
        "name": "testl2vlannetwork",
        "description":"l2vlannetwork",
        "resourceUuid":"testuuid",
        "zoneUuid": {
          "Ref": "ZoneUuid"
        },
        "physicalInterface": {
          "Ref": "L2Interface"
        },
        "timeout":100,
        "systemTags": [
          "l2vlansystemtags",
          "l2vlansystemtages2"
        ],
        "userTags": [
          "l2vlansertages1",
          "l2vlanpoolertages2",
          "中文试一下;"
        ]
      }
    },
    "L2VxlanNetwork": {
      "Type": "ZStack::Resource::L2VxlanNetwork",
      "Properties": {
        "name": "testl2vxlannetwork",
        "description":"vxlannetwork",
        "resourceUuid":"testuuid",
        "type":"test",
        "zoneUuid": {
          "Ref": "ZoneUuid"
        },
        "physicalInterface": {
          "Ref": "L2Interface"
        },
        "timeout":100,
        "systemTags": [
          "l2vxlansystemtags",
          "l2vxlansystemtages2"
        ],
        "userTags": [
          "l2vxlansertages1",
          "l2vxlanpoolertages2",
          "中文试一下;"
        ]
      }
    },
    "L3Network": {
      "Type": "ZStack::Resource::L3Network",
      "Properties": {
        "name": "testl3network",
        "description": "l3network",
        "dnsDomain": "8.8.8.8",
        "l2NetworkUuid": "uuid",
        "resourceUuid":"testuuid",
        "system":false,
        "type":"L3BasicNetwork",
        "category":"Private",
        "timeout":100,
        "systemTags": [
          "l2vxlansystemtags",
          "l2vxlansystemtages2"
        ],
        "userTags": [
          "l2vxlansertages1",
          "l2vxlanpoolertages2",
          "中文试一下;"
        ]
      }
    },
    "VRouterRouteTable": {
      "Type": "ZStack::Resource::VRouterRouteTable",
      "Properties": {
        "name": "testVrouterRouTable",
        "description": "VrouterRouteTable",
        "resourceUuid": "testuuid",
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]


      }
    },
    "VpcVRouter": {
      "Type": "ZStack::Resource::VpcVRouter",
      "Properties": {
        "name": "testvpcvrouter",
        "description": "vpc vrouter",
        "virtualRouterOfferingUuid": "Todo",
        "resourceUuid":"uuid",
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    },
    "SecurityGroup": {
      "Type": "ZStack::Resource::SecurityGroup",
      "Properties": {
        "name": "testsecurityGroup",
        "description": "安全组",
        "resourceUuid": "testuuid",
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    },
    "SecurityGroupRule": {
      "Type": "ZStack::Resource::SecurityGroupRule",
      "Properties": {
        "remoteSecurityGroupUuids":["remotesguuid"],
        "securityGroupUuid": "sguuid",
        "rules":["rule1"],
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    },
    "Vip": {
      "Type": "ZStack::Resource::Vip",
      "Properties": {
        "name": "testvip",
        "description": "vip",
        "allocatorStrategy":"Random",
        "l3NetworkUuid": {
          "Fn::GetAtt": [
            "L3Network",
            "uuid"
          ]
        },
        "requiredIp":"10.141.23.21",
        "resourceUuid": "testuuid",
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    },
    "Eip": {
      "Type": "ZStack::Resource::Eip",
      "Properties": {
        "name": "testeip",
        "description": "eip",
        "vipUuid": {
          "Fn::GetAtt": [
            "Vip",
            "uuid"
          ]
        },
        "resourceUuid": "testuuid",
        "vmNicUuid":"vmNicUuid",
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    },
    "PortForwardingRule": {
      "Type": "ZStack::Resource::PortForwardingRule",
      "Properties": {
        "name": "testPortForwardingRule",
        "description": "pf",
        "allowedCidr": "192.168.24.0/24",
        "vipUuid": {
          "Fn::GetAtt": [
            "Vip",
            "uuid"
          ]
        },
        "protocolType": "TCP",
        "vipUuid": "vipuuid",
        "vmNicUuid": "vmnicuuid",
        "resourceUuid": "testuuid",
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    },
    "LoadBalancer": {
      "Type": "ZStack::Resource::LoadBalancer",
      "Properties": {
        "name": "testLoadBalancer",
        "description":"lb",
        "resourceUuid":"testuuid",
        "vipUuid": {
          "Fn::GetAtt": [
            "Vip",
            "uuid"
          ]
        },
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    },
    "LoadBalancerListener": {
      "Type": "ZStack::Resource::LoadBalancerListener",
      "Properties": {
        "name": "testLocaBalancerListerner",
        "description":"lbl",
        "loadBalancerUuid": {
          "Fn::GetAtt": [
            "LoadBalancer",
            "uuid"
          ]
        },
        "loadBalancerPort": {
          "Ref": "LoadBalancerPort"
        },
        "protocol":"TCP",
        "resourceUuid":"testuuid",
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    },
    "IPsecConnection": {
      "Type": "ZStack::Resource::IPsecConnection",
      "Properties": {
        "name": "testIPsecConnection",
        "description":"IPsec",
        "peerAddress": {
          "Ref": "PeerAddress"
        },
        "authKey": {
          "Ref": "AuthKey"
        },
        "vipUuid": {
          "Fn::GetAtt": [
            "Vip",
            "uuid"
          ]
        },
        "l3NetworkUuid":"l3uuid",
        "peerCidrs":["192.168.100.0/24"],
        "authMode":"psk",
        "ikeAuthAlgorithm":"sha1",
        "ikeEncryptionAlgorithm":"aes-128",
        "ikeDhGroup":2,
        "policyAuthAlgorithm":"sha1",
        "policyEncryptionAlgorithm":"aes-128",
        "policyMode":"tunnel",
        "pfs":"pfs",
        "resourceUuid":"testuuid",
        "transformProtocol":"esp",
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    },
    "VirtualRouterOffering": {
      "Type": "ZStack::Resource::VirtualRouterOffering",
      "Properties": {
        "name": "virtualrouteroffering",
        "description":"vr-offering",
        "resourceUuid":"testuuid",
        "allocatorStrategy":"Mevoco",
        "cpuNum":2,
        "imageUuid":"imageuuid",
        "isDefault":false,
        "managementNetworkUuid":"mnnetworkUuid",
        "memorySize":1124774006935781000,
        "publicNetworkUuid":"pubuuid",
        "sortKey":1,
        "type":"ApplianceVm",
        "zoneUuid":"zoneuuid",
        "timeout": 100,
        "systemTags":["test"],
        "userTags":["test"]
      }
    }
    

  },
  "Outputs": {
    "InstanceOffering": {
      "Value": {
        "Ref": "InstanceOffering"
      }
    },
    "IP": {
      "Value": {
        "Fn::Select": [
          "0",
          [
            "ip",
            "11",
            "test"
          ]
        ]
      }
    }
  }
}


'''
    parameter = '''
{
    "TestStringBasicEcho": "Just a string Possiple"
}
'''

    stack_template_option.set_templateContent(templateContent)
    #preview_resource_stack = resource_stack_ops.preview_resource_stack(stack_template_option)
    try:
      preview_resource_stack(templateContent, parameter)
    except:
      test_util.test_fail('error')


    stack_template = stack_template_ops.add_stack_template(stack_template_option)

    cond = res_ops.gen_query_conditions('uuid', '=', stack_template.uuid)
    stack_template_queried = res_ops.query_resource(res_ops.STACK_TEMPLATE, cond)
    if len(stack_template_queried) == 0:
        test_util.test_fail("Fail to query stack template")
    #Add a template via text.

#     newTemplateContent = '''
# {
#     "ZStackTemplateFormatVersion": "2018-06-18",
#     "Description":"test",
#     "Parameters": {
#             "TestJsonEcho": {
#             "Type": "Json",
#             "Description":"测试 Json",
#              "DefaultValue": {"menu": {
#                           "id": "file",
#                           "value": "File",
#                           "popup": {
#                             "menuitem": [
#                               {"value": "New", "onclick": "CreateNewDoc()"},
#                               {"value": "Open", "onclick": "OpenDoc()"},
#                               {"value": "Close", "onclick": "CloseDoc()"}
#                             ]
#                           }
#                         }}
#                 }
#         },
#     "Resources": {
#         "InstanceOffering": {
#             "Type": "ZStack::Resource::InstanceOffering",
#             "Properties": {
#                 "name": "8cpu-8g",
#                 "cpuNum": 8,
#                 "memorySize": {"Ref":"TestNumberMaxEcho"}
#             }
#         }
#     },
#     "Outputs": {
#         "InstanceOffering": {
#             "Value": {
#                 "Ref": "InstanceOffering"
#             }
#         }
#     }
# }
# '''

#     stack_template_option.set_templateContent(newTemplateContent)
#     stack_template_option.set_name("newname")

#     new_stack_template = stack_template_ops.update_stack_template(stack_template.uuid, stack_template_option)

#     if new_stack_template.name != "newname":
#         test_util.test_fail("Fail to update stack template name")
    
#     stack_template_ops.delete_stack_template(stack_template.uuid)

#     stack_template_queried = res_ops.query_resource(res_ops.STACK_TEMPLATE, cond)
#     if len(stack_template_queried) != 0:
#         test_util.test_fail("Fail to query stack template")

    test_util.test_pass('Create Stack Template Test Success')

#Will be called only if exception happens in test().
def preview_resource_stack(templateContent, parameters, session_uuid=None):
    action = api_actions.PreviewResourceStackAction()
    #action.type = resource_stack_option.get_type()
    action.parameters = parameters
    action.templateContent = templateContent
    #action.uuid = resource_stack_option.get_uuid()
    test_util.action_logger('Preview Resource Stack template')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def error_cleanup():
    print "Ignore cleanup"
