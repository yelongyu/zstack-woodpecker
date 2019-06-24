'''
Test for iam2 delete project cascade net services.
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as test_sg_header
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as test_sg_vm_header
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as test_pf_header
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_load_balancer as zstack_lb_header
import apibinding.inventory as inventory
import os

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    # global test_obj_dict
    iam2_ops.clean_iam2_enviroment()

    global project_uuid,virtual_id_uuid,project_admin_uuid
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


    #create Security Group
    sg = test_sg_header.ZstackTestSecurityGroup()
    sg_creation_option = test_util.SecurityGroupOption()
    sg_creation_option.set_name('test_sg')
    sg_creation_option.session_uuid = project_admin_session_uuid
    sg.set_creation_option(sg_creation_option)
    sg.create()
    test_obj_dict.add_sg(sg.get_security_group().uuid)
    
    #create EIP
    vm = test_stub.create_vm(session_uuid=project_admin_session_uuid)
    test_obj_dict.add_vm(vm)
    pri_l3_name = os.environ.get('l3VlanNetworkName3')
    if test_lib.lib_get_l3_by_name(pri_l3_name) == None:
        error_cleanup()
        test_util.test_skip('Skip in no private env.')
    else:
        pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid
    pub_l3_name = os.environ.get('l3PublicNetworkName')
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid
    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    vip_for_eip = test_stub.create_vip('create_eip_test', pub_l3_uuid,session_uuid=project_admin_session_uuid)
    test_obj_dict.add_vip(vip_for_eip)
    eip = test_stub.create_eip(vip_uuid=vip_for_eip.get_vip().uuid ,eip_name='create eip test', vnic_uuid=vm_nic_uuid, vm_obj=vm,session_uuid=project_admin_session_uuid)
    vip_for_eip.attach_eip(eip)

    # create LB
    vip_for_lb = test_stub.create_vip('create_lb_test', pub_l3_uuid,session_uuid=project_admin_session_uuid)
    test_obj_dict.add_vip(vip_for_lb)
    lb = zstack_lb_header.ZstackTestLoadBalancer()
    lb.create('create lb test', vip_for_lb.get_vip().uuid,session_uuid=project_admin_session_uuid)
    test_obj_dict.add_load_balancer(lb)
    vip_for_lb.attach_lb(lb)
    lb_creation_option = test_lib.lib_create_lb_listener_option(lbl_port = 222, lbi_port = 22)
    lb_creation_option.set_session_uuid(project_admin_session_uuid)
    lbl = lb.create_listener(lb_creation_option)

    # test PF
    vip_for_pf = test_stub.create_vip('create_pf_test', pub_l3_uuid,session_uuid=project_admin_session_uuid)
    test_obj_dict.add_vip(vip_for_pf)
    vr_list = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)
    if len(vr_list) < 1:
        error_cleanup()
        test_util.test_skip("skip the test for no vr found in the env.")
    else:
        vr = vr_list[0]
    vr_pub_ip = test_lib.lib_find_vr_pub_ip(vr)
    pf_creation_opt = PfRule.generate_pf_rule_option(vr_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip_for_pf.get_vip().uuid)
    pf_creation_opt.set_session_uuid(project_admin_session_uuid)
    pf = test_pf_header.ZstackTestPortForwarding()
    pf.set_creation_option(pf_creation_opt)
    pf.create()
    vip_for_pf.attach_pf(pf)

    # delete project
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)

    test_stub.check_resource_not_exist(eip.get_eip().uuid,res_ops.EIP)
    test_stub.check_resource_not_exist(sg.get_security_group().uuid,res_ops.SECURITY_GROUP)
    test_stub.check_resource_not_exist(lb.get_load_balancer().uuid,res_ops.LOAD_BALANCER)
    test_stub.check_resource_not_exist(lbl.get_load_balancer_listener().uuid,res_ops.LOAD_BALANCER_LISTENER)
    test_stub.check_resource_not_exist(pf.get_port_forwarding().uuid,res_ops.PORT_FORWARDING)

    test_lib.lib_robot_cleanup(test_obj_dict)
    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass("Test for iam2 delete project cascade net services success.")

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
    iam2_ops.clean_iam2_enviroment()
    
