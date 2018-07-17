#coding:utf-8
'''

New Integration Test for zstack cloudformation.
Create Resource Stack when state of stack template is false(expected result is failed).

@author: Lei Liu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.stack_template as stack_template_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
    test_util.test_dsc("Test Resource template Apis")
    
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

    stack_template_option = test_util.StackTemplateOption()
    stack_template_option.set_name("template")
    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("Stack_test")
    templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "Just create a flat network & VM",
    "Parameters": {
        "L3NetworkUuid":{
            "Type": "String",
            "Label": "三层网络"
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
    #1.Add template which state is false
    stack_template_option.set_templateContent(templateContent)
    stack_template = stack_template_ops.add_stack_template(stack_template_option)
    cond = res_ops.gen_query_conditions('uuid', '=', stack_template.uuid)
    stack_template_queried = res_ops.query_resource(res_ops.STACK_TEMPLATE, cond)
    if len(stack_template_queried) == 0:
        test_util.test_fail("Fail to query stack template")
    
    stack_template_option.set_state('false')
    new_stack_template = stack_template_ops.update_stack_template(stack_template.uuid, stack_template_option)
   
    #2.Create a resource stack based on this template
    parameter = '{"L3NetworkUuid":"%s","ImageUuid":"%s","InstanceOfferingUuid":"%s"}' % (l3_queried[0].uuid, image_queried[0].uuid, instance_offering_queried[0].uuid)
    resource_stack_option.set_template_uuid(new_stack_template.uuid)
    resource_stack_option.set_parameters(parameter)
    #preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)

    try:
        resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)
        test_util.test_fail('Cannot create stack when stack template is disabled.')
    except:
        pass    

    #3.Qeury this stack
    cond = res_ops.gen_query_conditions('name', '=', 'Stack_test')
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)
    if len(resource_stack_queried) != 0:
        test_util.test_fail('Resource stack should not be existed.')

    stack_template_option.set_state('true')
    lastest_stack_template = stack_template_ops.update_stack_template(stack_template.uuid, stack_template_option)
    test_util.test_logger(lastest_stack_template.uuid)

    #4.Set template state true
    resource_stack_option.set_template_uuid(lastest_stack_template.uuid)
    resource_stack_option.set_parameters(parameter)
    resource_stack_option.set_name("Stack_test")

    resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)
    cond = res_ops.gen_query_conditions('name', '=', 'Stack_test')
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)
    if len(resource_stack_queried) == 0:
        test_util.test_fail('Failed to create resource stack.')

    cond = res_ops.gen_query_conditions('name', '=', 'VM-STACK')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)

    if resource_stack_queried[0].status == 'Created':
        if len(vm_queried) == 0:
            test_util.test_fail("Fail to create all resource when resource stack status is Created")   

    #5.delete resource stack
    resource_stack_ops.delete_resource_stack(resource_stack.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    cond = res_ops.gen_query_conditions('name', '=', 'VM-STACK')
    vm_queried = res_ops.query_resource(res_ops.VM_INSTANCE, cond)


    if len(resource_stack_queried) != 0 :
        test_util.test_fail("Fail to delete resource stack") 
    elif len(vm_queried) != 0 :
        test_util.test_fail("Fail to delete resource when resource stack is deleted")   
    #6.delete stack template
    stack_template_ops.delete_stack_template(lastest_stack_template.uuid)
    stack_template_queried = res_ops.query_resource(res_ops.STACK_TEMPLATE, cond)
    if len(stack_template_queried) != 0:
        test_util.test_fail("Fail to query stack template")


    test_util.test_pass('Create Resource Stack Test Success')


#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"
