'''
test iam2 ticket by platform admin
create project
create virtual id
create platform admin
login in project by platform admin
create ticket
query ticket


'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.iam2_ticket_operations as ticket_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import os

project_uuid = None
platform_admin_uuid = None
virtual_id_uuid = None

def test():
	iam2_ops.clean_iam2_enviroment()
	global project_uuid,platform_admin_uuid,virtual_id_uuid
    #create project
	project_name = 'test_project'
	project_uuid = iam2_ops.create_iam2_project(project_name).uuid
	
	#create virtual id
	platform_admin_name = 'username'
	platform_admin_password = 'password'
	platform_admin_uuid = iam2_ops.create_iam2_virtual_id(platform_admin_name, platform_admin_password).uuid
	virtual_id_uuid = iam2_ops.create_iam2_virtual_id('usernametwo', 'password').uuid

	#create platform admin
	iam2_ops.add_iam2_virtual_ids_to_project([platform_admin_uuid],project_uuid)
	attributes = [{"name": "__PlatformAdmin__", "value": project_uuid}]
	iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin_uuid, attributes)

	#login in project by platform admin
	platform_admin_session_uuid = iam2_ops.login_iam2_virtual_id(platform_admin_name, platform_admin_password)
	project_login_uuid = iam2_ops.login_iam2_project(project_name, session_uuid=platform_admin_session_uuid).uuid

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
	try:
		ticket= ticket_ops.create_ticket(ticket_name,request_name,api_body,api_name,executeTimes,account_system_type,virtual_id_uuid,project_uuid,session_uuid)
		test_util.test_fail("can't create ticket by platform admin ")
	except:
		test_util.test_logger("create ticket fail by platform admin ")
	#query ticket

	try:
		cond= res_ops.gen_query_conditions('uuid','=', ticket.uuid)
		ticket_list = res_ops.query_resource(res_ops.TICKET,cond)
		test_util.test_fail("can't query ticket by platform admin ")
	except:
		test_util.test_pass('success test iam2 ticket by platform admin')
		
def error_cleanup():
	global project_uuid, platform_admin_uuid, virtual_id_uuid
	if virtual_id_uuid:
		iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
	if platform_admin_uuid:
		iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)
	if project_uuid:
		iam2_ops.delete_iam2_project(project_uuid)
		iam2_ops.expunge_iam2_project(project_uuid)
	iam2_ops.clean_iam2_enviroment()
	