#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Create a vm with a datavolume.
Cover resource:VM,Data Volume,RootVolumeTemplate,DataVolumeTemplate,DiskOffering,Affinity group

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

    cond = res_ops.gen_query_conditions("category", '=', "Private")
    l3_pri_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('type', '=', 'UserVm', cond)
    instance_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)  

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    bs_queried = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)

    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("Create_STACK")
    resource_stack_option.set_rollback("true")
    templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "本示例将创建一个云盘，并将云盘加载到云主机上(基于本地存储), 创建示例前提环境：\n计算规格，镜像，云盘规格，私有网络，可用物理机",
    "Parameters": {
        "InstanceOfferingUuid": {
            "Type": "String",
            "Label": "计算规格",
            "Description": "The instance offering uuid"
        },
        "ImageUuid":{
            "Type": "String",
            "Label": "镜像",
            "Description": "The Image uuid for creating VmInstance, Please choose an image not iso"
        },
        "PrivateNetworkUuid":{
            "Type": "String",
            "Label": "私有网络",
            "Description" : "The private network uuid for creating VmInstance"
        },
        "BackupStorage":{
            "Type": "CommaDelimitedList",
            "Label": "镜像服务器",
            "Description":"镜像服务器Uuid"
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
        "DataVolume": {
            "Type": "ZStack::Resource::DataVolume",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"Data-Volume"]]},
                "diskOfferingUuid":{"Fn::GetAtt":["DiskOffering","uuid"]}
            }
        },
        "RootVolumeTemplate": {
            "Type": "ZStack::Resource::RootVolumeTemplate",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"Root-Volume-Template"]]},
                "backupStorageUuids": {"Ref":"BackupStorage"},
                "rootVolumeUuid": {"Fn::GetAtt":["VmInstance","rootVolumeUuid"]}
            }
        },
        "DiskOffering": {
            "Type":"ZStack::Resource::DiskOffering",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"Volume-Offering-1G"]]},
                "diskSize": 1073741824
            }
        },
        "AffinityGroup": {
            "Type": "ZStack::Resource::AffinityGroup",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"AffinityGroup"]]},
                "policy": "antiSoft"
            }
        },
        "AddVmToAffinityGroup": {
            "Type": "ZStack::Action::AddVmToAffinityGroup",
            "Properties": {
                "uuid":{"Fn::GetAtt":["VmInstance","uuid"]},
                "affinityGroupUuid":{"Fn::GetAtt":["AffinityGroup","uuid"]}
            }
        },
        "AttachDataVolumeToVm": {
            "Type": "ZStack::Action::AttachDataVolumeToVm",
            "Properties": {
                "vmInstanceUuid": {"Fn::GetAtt":["VmInstance","uuid"]},
                "volumeUuid": {"Fn::GetAtt":["DataVolume","uuid"]}
            }
        },
        "DataVolumeTemplate": {
            "Type": "ZStack::Resource::DataVolumeTemplate",
            "Properties": {
                "name": {"Fn::Join":["-",[{"Ref":"ZStack::StackName"},"Data-Volume-Template"]]},
                "backupStorageUuids": {"Ref":"BackupStorage"},
                "volumeUuid": {"Fn::GetAtt":["DataVolume","uuid"]}
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
    #test_util.test_logger('{"PrivateNetworkUuid":"%s","ImageUuid":"%s","InstanceOfferingUuid":"%s"}' % (l3_pri_queried[0].uuid, image_queried[0].uuid, instance_offering_queried[0].uuid))
    parameter = '{"PrivateNetworkUuid":"%s","ImageUuid":"%s","InstanceOfferingUuid":"%s","BackupStorage":"%s"}' % (l3_pri_queried[0].uuid, image_queried[0].uuid, instance_offering_queried[0].uuid, bs_queried[0].uuid)
    
    resource_stack_option.set_templateContent(templateContent)
    resource_stack_option.set_parameters(parameter)
    preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)
    resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)
    

    #2.query resource stack
    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VM')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Data-Volume')
    data_volume_queried = res_ops.query_resource(res_ops.VOLUME, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Volume-Offering-1G')
    volume_offering_queried = res_ops.query_resource(res_ops.DISK_OFFERING, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Data-Volume-Template')
    dv_template_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Root-Volume-Template')
    rv_template_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-AffinityGroup')
    affinity_group_queried = res_ops.query_resource(res_ops.AFFINITY_GROUP, cond)

    if len(resource_stack_queried) == 0:
        test_util.test_fail("Fail to query resource stack")

    if resource_stack_queried[0].status == 'Created':
        if len(vm_queried) == 0 or len(data_volume_queried) == 0 or len(volume_offering_queried) == 0 or len(dv_template_queried) == 0 or len(rv_template_queried) == 0 or len(affinity_group_queried) == 0:
            test_util.test_fail("Fail to create all resource when resource stack status is Created")  
    
    #3.get resource from resource stack
    resource = resource_stack_ops.get_resource_from_resource_stack(resource_stack.uuid)
    if resource == None or len(resource) != 6:
        test_util.test_fail("Fail to get resource from resource_stack")
    
    #4.query event from resource stack
    cond = res_ops.gen_query_conditions('stackUuid', '=', resource_stack.uuid)
    event = res_ops.query_event_from_resource_stack(cond)
    if event == None or len(event) != 16:
        test_util.test_fail("Fail to get event from resource_stack")

    #5.delete resource stack
    resource_stack_ops.delete_resource_stack(resource_stack.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-VM')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Data-Volume')
    data_volume_queried = res_ops.query_resource(res_ops.VOLUME, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Volume-Offering-1G')
    volume_offering_queried = res_ops.query_resource(res_ops.DISK_OFFERING, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Data-Volume-Template')
    dv_template_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-Root-Volume-Template')
    rv_template_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_STACK-AffinityGroup')
    affinity_group_queried = res_ops.query_resource(res_ops.AFFINITY_GROUP, cond)

    if len(resource_stack_queried) != 0 :
        test_util.test_fail("Fail to delete resource stack") 
    elif len(vm_queried) != 0 or len(data_volume_queried) != 0 or len(volume_offering_queried) != 0 or len(dv_template_queried) != 0 or len(rv_template_queried) != 0 or len(affinity_group_queried) != 0:
        test_util.test_fail("Fail to delete resource when resource stack is deleted")   
   

    test_util.test_pass('Create Resource Stack Test Success')




#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"

