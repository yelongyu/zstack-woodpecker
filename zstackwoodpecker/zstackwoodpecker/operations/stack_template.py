'''

All Stack template operations for test.

@author: Lei Liu
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations

def add_stack_template(stack_template_option):
    add_stack_template = api_actions.AddStackTemplateAction()
    name = stack_template_option.get_name()
    if not name:
        add_stack_template.name = 'test_stack_template_default_name'
    else:
        add_stack_template.name = name

    add_stack_template.templateContent = stack_template_option.get_templateContent()
    add_stack_template.url = stack_template_option.get_url()

    evt = account_operations.execute_action_with_session(add_stack_template, stack_template_option.get_session_uuid())
    return evt.inventory

def delete_stack_template(uuid, session_uuid=None):
    action = api_actions.DeleteStackTemplateAction()
    action.uuid = uuid
    action.timeout = 240000
    test_util.action_logger('Destroy Stack template [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_stack_template(uuid, stack_template_option, session_uuid=None):
    action = api_actions.UpdateStackTemplateAction()
    action.name = stack_template_option.get_name()
    action.state = stack_template_option.get_state()
    action.uuid = uuid
    action.templateContent = stack_template_option.get_templateContent()
    action.timeout = 240000
    test_util.action_logger('update stack template [name:] %s' % stack_template_option.get_name())
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

    action = api_actions.DeleteInstanceOfferingAction()
    action.uuid = instance_offering_uuid
    test_util.action_logger('Delete Instance Offering [uuid:] %s' \
            % instance_offering_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt
