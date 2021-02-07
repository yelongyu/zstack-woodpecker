#coding:utf-8
'''

New Integration Test for zstack cloudformation.

@author: Lei Liu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_stack as resource_stack_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():
    test_util.test_dsc("Test Resource template Apis")
    
    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_name("test")
    templateContent = '''
{
    "ZStackTemplateFormatVersion": "2018-06-18",
    "Description": "test",
    "Parameters": {
        "TestStringBasicEcho": {
             "Type": "String",
             "DefaultValue":"testonly"
        }
    },
    "Resources": {
        "InstanceOffering": {
            "Type": "ZStack::Resource::InstanceOffering",
            "Properties": {
                "name": "8cpu-8g",
                "cpuNum": 8,
                "memorySize": 8589934592
            }
        }
    },
    "Outputs": {
        "InstanceOffering": {
            "Value": {
                "Ref": "InstanceOffering"
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
    resource_stack_option.set_templateContent(templateContent)
    resource_stack_option.set_parameters(parameter)

    preview_resource_stack = resource_stack_ops.preview_resource_stack(resource_stack_option)

    resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)

    if len(resource_stack_queried) == 0:
        test_util.test_fail("Fail to query stack template")
    #Add a template via text.

    resource = resource_stack_ops.get_resource_from_resource_stack(resource_stack.uuid)
    print resource
    if resource == None:
        test_util.test_fail("Fail to get resource from resource_stack")

    print resource_stack.uuid
    cond = res_ops.gen_query_conditions('stackUuid', '=', resource_stack.uuid)
    event = res_ops.query_event_from_resource_stack(cond)
    print event
    if event == None:
        test_util.test_fail("Fail to get event from resource_stack")

    resource_stack_ops.delete_resource_stack(resource_stack.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', resource_stack.uuid)
    resource_stack_queried = res_ops.query_resource(res_ops.RESOURCE_STACK, cond)
    if len(resource_stack_queried) != 0:
        test_util.test_fail("Fail to query stack template")

    test_util.test_pass('Create Stack Template Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    print "Ignore cleanup"
