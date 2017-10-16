import apibinding.api_actions as api_actions
import account_operations
import apibinding.inventory as inventory


def create_vpc_vrouter(name, virtualrouter_offering_uuid, resource_uuid=None, system_tags=None, use_tags=None, session_uuid=None):
    action = api_actions.CreateVpcVRouterAction()
    action.timeout = 30000
    action.name = name
    action.virtualRouterOfferingUuid = virtualrouter_offering_uuid
    action.resourceUuid = resource_uuid
    action.systemTags = system_tags
    action.userTags = use_tags
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

