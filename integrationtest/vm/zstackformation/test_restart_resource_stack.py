#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Test Restartresourcestack api.


@author: xiaoshuang
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops

def test():
    test_util.test_dsc("Test Resource Stack Apis")
    
    cond = res_ops.gen_query_conditions('status', '=', 'Ready')
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled', cond)
    cond = res_ops.gen_query_conditions('system', '=', 'false', cond)
    image_queried = res_ops.query_resource(res_ops.IMAGE, cond)

    cond = res_ops.gen_query_conditions("category", '=', "Public")
    l3_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    if len(l3_queried) == 0:
        cond = res_ops.gen_query_conditions("category", '=', "Private")
        l3_queried = res_ops.query_resource(res_ops.L3_NETWORK, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('type', '=', 'UserVm', cond)
    instance_offering_queried = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    ps_queried = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)  

    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("Restart_Stack")
    templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "Just create a flat network & VM",
    "Parameters": {
        "L3NetworkUuid":{
            "Type": "String",
            "Label": "三层网络",
            "DefaultValue": "testuuid"
        },
        "ImageUuid":{
            "Type": "String",
            "Label": "镜像"
        },
        "InstanceOfferingUuid":{
            "Type": "String",
            "Label": "计算规格"
        }
    },
    "Resources": {
        "VmInstance": {
            "Type": "ZStack::Resource::VmInstance",
            "Properties": {
                "name": "VM-STACK",
                "instanceOfferingUuid": {"Ref":"InstanceOfferingUuid"},
                "imageUuid":{"Ref":"ImageUuid"},
                "l3NetworkUuids":[{"Ref":"L3NetworkUuid"}]
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
    ps_ops.change_primary_storage_state(ps_queried[0].uuid, 'disable')
    parameter = '{"ImageUuid":"%s","InstanceOfferingUuid":"%s","L3NetworkUuid":"%s"}' % (image_queried[0].uuid, instance_offering_queried[0].uuid, l3_queried[0].uuid)
    resource_stack_option.set_templateContent(templateContent)
    resource_stack_option.set_parameters(parameter)
    #preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)
    try:
        resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)
        test_util.test_fail('This resource stack cannot be created successfully')
    except:
        pass
    
    #2.query resource stack
    cond = res_ops.gen_query_conditions('name', '=', 'Restart_Stack')
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'VM-STACK')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    if len(resource_stack_queried) == 0:
        test_util.test_fail("Fail to query resource stack")
    elif resource_stack_queried[0].status == 'Created':
        test_util.test_fail('The status of resource stack cannot be created')
    else:
        if len(vm_queried) != 0:
            test_util.test_fail('Vm cannot be created when resource stack is Rollbacked or Failed')

    #3.restart resource stack
    ps_ops.change_primary_storage_state(ps_queried[0].uuid, 'enable')
    resource_stack_ops.restart_resource_stack(resource_stack_queried[0].uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack_queried[0].uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'VM-STACK')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    if len(resource_stack_queried) == 0:
        test_util.test_fail("Fail to query resource stack")
    elif resource_stack_queried[0].status != 'Created':
        test_util.test_fail('The status of resource stack should be created')
    else:
        if len(vm_queried) == 0:
            test_util.test_fail('Vm should be created when resource stack is Created')

    try:
        resource_stack_ops.restart_resource_stack(resource_stack_queried[0].uuid)
        test_util.test_fail('Resource stack cannot restart when status of stack is created')
    except:
        pass

    #4.delete resource stack
    resource_stack_ops.delete_resource_stack(resource_stack_queried[0].uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack_queried[0].uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'VM-STACK')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    if len(resource_stack_queried) != 0 :
        test_util.test_fail("Fail to delete resource stack") 
    elif len(vm_queried) != 0:
        test_util.test_fail("Fail to delete resource when resource stack is deleted")   
   

    test_util.test_pass('Restart Resource Stack Test Success')




#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"
