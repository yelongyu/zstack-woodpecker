

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.resource_operations as res_ops

def create_ticket(name,request_name,api_body,api_name,execute_times,account_system_type,virtual_id_uuid,project_uuid,session_uuid=None,description=None,resource_uuid=None,flow_collection_uuid=None):
	action =api_actions.CreateTicketAction()
	action.timeout = 30000
	action.name = name
	
	if description:
		action.description = description
		
	action.requests = [{'requestName':request_name,'apiName':api_name,'executeTimes':execute_times,'apiBody':api_body}]
	action.flowCollectionUuid = flow_collection_uuid
	action.accountSystemType = account_system_type 
	action.accountSystemContext = {'virtualIDUuid':virtual_id_uuid,'projectUuid':project_uuid}
	
	if resource_uuid:
		action.resourceUuid = resource_uuid
		
	test_util.action_logger('Create Ticket %s ' %name)
	evt = account_operations.execute_action_with_session(action,session_uuid)
	return evt.inventory
	
def update_ticket_request(uuid,request_name,api_body,api_name,execute_times,session_uuid=None):
	action =api_actions.UpdateTicketRequestAction()
	action.timeout = 30000
	action.uuid = uuid
	action.requests = [{'requestName':request_name,'apiName':api_name,'executeTimes':execute_times,'apiBody':api_body}]
	test_util.action_logger('Update Ticket uuid= %s' %uuid )
	evt = account_operations.execute_action_with_session(action,session_uuid)
	return evt
	
def change_ticket_status(uuid,status_event,session_uuid = None,comment = None):
	action =api_actions.ChangeTicketStatusAction()
	action.timeout = 30000
	action.uuid = uuid
	action.statusEvent = status_event
	test_util.action_logger('Change Ticket uuid= %s' %uuid )
	evt = account_operations.execute_action_with_session(action, session_uuid)
	return evt
	
def delete_ticket(uuid,session_uuid=None,delete_mode= None):
	action =api_actions.DeleteTicketAction()
	action.timeout = 30000
	action.uuid = uuid
	action.deleteMode =delete_mode
	test_util.action_logger('Delete Ticket uuid= %s' %uuid )
	evt = account_operations.execute_action_with_session(action, session_uuid)
	return evt

