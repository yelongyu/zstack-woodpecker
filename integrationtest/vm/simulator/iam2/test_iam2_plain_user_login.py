'''
test iam2 login by plain user

# 1 create project
# 2 create plain user
# 3 login in project by plain user
# 4 TODO:more operations
# 5 logout
# 6 delete

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time

project_uuid = None
plain_user_uuid = None


def test():
	global project_uuid, plain_user_uuid

	# 1 create project
	project_name = 'test_project'
	project = iam2_ops.create_iam2_project(project_name)
	project_name = project.name
	project_uuid = project.uuid

	# 2 create plain user
	plain_user_name = 'username'
	plain_user_password = 'password'
	plain_user_uuid = iam2_ops.create_iam2_virtual_id(plain_user_name, plain_user_password,
	                                                  project_uuid=project_uuid).uuid

	# 3 add virtual id to project
	iam2_ops.add_iam2_virtual_ids_to_project([plain_user_uuid],project_uuid)

	# 4 login in project by plain user
	plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(plain_user_name, plain_user_password)

	# 4 login in project
	#project_inv=iam2_ops.get_iam2_projects_of_virtual_id(plain_user_session_uuid)
	project_session_uuid = iam2_ops.login_iam2_project(project_name, plain_user_session_uuid).uuid

	# 5 get iam2 virtual id api permission and project
	iam2_ops.get_iam2_virtual_id_permission(session_uuid=project_session_uuid)
	# time.sleep(20)

	# 6 logout
	acc_ops.logout(project_session_uuid)

	# 7 delete
	iam2_ops.delete_iam2_virtual_id(plain_user_uuid)
	iam2_ops.delete_iam2_project(project_uuid)
	iam2_ops.expunge_iam2_project(project_uuid)

	test_util.test_pass('success test iam2 login in by plain user')


def error_cleanup():
	global project_uuid, plain_user_uuid
	if project_uuid:
		iam2_ops.delete_iam2_project(project_uuid)
		iam2_ops.delete_iam2_project(project_uuid)
	if plain_user_uuid:
		iam2_ops.delete_iam2_virtual_id(plain_user_uuid)
