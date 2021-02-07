'''
test iam2  admin negtive operations

@author: rhZhou
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util

def test():
    iam2_ops.clean_iam2_enviroment()

    virtual_id_uuid_list = []
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    for char in ['A','B','C','D','E']:
        username = 'testuser-'+char
        virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
        virtual_id_uuid_list.append(virtual_id_uuid)

    project_name = 'test_project'
    project_uuid = iam2_ops.create_iam2_project(project_name).uuid

    company_uuid_01 = iam2_ops.create_iam2_organization('test_company_01', 'Company').uuid
    department_01_uuid = iam2_ops.create_iam2_organization('test_department_01', 'Department',
                                                           parent_uuid=company_uuid_01).uuid

    for virtual_id_uuid in virtual_id_uuid_list:
        iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid],project_uuid)
        iam2_ops.add_iam2_virtual_ids_to_organization([virtual_id_uuid],company_uuid_01)



    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid_list[0], attributes)

    try:
        iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid_list[1],attributes)
        test_util.test_fail("can't set 2 projectAdmin in one project")
    except:
        test_util.test_dsc("can't set 2 projectAdmin in one project,success")

    attributes = [{"name": "__OrganizationSupervisor__", "value": virtual_id_uuid_list[2]}]
    iam2_ops.add_attributes_to_iam2_organization(department_01_uuid, attributes)

    try:
        attributes = [{"name": "__OrganizationSupervisor__", "value": virtual_id_uuid_list[3]}]
        iam2_ops.add_attributes_to_iam2_organization(department_01_uuid,attributes)
        test_util.test_fail("can't set 2 OrganizationSupervisor in 1 organization")
    except:
        test_util.test_dsc("can't set 2 OrganizationSupervisor in 1 organization,success")

    try:
        attributes = [{"name": "phone", "value": 'abcdefg'}]
        iam2_ops.add_attributes_to_iam2_organization(virtual_id_uuid_list[4],attributes)
        test_util.test_fail("can't set wrong phone number")
    except:
        test_util.test_dsc("can't set wrong phone number,success")

    try:
        attributes = [{"name": "mail", "value": '1234098djfghd'}]
        iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid_list[4],attributes)
        test_util.test_fail("can't set wrong mail")
    except:
        test_util.test_dsc("can't set wrong mail,success")

    iam2_ops.clean_iam2_enviroment()

    test_util.test_pass('success test iam2 admin negtive operations!')


# Will be called only if exception happens in test().
def error_cleanup():
    iam2_ops.clean_iam2_enviroment()
