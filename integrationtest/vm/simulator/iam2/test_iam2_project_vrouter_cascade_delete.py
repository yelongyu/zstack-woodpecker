
'''
@auther:fangxiao
'''
import apibinding.api_actions as api_actions    
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vxlan_operations as vxlan_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.deploy_operations as dep_ops
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

l2_vxlan_network_uuid = None
project_uuid = None
project_operator_uuid = None
vni_range_uuid = None
vxlan_pool_uuid = None
l3_vr_network_uuid = None

dns_text = '223.5.5.5'
allservices = ["VRouterRoute","DHCP","IPsec","LoadBalancer","CentralizedDNS","Eip","DNS","SNAT","VipQos","PortForwarding"]
cond = res_ops.gen_query_conditions("type","=","vrouter")
network_service_provider_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER,cond)[0].uuid

def AddDnsToL3Network(l3_network_uuid,dns_text,session_uuid = None):
    action = api_actions.AddDnsToL3NetworkAction()
    action.sessionUuid = session_uuid
    action.dns = dns_text
    action.l3NetworkUuid = l3_network_uuid
    evt = acc_ops.execute_action_with_session(action,session_uuid)
    test_util.action_logger('add dns to l3 network: %s' % l3_network_uuid)
    return evt

    
    
def AttachNetworkServiceToL3Network(l3_network_uuid,allservices,session_uuid = None):
    action = api_actions.AttachNetworkServiceToL3NetworkAction()
    action.sessionUuid = session_uuid
    action.l3NetworkUuid = l3_network_uuid
    action.networkServices = {network_service_provider_uuid:allservices}
    evt = acc_ops.execute_action_with_session(action,session_uuid)
    test_util.action_logger('add network services to l3 network: %s' % l3_network_uuid)
    return evt

def test():
    global l2_vxlan_network_uuid,project_uuid,project_operator_uuid,vni_range_uuid,vxlan_pool_uuid,l3_vr_network_uuid

    # create vxlan pool and vni range
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.get_resource(res_ops.CLUSTER)[0].uuid
    vxlan_pool_name = 'vxlan_pool_name'

    vxlan_pool_uuid = vxlan_ops.create_l2_vxlan_network_pool(vxlan_pool_name,zone_uuid).uuid
    vxlan_ops.create_vni_range('vni_range',20,40,vxlan_pool_uuid)

    systemTags = ["l2NetworkUuid::%s::clusterUuid::%s::cidr::{172.20.0.1/16}"%(vxlan_pool_uuid,cluster_uuid)]
    net_ops.attach_l2_vxlan_pool(vxlan_pool_uuid,cluster_uuid,systemTags)

    # 1 create project
    project_name = 'test_project7'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    cond = res_ops.gen_query_conditions("name",'=',"test_project7")
    linked_account_uuid = res_ops.query_resource(res_ops.ACCOUNT,cond)[0].uuid

    # 2 create project operator
    project_operator_name = 'username7'
    project_operator_password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    project_operator_uuid = iam2_ops.create_iam2_virtual_id(project_operator_name,project_operator_password,attributes=attributes).uuid
    
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    attributes = [{"name": "__ProjectRelatedZone__", "value": zone_uuid}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)
    # 3 login in project by project operator
    iam2_ops.add_iam2_virtual_ids_to_project([project_operator_uuid],project_uuid)
    project_operator_session_uuid = iam2_ops.login_iam2_virtual_id(project_operator_name,project_operator_password)
    project_login_uuid = iam2_ops.login_iam2_project(project_name,session_uuid=project_operator_session_uuid).uuid

    # 4 share vxlan pool to project
    l2vxlan_pools = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL)
    for l2vxlan_pool in l2vxlan_pools:
        acc_ops.share_resources([linked_account_uuid],[l2vxlan_pool.uuid])
    # 5 create l2 vxlan 
    l2_vxlan_network_uuid = vxlan_ops.create_l2_vxlan_network('l2_vxlan',vxlan_pool_uuid,zone_uuid,session_uuid=project_login_uuid).uuid
    
    
    # 6 use the l2 vxlan to create l3
    # 6.1 create l3_vr_network
    l3_vr_network_uuid = net_ops.create_l3('l3_vr_network',l2_vxlan_network_uuid,session_uuid=project_login_uuid).uuid
    
    cond = res_ops.gen_query_conditions('name','=','virtual-router-vm')
    vr_instance_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING,cond)[0].uuid
    tag = "guestL3Network::" + l3_vr_network_uuid
    tag_ops.create_system_tag("InstanceOfferingVO",vr_instance_uuid,tag)
    # add ip range
    ir_option = test_util.IpRangeOption()
    ir_option.set_name('iprange1')
    ir_option.set_description('iprange for vrouter network')
    ir_option.set_netmask('255.255.255.0')
    ir_option.set_gateway('192.168.22.1')
    ir_option.set_l3_uuid(l3_vr_network_uuid)
    ir_option.set_startIp('192.168.22.2')
    ir_option.set_endIp('192.168.22.254')
    
    net_ops.add_ip_range(ir_option)
    # add dns
    AddDnsToL3Network(l3_vr_network_uuid,dns_text,session_uuid = project_login_uuid)
    # add network service
    AttachNetworkServiceToL3Network(l3_vr_network_uuid,allservices,session_uuid = project_login_uuid)
    
    # create vrouter vm 
    test_stub.share_admin_resource_include_vxlan_pool([linked_account_uuid])
    vr_vm = test_stub.create_vr_vm(test_obj_dict, l3_vr_network_uuid,session_uuid=project_login_uuid)
    test_stub.check_resource_not_exist(vr_vm.uuid,res_ops.VM_INSTANCE)
    
    #6 expunge the project and check the l2 vxlan
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)
    
    try:
        l2_vxlan_network_test_uuid = res_ops.query_resource(res_ops.L2_VXLAN_NETWORK)[0].uuid
    except: 
        
        test_util.test_pass(
            "l2 vxlan  is delete after delete the project " )
    test_util.test_dsc('test l2 l2 cascade delete')

    # 7 check the l3 vrouter network
    try:
        cond = res_ops.gen_query_conditions("name",'=',"l3_vr_network")
        l3_vrouter_network_uuid = res_ops.query_resource(res_ops.L3_NETWORK,cond)[0].uuid
    except:
        
        test_util.test_pass(
            "l3_vrouter network  is deleted after delete the project")
    
    # todo:check the virtual router vm 
    


    # 8 delete 
    vni_range_uuid = res_ops.get_resource(res_ops.VNI_RANGE)[0].uuid
    vxlan_ops.delete_vni_range(vni_range_uuid)
    net_ops.delete_l2(vxlan_pool_uuid)
    iam2_ops.delete_iam2_virtual_id(project_operator_uuid)



def error_cleanup():
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
    if project_operator_uuid:
        iam2_ops.delete_iam2_virtual_id(project_operator_uuid)
    if l2_vxlan_network_uuid:
            net_ops.delete_l2(l2_vxlan_network_uuid)
    if vni_range_uuid:
        vxlan_ops.delete_vni_range(vni_range_uuid)
    if vxlan_pool_uuid:
        net_ops.delete_l2(vxlan_pool_uuid)
    if l3_vr_network_uuid:
        net_ops.delete_l3(l3_vr_network_uuid)