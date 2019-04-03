import apibinding.api_actions as api_actions
import account_operations
import apibinding.inventory as inventory
import zstackwoodpecker.operations.resource_operations as res_ops
import net_operations as net_ops
import vm_operations as vm_ops



def create_vrouter_ospf_area(areaId='0.0.0.0', areaType='Standard', areaAuth=None, password=None, keyId=None, session_uuid=None):
    action = api_actions.CreateVRouterOspfAreaAction()
    action.timeout = 300000
    action.areaId = areaId
    action.areaType = areaType
    action.areaAuth = areaAuth
    action.password = password
    action.keyId = keyId
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_vrouter_ospf_area(uuid, areaType, areaAuth, password, keyId, session_uuid=None):
    action = api_actions.UpdateVRouterOspfAreaAction()
    action.timeout = 300000
    action.uuid = uuid
    action.areaType = areaType
    action.areaAuth = areaAuth
    action.password = password
    action.keyId = keyId
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_vrouter_ospf_area(uuid, session_uuid=None):
    action = api_actions.DeleteVRouterOspfAreaAction()
    action.timeout = 300000
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def query_vrouter_ospf_area(areaId=None, session_uuid=None):
    action = api_actions.QueryVRouterOspfAreaAction()
    action.timeout = 300000
    action.areaId = areaId
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_vrouter_networks_to_ospf_area(vRouterUuid, l3NetworkUuids, routerAreaUuid, session_uuid=None):
    action = api_actions.AddVRouterNetworksToOspfAreaAction()
    action.timeout = 300000
    action.vRouterUuid = vRouterUuid
    action.l3NetworkUuids = l3NetworkUuids
    action.routerAreaUuid = routerAreaUuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def remove_vrouter_networks_from_ospf_area(uuids, vrouter, session_uuid=None):
    action = api_actions.RemoveVRouterNetworksFromOspfAreaAction()
    action.timeout = 300000
    action.uuids = uuids
    action.vrouter = vrouter
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def query_vrouter_ospf_network(session_uuid=None):
    action = api_actions.QueryVRouterOspfNetworkAction()
    action.timeout = 300000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def set_vrouter_router_id(uuid, routerId, session_uuid=None):
    action = api_actions.SetVRouterRouterIdAction()
    action.timeout = 300000
    action.uuid = uuid
    action.routerId = routerId
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_vrouter_router_id(uuid, session_uuid=None):
    action = api_actions.GetVRouterRouterIdAction()
    action.timeout = 300000
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_vrouter_route_table(session_uuid=None):
    action = api_actions.GetVRouterRouteTableAction()
    action.timeout = 300000
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_vrouter_ospf_neighbor(vRouterUuid, session_uuid=None):
    action = api_actions.GetVRouterOspfNeighborAction()
    action.timeout = 300000
    action.vRouterUuid = vRouterUuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.neighbors

def set_vpc_vrouter_network_service_state(uuid, networkService='SNAT', state=None, session_uuid=None):
    action = api_actions.SetVpcVRouterNetworkServiceStateAction()
    action.timeout = 300000
    action.uuid = uuid
    action.networkService = networkService
    action.state = state
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_vpc_vrouter_network_service_state(uuid, networkService='SNAT', session_uuid=None):
    action = api_actions.GetVpcVRouterNetworkServiceStateAction()
    action.timeout = 300000
    action.uuid = uuid
    action.networkService = networkService
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.state

def create_vpc_vrouter(name, virtualrouter_offering_uuid, resource_uuid=None, system_tags=None, use_tags=None, session_uuid=None):
    action = api_actions.CreateVpcVRouterAction()
    action.timeout = 300000
    action.name = name
    action.virtualRouterOfferingUuid = virtualrouter_offering_uuid
    action.resourceUuid = resource_uuid
    action.systemTags = system_tags
    action.userTags = use_tags
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory


def remove_all_vpc_vrouter():
    cond = res_ops.gen_query_conditions('applianceVmType', '=', 'vpcvrouter')
    vr_vm_list = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)
    if vr_vm_list:
        for vr_vm in vr_vm_list:
            nic_uuid_list = [nic.uuid for nic in vr_vm.vmNics if nic.metaData == '4']
            for nic_uuid in nic_uuid_list:
                net_ops.detach_l3(nic_uuid)
            vm_ops.destroy_vm(vr_vm.uuid)
