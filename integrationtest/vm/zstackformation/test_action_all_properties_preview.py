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
      "DefaultValue":"198.168.0.1"
    },
    "Dns":{
      "Type":"String",
      "DefaultValue":"114.114.114.114"
    },
    "NetworkCidr":{
      "Type":"String",
      "DefaultValue":"192.168.10.0/24"
    },
    "PeerCidrs":{
      "Type": "CommaDelimitedList",
      "Description": "PeerCidra",
      "DefaultValue": "192.168.23.0/24"
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
    "L3Network":{
      "Type":"ZStack::Resource::L3Network",
      "Properties":{
        "name":"testl3network",
        "l2NetworkUuid":"uuid"
      }
    },
    "VRouterRouteTable":{
      "Type":"ZStack::Resource::VRouterRouteTable",
      "Properties":{
        "name":"testVrouterRouTable"
      }
    },
    "SecurityGroup":{
      "Type":"ZStack::Resource::SecurityGroup",
      "Properties":{
        "name":"testsecurityGroup"
      }
    },
    "LoadBalancer":{
      "Type":"ZStack::Resource::LoadBalancer",
      "Properties":{
        "name":"testLoadBalancer",
        "vipUuid":{"Fn::GetAtt":["Vip","uuid"]}
      }
    },
    "LoadBalancerListener":{
      "Type":"ZStack::Resource::LoadBalancerListener",
      "Properties":{
        "name":"testLocaBalancerListerner",
        "loadBalancerUuid":{"Fn::GetAtt":["LoadBalancer","uuid"]},
        "loadBalancerPort": {"Ref":"LoadBalancerPort"}
      }
    },
    "PortForwardingRule":{
      "Type":"ZStack::Resource::PortForwardingRule",
      "Properties":{
        "name":"testPortForwardingRule",
        "vipUuid":{"Fn::GetAtt":["Vip","uuid"]},
        "vipPortStart":{"Ref":"VipPortStart"},
        "protocolType":"TCP"
      }
    },
    "Vip":{
      "Type":"ZStack::Resource::Vip",
      "Properties":{
        "name":"testvip",
        "l3NetworkUuid":{"Fn::GetAtt":["L3Network","uuid"]}
      }
    },
    "Eip":{
      "Type":"ZStack::Resource::Eip",
      "Properties":{
        "name":"testeip",
        "vipUuid":{"Fn::GetAtt":["Vip","uuid"]}
      }
    },
    "IPsecConnection": {
      "Type":"ZStack::Resource::IPsecConnection",
      "Properties":{
        "name":"testIPsecConnection",
        "peerAddress":{"Ref":"PeerAddress"},
        "authKey":{"Ref":"AuthKey"},
        "vipUuid":{"Fn::GetAtt":["Vip","uuid"]}
      }
    },
    "AddIpRange":{
      "Type":"ZStack::Action::AddIpRange",
      "Properties":{
        "l3NetworkUuid":{"Fn::GetAtt":["L3Network","uuid"]},
        "name":"TestIpRange",
        "description":"iprange",
        "startIp":"192.168.23.1",
        "endIp":{"Ref":"EndIp"},
        "netmask":{"Ref":"Netmask"},
        "gateway":{"Ref":"Gateway"},
        "resourceUuid":"testuuid",
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AddDnsToL3Network":{
      "Type":"ZStack::Action::AddDnsToL3Network",
      "Properties":{
         "l3NetworkUuid":{"Fn::GetAtt":["L3Network","uuid"]},
         "dns":{"Ref":"Dns"},
         "timeout":200,
         "systemTags": ["test"],
         "userTags": ["test"]
      }
    },
    "AddSecurityGroupRule":{
      "Type":"ZStack::Action::AddSecurityGroupRule",
      "Properties":{
        "securityGroupUuid":{"Fn::GetAtt":["SecurityGroup","uuid"]},
        "rules":[
        {
          "type":"Ingress",
          "startPort":22,
          "endPort":22,
          "protocol":"TCP",
          "allowedCidr":"0.0.0.0/0"
        }
        ],
        "remoteSecurityGroupUuids":["testuuid"],
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AddVmToAffinityGroup":{
      "Type":"ZStack::Action::AddVmToAffinityGroup",
      "Properties":{
        "affinityGroupUuid":{"Fn::GetAtt":["AffinityGroup","uuid"]},
        "uuid":{"Fn::GetAtt":["VM","uuid"]},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AddVRouterRouteEntry":{
      "Type":"ZStack::Action::AddVRouterRouteEntry",
      "Properties":{
        "routeTableUuid":{"Fn::GetAtt":["VRouterRouteTable","uuid"]},
        "destination":{"Ref":"Destination"},
        "type":"UserStatic",
        "routeTableUuid":"routeTableUuid",
        "description":"test",
        "target":"10.141.23.2",
        "distance":1,
        "resourceUuid":"testuuid",
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AddIpRangeByNetworkCidr":{
      "Type":"ZStack::Action::AddIpRangeByNetworkCidr",
      "Properties":{
        "name":"Test-IpRange",
        "description":"111",
        "l3NetworkUuid":{"Fn::GetAtt":["L3Network","uuid"]},
        "networkCidr":{"Ref":"NetworkCidr"},
        "resourceUuid":"addiprangeuuid",
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AddVmNicToLoadBalancer":{
      "Type":"ZStack::Action::AddVmNicToLoadBalancer",
      "Properties":{
        "vmNicUuids":["testuuid"],
        "listenerUuid":{"Fn::GetAtt":["LoadBalancerListener","uuid"]},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AddVmNicToSecurityGroup":{
      "Type":"ZStack::Action::AddVmNicToSecurityGroup",
      "Properties":{
        "securityGroupUuid":{"Fn::GetAtt":["SecurityGroup","uuid"]},
        "vmNicUuids":["testuuid"],
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AddRemoteCidrsToIPsecConnection":{
      "Type":"ZStack::Action::AddRemoteCidrsToIPsecConnection",
      "Properties":{
        "uuid":{"Fn::GetAtt":["IPsecConnection","uuid"]},
        "peerCidrs":{"Ref":"PeerCidrs"},
        "resourceUuid":"addiprangeuuid",
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]

      }
    },
    "AttachEip":{
      "Type":"ZStack::Action::AttachEip",
      "Properties":{
        "eipUuid":{"Fn::GetAtt":["Eip","uuid"]},
        "vmNicUuid":"testuuid",
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AttachDataVolumeToVm":{
      "Type":"ZStack::Action::AttachDataVolumeToVm",
      "Properties":{
        "vmInstanceUuid":{"Fn::GetAtt":["VM","uuid"]},
        "volumeUuid":{"Fn::GetAtt":["DataVolume","uuid"]},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AttachPortForwardingRule":{
      "Type":"ZStack::Action::AttachPortForwardingRule",
      "Properties":{
        "ruleUuid":{"Fn::GetAtt":["PortForwardingRule","uuid"]},
        "vmNicUuid":{"Fn::Select": ["0", ["foo; bar; achoo"]]},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]

      }
    },
    "AttachIsoToVmInstance":{
      "Type":"ZStack::Action::AttachIsoToVmInstance",
      "Properties":{
        "vmInstanceUuid":{"Fn::GetAtt":["VM","uuid"]},
        "isoUuid":"isouuid",
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AttachPciDeviceToVm":{
      "Type":"ZStack::Action::AttachPciDeviceToVm",
      "Properties":{
        "pciDeviceUuid":{"Ref":"PciDeviceUuid"},
        "vmInstanceUuid":{"Fn::GetAtt":["VM","uuid"]},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AttachUsbDeviceToVm":{
      "Type":"ZStack::Action::AttachUsbDeviceToVm",
      "Properties":{
        "usbDeviceUuid":{"Ref":"UsbDeviceUuid"},
        "vmInstanceUuid":{"Fn::GetAtt":["VM","uuid"]},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AttachL2NetworkToCluster":{
      "Type":"ZStack::Action::AttachL2NetworkToCluster",
      "Properties":{
        "l2NetworkUuid":{"Fn::GetAtt":["L2NoVlanNetwork","uuid"]},
        "clusterUuid":{"Ref":"ClusterUuid"},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AttachL3NetworkToVm":{
      "Type":"ZStack::Action::AttachL3NetworkToVm",
      "Properties":{
        "vmInstanceUuid":{"Fn::GetAtt":["VM","uuid"]},
        "l3NetworkUuid":{"Fn::GetAtt":["L3Network","uuid"]},
        "staticIp":"10.141.23.22",
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AttachNetworkServiceToL3Network":{
      "Type":"ZStack::Action::AttachNetworkServiceToL3Network",
      "Properties":{
        "l3NetworkUuid":{"Fn::GetAtt":["L3Network","uuid"]},
        "networkServices":{"1":"a","2":"b"},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AttachSecurityGroupToL3Network":{
      "Type":"ZStack::Action::AttachSecurityGroupToL3Network",
      "Properties":{
        "securityGroupUuid":{"Fn::GetAtt":["SecurityGroup","uuid"]},
        "l3NetworkUuid":{"Fn::GetAtt":["L3Network","uuid"]},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AttachVRouterRouteTableToVRouter":{
      "Type":"ZStack::Action::AttachVRouterRouteTableToVRouter",
      "Properties":{
        "routeTableUuid":{"Fn::GetAtt":["VRouterRouteTable","uuid"]},
        "virtualRouterVmUuid":"lei",
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AddCertificateToLoadBalancerListener":{
      "Type":"ZStack::Action::AddCertificateToLoadBalancerListener",
      "Properties":{
        "certificateUuid":"lei",
        "listenerUuid":{"Fn::GetAtt":["LoadBalancerListener","uuid"]},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
      }
    },
    "AddHostRouteToL3Network":{
      "Type":"ZStack::Action::AddHostRouteToL3Network",
      "Properties":{
        "l3NetworkUuid":{"Fn::GetAtt":["L3Network","uuid"]},
        "prefix":{"Ref":"Prefix"},
        "nexthop":{"Ref":"Nexthop"},
        "timeout":200,
        "systemTags": ["test"],
        "userTags": ["test"]
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
