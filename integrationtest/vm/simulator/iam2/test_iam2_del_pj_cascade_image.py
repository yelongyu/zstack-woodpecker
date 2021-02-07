'''
@author: yuling.ren

test for iam2 delete project cascade image

# 1 create project
# 2 create projectAdmin  into project
# 3 add image
# 4 delete project
# 5 expunge project
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.image_operations as img_ops
import os

test_stub = test_lib.lib_get_test_stub()
image=None

def test():
    global image
    iam2_ops.clean_iam2_enviroment()
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid

    # 1 create project
    project_name = 'test_project'
    password = \
        'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    linked_account_uuid = project.linkedAccountUuid
    attributes = [{"name": "__ProjectRelatedZone__", "value": zone_uuid}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)
    test_stub.share_admin_resource_include_vxlan_pool([linked_account_uuid])

    # 2 create projectAdmin  into project
    project_admin_name = 'projectadmin'
    project_admin_uuid = iam2_ops.create_iam2_virtual_id(project_admin_name, password).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid], project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)
    project_admin_session_uuid = iam2_ops.login_iam2_virtual_id(project_admin_name,password)
    project_admin_session_uuid = iam2_ops.login_iam2_project(project_name,project_admin_session_uuid).uuid
    res_ops.query_resource(res_ops.L2_VXLAN_NETWORK_POOL)

    # 3 add image
    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, bs_cond)

    image_option = test_util.ImageOption()
    image_option.set_format('iso')
    image_option.set_name('test_add_iso_image')
    image_option.set_url(os.environ.get('imageServer') + "/iso/CentOS-x86_64-7.2-Minimal.iso")
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(60000)
    image_option.set_session_uuid(project_admin_session_uuid)
    image = img_ops.add_image(image_option)

    # 4 delete project
    iam2_ops.delete_iam2_project(project_uuid)
    cond =res_ops.gen_query_conditions('uuid','=',image.uuid)
    img_inv=res_ops.query_resource(res_ops.IMAGE,cond)
    if not img_inv:
        test_util.test_fail("can't query image %s after delete the project,test fail"%image.uuid)

    # 5 expunge project
    iam2_ops.expunge_iam2_project(project_uuid)
    cond = res_ops.gen_query_conditions('uuid','=',image.uuid)
    img_inv = res_ops.query_resource(res_ops.IMAGE,cond)[0]
    if img_inv.status != 'Deleted':
        test_util.test_fail('The image created in project is not deleted after project is expunge, test fail')

    img_ops.expunge_image(image.uuid)
    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass('success')

# Will be called only if exception happens in test().
def error_cleanup():
    global image
    iam2_ops.clean_iam2_enviroment()
    if image:
        try:
            img_ops.delete_image(image.uuid)
        except:
            img_ops.expunge_image(image.uuid)
