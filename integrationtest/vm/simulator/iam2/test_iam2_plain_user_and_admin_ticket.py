'''
test iam2 ticket by plain user
create project
create plain user
add virtual id to project
login in project by plain user
get iam2 virtual id api permission and project
create ticket
query ticket
update ticket
Withdraw the ticket
examination the ticket
create ticket_2
delete ticket 

'''

import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.iam2_ticket_operations as ticket_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import os

project_uuid = None
project_admin_uuid = None
virtual_id_uuid = None

def test():
	iam2_ops.clean_iam2_enviroment()
	global project_uuid,project_admin_uuid,virtual_id_uuid
	#  create project
	project_name = 'test_project'
	project_uuid = iam2_ops.create_iam2_project(project_name).uuid
	
	#  create plain user
	plain_user_name = 'username'
	plain_user_password = 'password'
	plain_user_uuid = iam2_ops.create_iam2_virtual_id(plain_user_name, plain_user_password,project_uuid=project_uuid).uuid
	
	#add role
	statements = [{"effect": "Allow", "actions": ["org.zstack.ticket.**"]}]
	role_uuid = iam2_ops.create_role('test_role', statements).uuid
	action = "org.zstack.ticket.**"
	statements = [{"effect": "Allow", "actions": [action]}]
	iam2_ops.add_policy_statements_to_role(role_uuid, statements)
	statement_uuid = iam2_ops.get_policy_statement_uuid_of_role(role_uuid, action)
	
	iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], plain_user_uuid)
	
	#add virtual id to project
	iam2_ops.add_iam2_virtual_ids_to_project([plain_user_uuid],project_uuid)
	
	#login in project by plain user
	plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(plain_user_name, plain_user_password)
	project_login_uuid = iam2_ops.login_iam2_project(project_name, session_uuid=plain_user_session_uuid).uuid
	#get iam2 virtual id api permission and project
	iam2_ops.get_iam2_virtual_id_permission(session_uuid=project_login_uuid)
	
	#create ticket
	ticket_name = 'ticket_1'
	session_uuid = project_login_uuid
	api_name='org.zstack.header.vm.APICreateVmInstanceMsg'
	request_name='create-vm-ticket'
	executeTimes=1
	account_system_type='iam2'	
	
	conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
	instance_offering_uuid =res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
	
	image_name = os.environ.get('imageName_s')
	image_uuid=test_lib.lib_get_image_by_name(image_name).uuid
	
	l3_name = os.environ.get('l3VlanNetworkName1')
	l3_network_uuids=test_lib.lib_get_l3_by_name(l3_name).uuid
	
	api_body={"name":"vm","instanceOfferingUuid":instance_offering_uuid,"imageUuid":image_uuid,"l3NetworkUuids":[l3_network_uuids]}
	
	ticket= ticket_ops.create_ticket(ticket_name,request_name,api_body,api_name,executeTimes,account_system_type,plain_user_uuid,project_uuid,session_uuid)
	
	if ticket == None:
		test_util.test_fail('fail to create ticket by plain user!')
		
	
	#query ticket
	cond= res_ops.gen_query_conditions('uuid','=', ticket.uuid)
	ticket_list = res_ops.query_resource(res_ops.TICKET,cond,session_uuid)
	
	if ticket_list!= None:
		test_util.test_logger('success query ticket by plain user!')
	
	#examination the ticket by user
	try:
		ticket_ops.change_ticket_status(ticket.uuid,'reject',session_uuid)
		test_util.test_fail("can't examination ticket by user ")
	except:
		test_util.test_logger('examination ticket fail by user ')
	
	#examination the ticket by admin
	ticket_ops.change_ticket_status(ticket.uuid,'reject')
	
	#update ticket
	request_name_2='create-vm-ticket-2'
	ticket_ops.update_ticket_request(ticket.uuid,request_name_2,api_body,api_name,executeTimes,session_uuid)
	#query ticket 
	cond= res_ops.gen_query_conditions('uuid','=', ticket.uuid)
	ticket_list = res_ops.query_resource(res_ops.TICKET,cond,session_uuid)[0]
	request=ticket_list.request[0]
	requestName=request.requestName
	
	if requestName !='create-vm-ticket-2':
		test_util.test_fail('fail to update ticket by plain user!')
	
	#create ticket_2
	ticket_name = 'ticket_2'
	session_uuid = project_login_uuid
	api_name='org.zstack.header.vm.APICreateVmInstanceMsg'
	request_name='create-vm-ticket'
	executeTimes=1
	account_system_type='iam2'	
	
	conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
	instance_offering_uuid =res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
	
	image_name = os.environ.get('imageName_s')
	image_uuid=test_lib.lib_get_image_by_name(image_name).uuid
	
	l3_name = os.environ.get('l3VlanNetworkName1')
	l3_network_uuids=test_lib.lib_get_l3_by_name(l3_name).uuid
	
	api_body={"name":"vm","instanceOfferingUuid":instance_offering_uuid,"imageUuid":image_uuid,"l3NetworkUuids":[l3_network_uuids]}
	
	ticket_2= ticket_ops.create_ticket(ticket_name,request_name,api_body,api_name,executeTimes,account_system_type,plain_user_uuid,project_uuid,session_uuid)
	
	
	#Withdraw the ticket
	ticket_ops.change_ticket_status(ticket_2.uuid,'cancel',session_uuid)
	
	cond= res_ops.gen_query_conditions('uuid','=', ticket_2.uuid)
	statusEvent = res_ops.query_resource(res_ops.TICKET,cond,session_uuid)[0].status
	
	if statusEvent !='Cancelled' :
		test_util.test_fail('fail to Withdraw ticket by plain user!')
	
	#create ticket_3
	ticket_name = 'ticket_3'
	session_uuid = project_login_uuid
	api_name='org.zstack.header.vm.APICreateVmInstanceMsg'
	request_name='create-vm-ticket'
	executeTimes=1
	account_system_type='iam2'	
	
	conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
	instance_offering_uuid =res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
	
	image_name = os.environ.get('imageName_s')
	image_uuid=test_lib.lib_get_image_by_name(image_name).uuid
	
	l3_name = os.environ.get('l3VlanNetworkName1')
	l3_network_uuids=test_lib.lib_get_l3_by_name(l3_name).uuid
	
	api_body={"name":"vm","instanceOfferingUuid":instance_offering_uuid,"imageUuid":image_uuid,"l3NetworkUuids":[l3_network_uuids]}
	
	ticket_3= ticket_ops.create_ticket(ticket_name,request_name,api_body,api_name,executeTimes,account_system_type,plain_user_uuid,project_uuid,session_uuid)
	
	
	#delete ticket 
	ticket_ops.delete_ticket(ticket_3.uuid)
	cond= res_ops.gen_query_conditions('uuid','=', ticket_3.uuid)
	ticket_list_2 = res_ops.query_resource(res_ops.TICKET,cond)
	if not ticket_list_2:
		test_util.test_pass('success test iam2 ticket by plain user')
	else:
		test_util.test_fail("test fail ")
def error_cleanup():
	global project_uuid, project_admin_uuid, virtual_id_uuid
	if virtual_id_uuid:
		iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
	if project_admin_uuid:
		iam2_ops.delete_iam2_virtual_id(project_admin_uuid)
	if project_uuid:
		iam2_ops.delete_iam2_project(project_uuid)
		iam2_ops.expunge_iam2_project(project_uuid)
	iam2_ops.clean_iam2_enviroment()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	