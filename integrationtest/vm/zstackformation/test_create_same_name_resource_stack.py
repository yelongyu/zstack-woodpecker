#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Create 5 resource stacks with the same name and then delete them.

@author: chenyuan.xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
    test_util.test_dsc("Test Resource template Apis")
    
    cond = res_ops.gen_query_conditions('status', '=', 'Connected')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled', cond)
    bs_queried = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)

    cond = res_ops.gen_query_conditions("category", '=', "Public")
    l3_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    if len(l3_queried) == 0:
        cond = res_ops.gen_query_conditions("category", '=', "Private")
        l3_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)  

    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("Create_VM")
    templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "Just create a flat network & VM",
    "Parameters": {
        "L3NetworkUuid":{
            "Type": "String",
            "Label": "三层网络"
        },
        "BackupStorageUuid":{
            "Type": "CommaDelimitedList",
            "Label": "镜像服务器"
        }
    },
    "Resources": {
        "VmInstance": {
            "Type": "ZStack::Resource::VmInstance",
            "Properties": {
                "name": "VM-STACK",
                "instanceOfferingUuid": {"Fn::GetAtt":["InstanceOffering","uuid"]},
                "imageUuid":{"Fn::GetAtt":["Image","uuid"]},
                "l3NetworkUuids":[{"Ref":"L3NetworkUuid"}]
            }
        },
        "InstanceOffering": {
            "Type": "ZStack::Resource::InstanceOffering",
            "Properties": {
                "name":"1G-1CPU-STACK",
                "description":"测试创建计算规格",
                "cpuNum": 1,
                "memorySize": 1073741824
            }
        },
        "Image": {
            "Type": "ZStack::Resource::Image",
            "Properties": {
                "name": "IMAGE-STACK",
                "backupStorageUuids": {"Ref":"BackupStorageUuid"},
                "url":"file:///opt/zstack-dvd/zstack-image-1.4.qcow2",
                "format": "qcow2"
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
    #1.create resource stack 5 times with the same name
    parameter = '{"L3NetworkUuid":"%s","BackupStorageUuid":"%s"}' % (l3_queried[0].uuid, bs_queried[0].uuid)
    for i in range(5):
        resource_stack_option.set_templateContent(templateContent)
        resource_stack_option.set_parameters(parameter)
        preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)
        resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)
    

    #2.query resource stack
    cond = res_ops.gen_query_conditions('name', '=', 'Create_VM')
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'VM-STACK')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    cond = res_ops.gen_query_conditions('name', '=', '1G-1CPU-STACK')
    instance_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'IMAGE-STACK')
    image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    test_util.test_logger(len(image_queried))

    if len(resource_stack_queried) != 5:
        test_util.test_fail("Fail to query 5 resource stacks")

    for i in range(5):
        if resource_stack_queried[i].status == 'Created':
            if len(vm_queried) != 5 or len(instance_offering_queried) != 5 or len(image_queried) != 5:
                test_util.test_fail("Fail to create all resource when resource stack status is Created")

    #5.delete resource stack
    for i in range(5):
        resource_stack_ops.delete_resource_stack(resource_stack_queried[i].uuid)

    cond = res_ops.gen_query_conditions('name', '=', 'Create_VM')
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'VM-STACK')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    cond = res_ops.gen_query_conditions('name', '=', '1G-1CPU-STACK')
    instance_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'IMAGE-STACK')
    image_queried = res_ops.query_resource(res_ops.IMAGE, cond)


    if len(resource_stack_queried) != 0 :
        test_util.test_fail("Fail to delete all resource stack and there are still %s resource stacks not deleted.") % len(resource_stack_queried)
    elif len(vm_queried) != 0 or len(instance_offering_queried) != 0 or len(image_queried) != 0:
        test_util.test_fail("Fail to delete resource when resource stack is deleted and there are still %s vm, %s instance offering, %s image not deleted.") % (len(vm_queried), len(instance_offering_queried), len(image_queried)) 
   

    test_util.test_pass('Create Resource Stack With The Same Name Test Success')




#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"
