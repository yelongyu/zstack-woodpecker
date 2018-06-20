'''


# 1 create PlatformAdmin
# 2 log in by PlatformAdmin
# 3 create Company
# 4 Create sub department and set virtual id as OrganizationSupervisor
# (1) not less than 5 grades
# (2) the first three levels have only one department,and the latter two have ten brothers
# (3) the first three levels have two members in each department,and the latter two levels have 20 members in each department
# 5 delete

@author: Yuling.Ren
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util

virtual_id_uuid_list = []
def test():
    global virtual_id_uuid_list

    # 1 create PlatformAdmin
    platformname = "platformadmin"
    password = "password"
    platform_admin_uuid = iam2_ops.create_iam2_virtual_id(platformname, password).uuid
    attributes = [{"name": "__PlatformAdmin__"}]
    iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin_uuid, attributes)

    # 2 log in by PlatformAdmin
    platform_admin_session_uuid = iam2_ops.login_iam2_virtual_id(platformname, password, timeout=160000)

    # 3 create Company
    company_uuid_02 = iam2_ops.create_iam2_organization('test_company_02', 'Company',
                                                        session_uuid=platform_admin_session_uuid).uuid

    # 4 Create sub department and set virtual id as OrganizationSupervisor
    department_name = "test_department"
    for i in range(1, 2):
        department1_uuid = iam2_ops.create_iam2_organization(department_name + "_" + str(i), 'Department',
                                                             parent_uuid=company_uuid_02,
                                                             session_uuid=platform_admin_session_uuid).uuid
        for n1 in range(1, 3):
            username = department_name + "_" + str(i) + "_user_" + str(n1)
            virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, 'password',
                                                              session_uuid=platform_admin_session_uuid).uuid
            iam2_ops.add_iam2_virtual_ids_to_organization([virtual_id_uuid], department1_uuid,
                                                          session_uuid=platform_admin_session_uuid)
            virtual_id_uuid_list.append(virtual_id_uuid)

        attributes = [{"name": "__OrganizationSupervisor__", "value": virtual_id_uuid}]
        iam2_ops.add_attributes_to_iam2_organization(department1_uuid, attributes,
                                                     session_uuid=platform_admin_session_uuid)
        for j in range(1, 2):
            department2_uuid = iam2_ops.create_iam2_organization(department_name + "_" + str(i) + "_" + str(j),
                                                                 'Department', parent_uuid=department1_uuid,
                                                                 session_uuid=platform_admin_session_uuid).uuid
            for n2 in range(1, 3):
                username = department_name + "_" + str(i) + "_" + str(j) + "_user_" + str(n2)
                virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, 'password',
                                                                  session_uuid=platform_admin_session_uuid).uuid
                iam2_ops.add_iam2_virtual_ids_to_organization([virtual_id_uuid], department2_uuid,
                                                              session_uuid=platform_admin_session_uuid)
                virtual_id_uuid_list.append(virtual_id_uuid)
            attributes = [{"name": "__OrganizationSupervisor__", "value": virtual_id_uuid}]
            iam2_ops.add_attributes_to_iam2_organization(department2_uuid, attributes,
                                                         session_uuid=platform_admin_session_uuid)
            for k in range(1, 2):
                department3_uuid = iam2_ops.create_iam2_organization(
                    department_name + "_" + str(i) + "_" + str(j) + "_" + str(k), 'Department',
                    parent_uuid=department2_uuid, session_uuid=platform_admin_session_uuid).uuid
                for n3 in range(1, 3):
                    username = department_name + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_user_" + str(n3)
                    virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, 'password',
                                                                      session_uuid=platform_admin_session_uuid).uuid
                    iam2_ops.add_iam2_virtual_ids_to_organization([virtual_id_uuid], department3_uuid,
                                                                  session_uuid=platform_admin_session_uuid)
                    virtual_id_uuid_list.append(virtual_id_uuid)
                attributes = [{"name": "__OrganizationSupervisor__", "value": virtual_id_uuid}]
                iam2_ops.add_attributes_to_iam2_organization(department3_uuid, attributes,
                                                             session_uuid=platform_admin_session_uuid)
                for l in range(1, 11):
                    department4_uuid = iam2_ops.create_iam2_organization(
                        department_name + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l), 'Department',
                        parent_uuid=department3_uuid, session_uuid=platform_admin_session_uuid).uuid
                    for n4 in range(1, 21):
                        username = department_name + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(
                            l) + "_user_" + str(n4)
                        virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, 'password',
                                                                          session_uuid=platform_admin_session_uuid).uuid
                        iam2_ops.add_iam2_virtual_ids_to_organization([virtual_id_uuid], department4_uuid,
                                                                      session_uuid=platform_admin_session_uuid)
                        virtual_id_uuid_list.append(virtual_id_uuid)
                    attributes = [{"name": "__OrganizationSupervisor__", "value": virtual_id_uuid}]
                    iam2_ops.add_attributes_to_iam2_organization(department4_uuid, attributes,
                                                                 session_uuid=platform_admin_session_uuid)
                    for m in range(1, 11):
                        department5_uuid = iam2_ops.create_iam2_organization(
                            department_name + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l) + "_" + str(m),
                            'Department', parent_uuid=department4_uuid, session_uuid=platform_admin_session_uuid).uuid
                        for n5 in range(1, 21):
                            username = department_name + "_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(
                                l) + "_" + str(m) + "_user_" + str(n5)
                            virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, 'password',
                                                                              session_uuid=platform_admin_session_uuid).uuid
                            iam2_ops.add_iam2_virtual_ids_to_organization([virtual_id_uuid], department5_uuid,
                                                                          session_uuid=platform_admin_session_uuid)
                            virtual_id_uuid_list.append(virtual_id_uuid)
                        attributes = [{"name": "__OrganizationSupervisor__", "value": virtual_id_uuid}]
                        iam2_ops.add_attributes_to_iam2_organization(department5_uuid, attributes,
                                                                     session_uuid=platform_admin_session_uuid)

    # 5 delete
    iam2_ops.delete_iam2_organization(company_uuid_02)
    for virtual_id_uuid in virtual_id_uuid_list:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    virtual_id_uuid_list = []
    iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)
    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass('success')

# Will be called only if exception happens in test().
def error_cleanup():
    global  company_uuid_02 , virtual_id_uuid , platform_admin_uuid
    if company_uuid_02:
        iam2_ops.delete_iam2_organization(company_uuid_02)
    if platform_admin_uuid:
        iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)
    if virtual_id_uuid_list:
        for virtual_id_uuid in virtual_id_uuid_list:
            iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    iam2_ops.clean_iam2_enviroment()