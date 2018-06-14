'''

Network Security Group operations for test.

@author: Youyk
'''

import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.deploy_operations as dep_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.xmlobject as xmlobject

import os
import sys
import traceback

def create_security_group(sg_creation_option):
    action = api_actions.CreateSecurityGroupAction()
    if not sg_creation_option.get_name():
        action.name = 'test_sg'
    else:
        action.name = sg_creation_option.get_name()
        
    if not sg_creation_option.get_description():
        action.description = 'Test Security Group'
    else:
        action.description = sg_creation_option.get_description()

    if not sg_creation_option.get_timeout():
        action.timeout = 120000
    else:
        action.timeout = sg_creation_option.get_timeout()
    
    test_util.action_logger('Create [Security Group]: %s' % action.name)
    evt = acc_ops.execute_action_with_session(action, sg_creation_option.get_session_uuid())
    test_util.test_logger('[sg:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def delete_security_group(sg_uuid, session_uuid=None):
    action = api_actions.DeleteSecurityGroupAction()
    action.uuid = sg_uuid
    action.timeout = 12000
    test_util.action_logger('Delete [Security Group:] %s' % sg_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

#rules = [inventory.SecurityGroupRuleAO()]
def add_rules_to_security_group(sg_uuid, rules, remote_sg_uuids=None, session_uuid=None):
    action = api_actions.AddSecurityGroupRuleAction()
    action.securityGroupUuid = sg_uuid
    if remote_sg_uuids != None:
        action.remoteSecurityGroupUuids = remote_sg_uuids
    action.timeout = 120000
    action.rules = rules
    for rule in rules:
        test_util.action_logger('Add Security Group [Rule:] type: %s, protocol: %s, startPort: %s, endPort: %s, address: %s in [Security Group:] %s' % (rule.type, rule.protocol, rule.startPort, rule.endPort, rule.allowedCidr, sg_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

#rules = [rules_uuid]
def remove_rules_from_security_group(rules, session_uuid=None):
    '''
    params: rules is a list includes a list of rules uuids. 
    '''
    action = api_actions.DeleteSecurityGroupRuleAction()
    action.timeout = 12000
    action.ruleUuids = rules
    test_util.action_logger('Delete Security Group [Rules:] %s' % rules)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_nic_to_security_group(sg_uuid, vm_nic_list, session_uuid=None):
    action = api_actions.AddVmNicToSecurityGroupAction()
    action.securityGroupUuid = sg_uuid
    action.vmNicUuids = vm_nic_list
    action.timeout = 120000
    test_util.action_logger('Add [Nics:] %s to [Security Group:] %s' \
            % (vm_nic_list, sg_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def remove_nic_from_security_group(sg_uuid, nic_uuid_list, session_uuid=None):
    action = api_actions.DeleteVmNicFromSecurityGroupAction()
    action.securityGroupUuid = sg_uuid
    action.vmNicUuids = nic_uuid_list
    action.timeout = 12000
    test_util.action_logger('Delete [Nics:] %s From [Security Group:] %s' \
            % (nic_uuid_list, sg_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def attach_security_group_to_l3(sg_uuid, l3_uuid, session_uuid=None):
    action = api_actions.AttachSecurityGroupToL3NetworkAction()
    action.securityGroupUuid = sg_uuid
    action.l3NetworkUuid = l3_uuid
    action.timeout = 12000
    test_util.action_logger('Attach [Security Group:] %s to [l3:] %s' % (sg_uuid, l3_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def detach_security_group_from_l3(sg_uuid, l3_uuid, session_uuid=None):
    action = api_actions.DetachSecurityGroupFromL3NetworkAction()
    action.l3NetworkUuid = l3_uuid
    action.securityGroupUuid = sg_uuid
    action.timeout = 12000
    test_util.action_logger('Detach [Security Group:] %s from [l3:] %s' % (sg_uuid, l3_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def create_vip(vip_creation_option):
    action = api_actions.CreateVipAction()
    action.l3NetworkUuid = vip_creation_option.get_l3_uuid()
    action.allocateStrategy = vip_creation_option.get_allocateStrategy()
    action.requiredIp = vip_creation_option.get_requiredIp()
    action.timeout = vip_creation_option.get_timeout()
    #mandatory vip name:
    name = vip_creation_option.get_name()
    if not name:
        action.name = 'vip_test'
    else:
        action.name = name

    session_uuid = vip_creation_option.get_session_uuid()
    action.description = vip_creation_option.get_description()
    evt = acc_ops.execute_action_with_session(action, session_uuid).inventory
    test_util.action_logger('Create [VIP:] %s [IP:] %s in [l3:] %s' % (evt.uuid, evt.ip, action.l3NetworkUuid))
    return evt

def get_snat_ip_as_vip(snat_ip):
    conditions = res_ops.gen_query_conditions('ip', '=', snat_ip)
    vip = res_ops.query_resource(res_ops.VIP, conditions)
    test_util.action_logger('Get SNAT [VIP:] %s [IP:] %s' % (vip[0].uuid, vip[0].ip))
    return vip[0]

def delete_vip(vip_uuid, session_uuid=None):
    action = api_actions.DeleteVipAction()
    action.uuid = vip_uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[VIP]: %s is deleted" % vip_uuid)
    return evt

def set_vip_qos(vip_uuid, inboundBandwidth=None, outboundBandwidth=None, port=None, session_uuid=None):
    action = api_actions.SetVipQosAction()
    action.uuid = vip_uuid
    action.port = port
    action.inboundBandwidth = inboundBandwidth
    action.outboundBandwidth = outboundBandwidth
    action.timeout = 12000
    test_util.action_logger("SetVipQos [vip:] %s [inboundBandwidth: ] %s [outboundBandwidth: ] %s [port: ] %s" % (vip_uuid, inboundBandwidth, outboundBandwidth, port))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def get_vip_qos(vip_uuid, session_uuid=None):
    action = api_actions.GetVipQosAction()
    action.uuid = vip_uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("GetVipQos [vip:] %s" % vip_uuid)
    return evt.inventories

def delete_vip_qos(vip_uuid, port=None, session_uuid=None):
    action = api_actions.DeleteVipQosAction()
    action.uuid = vip_uuid
    action.port = port
#     action.direction = direction
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("DeleteVipQos [vip:] %s is deleted" % vip_uuid)
    return evt

def create_port_forwarding(pf_rule_creation_option):
    action = api_actions.CreatePortForwardingRuleAction()
    action.name = pf_rule_creation_option.get_name()
    if not action.name:
        action.name = 'test_port_forwarding_rule'

    action.timeout = pf_rule_creation_option.get_timeout()
    if not action.timeout:
        action.timeout = 12000

    action.description = pf_rule_creation_option.get_description()
    session_uuid = pf_rule_creation_option.get_session_uuid()

    action.vipPortStart, action.vipPortEnd = pf_rule_creation_option.get_vip_ports()
    action.privatePortStart, action.privatePortEnd = pf_rule_creation_option.get_private_ports()
    if not action.privatePortStart:
        action.privatePortStart = action.vipPortStart
        action.privatePortEnd = action.vipPortEnd

    action.vipUuid = pf_rule_creation_option.get_vip_uuid()
    action.vmNicUuid = pf_rule_creation_option.get_vm_nic_uuid()
    action.allowedCidr = pf_rule_creation_option.get_allowedCidr()
    action.protocolType = pf_rule_creation_option.get_protocol()
    test_util.action_logger("Create Port Forwarding Rule: [vipUuid:] %s [vm nic:] %s [vip start:] %s [vip end:] %s [pri start:] %s [pri end:] %s [allowedCidr:] %s" % (action.vipUuid, action.vmNicUuid, action.vipPortStart, action.vipPortEnd, action.privatePortStart, action.privatePortEnd, action.allowedCidr))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_port_forwarding(pf_rule_uuid, session_uuid=None):
    action = api_actions.DeletePortForwardingRuleAction()
    action.uuid = pf_rule_uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("Port Forwarding Rule [uuid:] %s is deleted" % pf_rule_uuid)
    return evt

def attach_port_forwarding(pf_rule_uuid, vm_nic_uuid, session_uuid=None):
    action = api_actions.AttachPortForwardingRuleAction()
    action.ruleUuid = pf_rule_uuid
    action.vmNicUuid = vm_nic_uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("Port Forwarding Rule [uuid:] %s is attached to %s" % (pf_rule_uuid, vm_nic_uuid))
    return evt.inventory

def detach_port_forwarding(pf_rule_uuid, session_uuid=None):
    action = api_actions.DetachPortForwardingRuleAction()
    action.uuid = pf_rule_uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("Port Forwarding Rule [uuid:] %s is detached" % pf_rule_uuid)
    return evt.inventory

def create_eip(eip_creation_option):
    action = api_actions.CreateEipAction()
    action.vipUuid = eip_creation_option.get_vip_uuid()
    action.vmNicUuid = eip_creation_option.get_vm_nic_uuid()
    action.name = eip_creation_option.get_name()
    if not action.name:
        action.name = 'eip test'
    action.description = eip_creation_option.get_description()
    action.timeout = eip_creation_option.get_timeout()
    if not action.timeout:
        action.timeout = 12000

    session_uuid = eip_creation_option.get_session_uuid()
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[EIP:] %s is created, with [vip:] %s and [nic:] %s" % (evt.inventory.uuid, action.vipUuid, action.vmNicUuid))
    return evt.inventory

def attach_eip(eip_uuid, nic_uuid, session_uuid=None):
    action = api_actions.AttachEipAction()
    action.eipUuid = eip_uuid
    action.vmNicUuid = nic_uuid
    action.timeout = 120000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[EIP:] %s is attached to [nic:] %s" % (eip_uuid, nic_uuid))
    return evt.inventory

def detach_eip(eip_uuid, session_uuid=None):
    action = api_actions.DetachEipAction()
    action.uuid = eip_uuid
    action.timeout = 12000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[EIP:] %s is detached" % eip_uuid)
    return evt.inventory

def delete_eip(eip_uuid, session_uuid=None):
    action = api_actions.DeleteEipAction()
    action.uuid = eip_uuid
    action.timeout = 12000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[EIP:] %s is deleted" % eip_uuid)
    return evt

def create_l2_novlan(name, nic, zone_uuid, session_uuid = None):
    '''
    Delete L2 will stop all VMs which is using this L2. When VM started again, 
    the related L2 NIC will be removed. 
    '''
    action = api_actions.CreateL2NoVlanNetworkAction()
    action.name = name
    action.physicalInterface = nic
    action.zoneUuid = zone_uuid
    action.timeout = 300000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[Novlan L2:] %s is created" % evt.uuid)
    return evt   

def create_l2_vlan(name, nic, zone_uuid, vlan, session_uuid = None):
    '''
    Delete L2 will stop all VMs which is using this L2. When VM started again, 
    the related L2 NIC will be removed. 
    '''
    action = api_actions.CreateL2VlanNetworkAction()
    action.name = name
    action.physicalInterface = nic
    action.vlan = vlan
    action.zoneUuid = zone_uuid
    action.timeout = 300000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[Vlan L2:] %s is created" % evt.uuid)
    return evt   

def delete_l2(l2_uuid, session_uuid = None):
    '''
    Delete L2 will stop all VMs which is using this L2. When VM started again, 
    the related L2 NIC will be removed. 
    '''
    action = api_actions.DeleteL2NetworkAction()
    action.uuid = l2_uuid
    action.timeout = 300000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[L2:] %s is deleted" % l2_uuid)
    return evt

def set_l3_mtu(l3_uuid, mtu, session_uuid = None):
    action = api_actions.SetL3NetworkMtuAction()
    action.l3NetworkUuid = l3_uuid
    action.mtu = mtu
    action.timeout = 300000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("Set [L3:] %s [mtu:] %s" % (l3_uuid, mtu))

def get_l3_mtu(l3_uuid, session_uuid = None):
    action = api_actions.GetL3NetworkMtuAction()
    action.l3NetworkUuid = l3_uuid
    action.timeout = 300000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("Get [L3:] %s mtu" % l3_uuid)
    return evt.mtu

def delete_l3(l3_uuid, session_uuid = None):
    '''
    Delete L3 will stop all VMs which is using this L3. When VM started again, 
    the related L3 NIC will be removed. 
    '''
    action = api_actions.DeleteL3NetworkAction()
    action.uuid = l3_uuid
    action.timeout = 300000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[L3:] %s is deleted" % l3_uuid)
    return evt

def attach_l2(l2_uuid, cluster_uuid, session_uuid = None):
    action = api_actions.AttachL2NetworkToClusterAction()
    action.clusterUuid = cluster_uuid
    action.l2NetworkUuid = l2_uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("Attach [L2:] %s to [Cluster:] %s " \
            % (l2_uuid, cluster_uuid))
    return evt

def add_l2_resource(deploy_config, l2_name, zone_name = None, \
        session_uuid = None):
    session_uuid_flag = True
    if not session_uuid:
        session_uuid = acc_ops.login_as_admin()
        session_uuid_flag = False
    try:
        dep_ops.add_l2_network(deploy_config, session_uuid, l2_name, \
                zone_name = zone_name)
        l2_uuid = res_ops.get_resource(res_ops.L2_NETWORK, session_uuid, \
                name = l2_name)[0].uuid
        
        for zone in xmlobject.safe_list(deploy_config.zones.zone):
            if zone_name and zone_name != zone.name_:
                continue
            for cluster in xmlobject.safe_list(zone.clusters.cluster):
                if xmlobject.has_element(cluster, 'l2NetworkRef'):
                    for l2ref in xmlobject.safe_list(cluster.l2NetworkRef):
                        if l2_name != l2ref.text_:
                            continue

                        cluster_uuid = res_ops.get_resource(res_ops.CLUSTER, \
                                session_uuid, name=cluster.name_)[0].uuid
                        attach_l2(l2_uuid, cluster_uuid, session_uuid)

        dep_ops.add_l3_network(None, None, deploy_config, session_uuid, l2_name = l2_name, \
                zone_name = zone_name)
        cond = res_ops.gen_query_conditions('l2NetworkUuid', '=', l2_uuid)
        l3_name = res_ops.query_resource(res_ops.L3_NETWORK, cond, \
                session_uuid)[0].name
        dep_ops.add_virtual_router(None, None, deploy_config, session_uuid, \
                l3_name = l3_name, zone_name = zone_name)
    except Exception as e:
        test_util.test_logger('[Error] zstack deployment meets exception when adding l2 resource .')
        traceback.print_exc(file=sys.stdout)
        raise e
    finally:
        if not session_uuid_flag:
            acc_ops.logout(session_uuid)

    test_util.action_logger('Complete add l2 resources for [uuid:] %s' \
            % l2_uuid)

def add_l3_resource(deploy_config, l3_name, l2_name = None, zone_name = None, \
        session_uuid = None):
    session_uuid_flag = True
    if not session_uuid:
        session_uuid = acc_ops.login_as_admin()
        session_uuid_flag = False
    try:
        dep_ops.add_l3_network(None, None, deploy_config, session_uuid, l3_name = l3_name, \
                l2_name = l2_name, zone_name = zone_name)
        dep_ops.add_virtual_router(None, None, deploy_config, session_uuid, \
                l3_name = l3_name, zone_name = zone_name)
        l3_uuid = res_ops.get_resource(res_ops.L3_NETWORK, session_uuid, \
                name = l3_name)[0].uuid
    except Exception as e:
        test_util.test_logger('[Error] zstack deployment meets exception when adding l3 resource .')
        traceback.print_exc(file=sys.stdout)
        raise e
    finally:
        if not session_uuid_flag:
            acc_ops.logout(session_uuid)

    test_util.action_logger('Complete add l3 resources for [uuid:] %s' \
            % l3_uuid)

def delete_ip_range(ip_range_uuid, session_uuid = None):
    action = api_actions.DeleteIpRangeAction()
    action.sessionUuid = session_uuid
    action.uuid = ip_range_uuid
    action.timeout = 300000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[IP Range:] %s is deleted" % ip_range_uuid)
    return evt

def add_ip_range(ip_range_option, session_uuid = None):
    action = api_actions.AddIpRangeAction()
    action.sessionUuid = session_uuid
    action.timeout = 30000
    action.name = ip_range_option.get_name()
    action.startIp = ip_range_option.get_startIp()
    action.endIp = ip_range_option.get_endIp()
    action.netmask = ip_range_option.get_netmask()
    action.gateway = ip_range_option.get_gateway()
    action.l3NetworkUuid = ip_range_option.get_l3_uuid()
    action.description = ip_range_option.get_description()
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger("[IP Range:] %s is add" % evt.inventory.uuid)
    return evt.inventory

def detach_l2(l2_uuid, cluster_uuid, session_uuid = None):
    action = api_actions.DetachL2NetworkFromClusterAction()
    action.sessionUuid = session_uuid
    action.timeout = 90000
    action.l2NetworkUuid = l2_uuid
    action.clusterUuid = cluster_uuid
    test_util.action_logger('Detach [l2:] %s from [cluster:] %s' % \
            (l2_uuid, cluster_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def get_ip_capacity_by_l3s(l3_network_list, session_uuid = None):
    action = api_actions.GetIpAddressCapacityAction()
    action.l3NetworkUuids = l3_network_list
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Get L3s: [%s] IP Capacity' % \
            l3_network_list)
    return evt
    
def get_free_ip(l3_uuid = None, ip_range = None, limit = 1, \
        session_uuid = None):
    action = api_actions.GetFreeIpAction()
    action.l3NetworkUuid = l3_uuid
    action.ipRangeUuid = ip_range
    action.limit = limit
    test_util.action_logger('Get free IP from [L3:] %s, in [IP Range:] %s with [limit:] %d ' % \
            (l3_uuid, ip_range, limit))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    print evt.ip
    import time
    time.sleep(1)
    test_util.test_logger('Get a free IP: %s from L3: %s' % \
            (evt.inventories[0].ip, l3_uuid))
    return evt.inventories

def attach_l3(l3_uuid, vm_uuid, session_uuid = None):
    action = api_actions.AttachL3NetworkToVmAction()
    action.l3NetworkUuid = l3_uuid
    action.vmInstanceUuid = vm_uuid
    test_util.action_logger('[Attach L3 Network:] %s to [VM:] %s' % \
            (l3_uuid, vm_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[L3 Network:] %s has been attached to [VM:] %s' % \
            (l3_uuid, vm_uuid))
    return evt.inventory

def detach_l3(nic_uuid, session_uuid = None):
    action = api_actions.DetachL3NetworkFromVmAction()
    action.vmNicUuid = nic_uuid
    test_util.action_logger('[Detach L3 Network Nic]: %s' % nic_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[L3 Network Nic]: %s has been detached'% nic_uuid)
    return evt.inventory

def create_load_balancer(vip_uuid, name, separated_vr = False, \
        session_uuid = None):
    action = api_actions.CreateLoadBalancerAction()
    action.vipUuid = vip_uuid
    action.name = name
    if separated_vr:
        action.systemTags = ['separateVirtualRouterVm']

    test_util.action_logger('[Create Load Balancer:] %s with [VIP]: %s' %\
            (name, vip_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Load Balancer]: %s has been created' % \
            evt.inventory.uuid)
    return evt.inventory

def delete_load_balancer(lb_uuid, session_uuid = None):
    action = api_actions.DeleteLoadBalancerAction()
    action.uuid = lb_uuid
    test_util.action_logger('[Delete Load Balancer:] %s' % lb_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Load Balancer]: %s has been deleted' % \
            lb_uuid)
    return evt

def create_load_balancer_listener(lb_listener_option):
    action = api_actions.CreateLoadBalancerListenerAction()
    action.loadBalancerUuid = lb_listener_option.get_load_balancer_uuid()
    action.name = lb_listener_option.get_name()
    action.loadBalancerPort = lb_listener_option.get_load_balancer_port()
    action.protocol = lb_listener_option.get_protocol()
    action.instancePort = lb_listener_option.get_instance_port()
    action.systemTags = lb_listener_option.get_system_tags()
    test_util.action_logger('[Create Load Balancer Listener:] %s with [Port]:\
%s [Protocol]: %s on [LB]: %s' %\
            (action.name, action.loadBalancerPort, \
            action.protocol, action.loadBalancerUuid))
    evt = acc_ops.execute_action_with_session(action, lb_listener_option.get_session_uuid())
    test_util.test_logger('[Load Balancer Listener]: %s has been created' % \
            evt.inventory.uuid)
    return evt.inventory

def delete_load_balancer_listener(lbl_uuid, session_uuid = None):
    action = api_actions.DeleteLoadBalancerListenerAction()
    action.uuid = lbl_uuid
    test_util.action_logger('[Delete Load Balancer Listener:] %s' % lbl_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Load Balancer Listener]: %s has been deleted' % \
            lbl_uuid)
    return evt

def add_nic_to_load_balancer(lb_listener_uuid, vm_nics_uuid_list, \
        session_uuid = None):
    action = api_actions.AddVmNicToLoadBalancerAction()
    action.listenerUuid = lb_listener_uuid
    action.vmNicUuids = vm_nics_uuid_list
    test_util.action_logger('[Add Nics:] %s to [load balancer listener]: %s '% \
            (vm_nics_uuid_list, lb_listener_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Nics]: %s have been added to load balancer listener: %s ' % \
            (vm_nics_uuid_list, lb_listener_uuid))
    return evt.inventory

def remove_nic_from_load_balancer(lb_listener_uuid, vm_nics_uuid_list, \
        session_uuid = None):
    action = api_actions.RemoveVmNicFromLoadBalancerAction()
    action.listenerUuid = lb_listener_uuid
    action.vmNicUuids = vm_nics_uuid_list
    test_util.action_logger('[Remove Nics:] %s from [load balancer listener]: %s '% \
            (vm_nics_uuid_list, lb_listener_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('[Nics]: %s have been removed from load balancer listener: %s ' % \
            (vm_nics_uuid_list, lb_listener_uuid))
    return evt.inventory

def refresh_load_balancer(lb_uuid, session_uuid = None):
    action = api_actions.RefreshLoadBalancerAction()
    action.uuid = lb_uuid
    test_util.action_logger('[Refresh Load Balancer]: %s '%  lb_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_vrouter_route_table(name=None, session_uuid = None):
    if name == None:
        name = 'vrouter_route_table'
    action = api_actions.CreateVRouterRouteTableAction()
    action.name = name
    action.timeout = 120000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Create [VRouter Route Table]: %s' % name)
    return evt.inventory

def delete_vrouter_route_table(vrrt_uuid, session_uuid=None):
    action = api_actions.DeleteVRouterRouteTableAction()
    action.uuid = vrrt_uuid
    action.timeout = 12000
    test_util.action_logger('Delete [VRouter Route Table]: %s' % vrrt_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def attach_vrouter_route_table_to_vrouter(route_table_uuid, virtual_router_vm_uuid, session_uuid=None):
    action = api_actions.AttachVRouterRouteTableToVRouterAction()
    action.routeTableUuid = route_table_uuid
    action.virtualRouterVmUuid = virtual_router_vm_uuid
    action.timeout = 12000
    test_util.action_logger('Attach [VRouter Route Table]: %s to [VirtualRouter]: %s' % (route_table_uuid, virtual_router_vm_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def detach_vrouter_route_table_from_vrouter(route_table_uuid, virtual_router_vm_uuid, session_uuid=None):
    action = api_actions.DetachVRouterRouteTableFromVRouterAction()
    action.routeTableUuid = route_table_uuid
    action.virtualRouterVmUuid = virtual_router_vm_uuid
    action.timeout = 12000
    test_util.action_logger('Detach [VRouter Route Table]: %s from [VirtualRouter]: %s' % (route_table_uuid, virtual_router_vm_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def add_vrouter_route_entry(route_table_uuid, destination, target, \
        session_uuid = None):
    action = api_actions.AddVRouterRouteEntryAction()
    action.routeTableUuid = route_table_uuid
    action.destination = destination
    action.target = target
    action.timeout = 120000
    test_util.action_logger('Add [VRouter Route Entry]:')
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_vrouter_route_entry(vrre_uuid, vrrt_uuid, session_uuid=None):
    action = api_actions.DeleteVRouterRouteEntryAction()
    action.uuid = vrre_uuid
    action.routeTableUuid = vrrt_uuid
    action.timeout = 12000
    test_util.action_logger('Delete [VRouter Route Entry]: %s from [VRouter Route Table]: %s' % (vrre_uuid, vrrt_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def attach_network_service_to_l3network(l3_uuid, service_uuid, session_uuid=None):
    providers = {}
    action = api_actions.AttachNetworkServiceToL3NetworkAction()
    action.l3NetworkUuid = l3_uuid
    providers[service_uuid] = ['VRouterRoute'] 
    action.networkServices = providers
    action.timeout = 12000
    test_util.action_logger('Attach [Network Service]: %s to [l3]: %s' % (service_uuid, l3_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def detach_network_service_from_l3network(l3_uuid, service_uuid, session_uuid=None):
    providers = {}
    action = api_actions.DetachNetworkServiceFromL3NetworkAction()
    action.l3NetworkUuid = l3_uuid
    providers[service_uuid] = ['VRouterRoute']
    action.networkServices = providers
    action.timeout = 12000
    test_util.action_logger('Detach [Network Service]: %s from [l3]: %s' % (service_uuid, l3_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)

def attach_eip_service_to_l3network(l3_uuid, service_uuid, session_uuid=None):
    providers = {}
    action = api_actions.AttachNetworkServiceToL3NetworkAction()
    action.l3NetworkUuid = l3_uuid
    providers[service_uuid] = ['Eip'] 
    action.networkServices = providers
    action.timeout = 12000
    test_util.action_logger('Attach [Eip Service]: %s to [l3]: %s' % (service_uuid, l3_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt

def detach_eip_service_from_l3network(l3_uuid, service_uuid, session_uuid=None):
    providers = {}
    action = api_actions.DetachNetworkServiceFromL3NetworkAction()
    action.l3NetworkUuid = l3_uuid
    providers[service_uuid] = ['Eip']
    action.networkServices = providers
    action.timeout = 12000
    test_util.action_logger('Detach [Eip Service]: %s from [l3]: %s' % (service_uuid, l3_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)

def create_virtual_router_offering(name, cpuNum, memorySize, imageUuid, zoneUuid, managementNetworkUuid, publicNetworkUuid=None, description=None, allocatorStrategy=None, offeringType=None, session_uuid = None):
    action = api_actions.CreateVirtualRouterOfferingAction()
    action.name = name
    action.cpuNum = cpuNum
    action.memorySize = memorySize
    action.imageUuid = imageUuid
    action.zoneUuid = zoneUuid
    action.managementNetworkUuid = managementNetworkUuid
    if publicNetworkUuid != None:
        action.publicNetworkUuid = publicNetworkUuid
    else:
        action.publicNetworkUuid = managementNetworkUuid
    if description != None:
        action.description = description
    if allocatorStrategy != None:
        action.allocatorStrategy = allocatorStrategy
    if offeringType != None:
        action.type = offeringType
    action.timeout = 12000
    test_util.action_logger('create virtual router offering: name: %s cpuNum: %s, memorySize: %s,\
             publicNetworkUuid: %s, managementNetworkUuid: %s, imageUuid: %s '\
            % (action.name, action.cpuNum, action.memorySize,\
             action.publicNetworkUuid, action.managementNetworkUuid, action.imageUuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Virtual Router Offering: %s is created' % evt.inventory.uuid)
    return evt.inventory

def get_l3network_router_interface_ip(l3NetworkUuid, systemTags=None, userTags=None, session_uuid=None):
    action = api_actions.GetL3NetworkRouterInterfaceIpAction()
    action.l3NetworkUuid = l3NetworkUuid
    if systemTags:
        action.systemTags = systemTags
    if userTags:
        action.userTags = userTags
    action.timeout = 12000
    test_util.test_logger('Get l3 network router interface ip from L3 uuid: {}'.format(l3NetworkUuid))
    result = acc_ops.execute_action_with_session(action, session_uuid)
    return result.routerInterfaceIp

def set_l3network_router_interface_ip(l3NetworkUuid, routerInterfaceIp, systemTags=None, userTags=None, session_uuid=None):
    action = api_actions.SetL3NetworkRouterInterfaceIpAction()
    action.l3NetworkUuid = l3NetworkUuid
    action.routerInterfaceIp = routerInterfaceIp
    if systemTags:
        action.systemTags = systemTags
    if userTags:
        action.userTags = userTags
    action.timeout = 12000
    test_util.test_logger('Set l3 network router interface ip for L3 uuid: {}'.format(l3NetworkUuid))
    result = acc_ops.execute_action_with_session(action, session_uuid)
    return result.success

def destroy_vrouter(vrouter_uuid, session_uuid=None):
    action = api_actions.DestroyVmInstanceAction()
    action.uuid = vrouter_uuid
    action.timeout = 12000
    test_util.test_logger('Destroy vRouter uuid: {}'.format(vrouter_uuid))
    result = acc_ops.execute_action_with_session(action, session_uuid)
    return result.success

def create_certificate(name, certificate, session_uuid = None):
    action = api_actions.CreateCertificateAction()
    action.name = name
    action.certificate = certificate
    action.timeout = 120000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Create [Certificate]: %s' % name)
    return evt.inventory

def delete_certificate(uuid, session_uuid = None):
    action = api_actions.DeleteCertificateAction()
    action.uuid = uuid
    action.timeout = 120000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Delete [Certificate]: %s' % uuid)
    return evt.inventory

