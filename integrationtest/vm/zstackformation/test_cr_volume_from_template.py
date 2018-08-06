#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Create a Basic vm with a data volume which is created from volume template.
Cover resource: DataVolumeFromVolumeTemplate and bug14035

@author: chenyuan.xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import os

def test():
    test_util.test_dsc("Test Resource template Apis")

    cond = res_ops.gen_query_conditions("category", '=', "Public")
    l3_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    if len(l3_queried) == 0:
        cond = res_ops.gen_query_conditions("category", '=', "Private")
        l3_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('type', '=', 'UserVm', cond)
    instance_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)

    cond = res_ops.gen_query_conditions('status', '=', 'Ready')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled', cond)
    cond = res_ops.gen_query_conditions('system', '=', 'false', cond)
    image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    ps_queried = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host_queried = res_ops.query_resource(res_ops.HOST, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    bs_queried = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)

    volume_image_url = os.environ.get('imageUrl_s')
    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("Create_STACK")
    resource_stack_option.set_rollback("true")
    templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "",
    "Parameters": {
        "InstanceOfferingUuid":{
            "Type": "String",
            "Label": "计算规格"
        },
        "ImageUuid":{
            "Type": "String",
            "Label": "云主机镜像"        
        },
        "PrivateNetworkUuid": {
            "Type": "String",
            "Label": "私有网络"
        },
        "PrimaryStorageUuid": {
            "Type": "String",
            "Label": "主存储"
        },
        "HostUuid": {
            "Type": "String",
            "Label": "物理机"
        },
        "BackupStorageUuid": {
            "Type": "CommaDelimitedList",
            "Label": "镜像服务器"
        },
        "VolumeImageUrl": {
            "Type": "String",
            "Label": "云盘镜像链接地址",
			"Description":"测试盘镜像，请确定ZStack 可以下载下面链接的镜像"
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
        "VolumeImage": {
            "Type": "ZStack::Resource::Image",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"IMAGE"]]},
                "url": {"Ref":"VolumeImageUrl"},
		"format": "qcow2",
		"mediaType": "DataVolumeTemplate",
		"backupStorageUuids":{"Ref":"BackupStorageUuid"}
            }
        },
        "VOLUME": {
            "Type": "ZStack::Resource::DataVolumeFromVolumeTemplate",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"VOLUME"]]},
                "systemTags": [
                    "capability::virtio-scsi"
                ],
                "imageUuid": {"Fn::GetAtt":["VolumeImage","uuid"]},
                "primaryStorageUuid": {"Ref":"PrimaryStorageUuid"},
                "hostUuid": {"Ref":"HostUuid"}
            }
        },
        "AttachDataVolumeToVm": {
            "Type": "ZStack::Action::AttachDataVolumeToVm",
            "Properties": {
                "volumeUuid": {
                    "Fn::GetAtt": [
                        "VOLUME",
                        "uuid"
                    ]
                },
                "vmInstanceUuid": {
                    "Fn::GetAtt": [
                        "VM",
                        "uuid"
                    ]
                }
            }
        }
    }
}
'''
    #1.create resource stack
    parameter = '{"InstanceOfferingUuid":"%s","PrivateNetworkUuid":"%s","PrimaryStorageUuid":"%s","BackupStorageUuid":"%s","HostUuid":"%s","VolumeImageUrl":"%s","ImageUuid":"%s"}' % (instance_offering_queried[0].uuid, l3_queried[0].uuid, ps_queried[0].uuid, bs_queried[0].uuid, host_queried[0].uuid, volume_image_url, image_queried[0].uuid)
    resource_stack_option.set_templateContent(templateContent)
    resource_stack_option.set_parameters(parameter)
    preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)
    resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)

    #2.query resource stack
    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VM')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-IMAGE')
    image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VOLUME')
    volume_queried = res_ops.query_resource(res_ops.VOLUME, cond)

    if len(resource_stack_queried) == 0:
        test_util.test_fail("Fail to query resource stack")
    if resource_stack_queried[0].status == 'Created':
        if len(vm_queried) == 0 or len(image_queried) == 0 or len(volume_queried) == 0:
            test_util.test_fail("Fail to create all resource when resource stack status is Created")

    #3.get resource from resource stack
    resource = resource_stack_ops.get_resource_from_resource_stack(resource_stack.uuid)
    if resource == None or len(resource) != 3:
        test_util.test_fail("Fail to get resource from resource_stack")

    #4.query event from resource stack
    cond = res_ops.gen_query_conditions('stackUuid', '=', resource_stack.uuid)
    event = res_ops.query_event_from_resource_stack(cond)
    if event == None or len(event) != 8:
        test_util.test_fail("Fail to get event from resource_stack")

    #5.delete resource stack
    resource_stack_ops.delete_resource_stack(resource_stack.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VM')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-IMAGE')
    image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VOLUME')
    cond = res_ops.gen_query_conditions('status', '=', 'Ready',cond)
    volume_queried = res_ops.query_resource(res_ops.VOLUME, cond)

    if len(resource_stack_queried) != 0 :
        test_util.test_fail("Fail to delete resource stack") 
    if len(vm_queried) != 0 or len(image_queried) != 0 or len(volume_queried) != 0:
        test_util.test_fail("Fail to delete resource when resource stack is deleted")   
   

    test_util.test_pass('Create Resource Stack Test Success')




#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"





