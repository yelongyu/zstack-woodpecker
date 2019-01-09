'''
prepare  resource for dhcp ip feature

@author Antony WeiJiang

'''
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.deploy_operations as dep_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.autoscaling_operations as aut_ops 
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.test_lib as test_lib
import os

class Dhcp_Ip_Server(object):
	def __init__(self):
		self.l2_type = None
		self.ipVersion = None
		self.l2_query_resource = None
		self.ip_range_option = test_util.IpRangeOption()
		self.ipv6_range_option = test_util.IpV6RangeOption()
		self.ip_by_networkcidroption = test_util.Ip_By_NetworkCidrOption()
		self.ipv6_by_networkcidroption = test_util.IpV6_By_NetworkCidrOption()
		self.l2_uuid = None

	def set_ipVersion(self, ipVersion):
		self.ipVersion = ipVersion

	def get_ipVersion(self):
		return self.ipVersion
	
	def set_l2_type(self, l2_type):
		self.l2_type = l2_type

	def get_l2_type(self):
		return self.l2_type
	
	def set_l2_query_resource(self, l2_query_resource):
		self.l2_query_resource = l2_query_resource

	def get_l2_query_resource(self):
		return self.l2_query_resource
	
	def set_ip_range_option(self, ip_range_option):
		self.ip_range_option = ip_range_option
	
	def get_ip_range_option(self):
		return self.ip_range_option

	def set_ipv6_range_option(self, ipv6_range_option):
		self.ipv6_range_option = ipv6_range_option

	def get_ipv6_range_option(self):
		return self.ipv6_range_option

	def set_ip_by_networkcidroption(self, ip_by_networkcidroption):
		self.ip_by_networkcidroption = ip_by_networkcidroption

	def get_ip_by_networkcidroption(self):
		return self.ip_by_networkcidroption

	def set_ipv6_by_networkcidroption(self, ipv6_by_networkcidroption):
		self.ipv6_by_networkcidroption = ipv6_by_networkcidroption

	def get_ipv6_by_networkcidroption(self):
		return self.ipv6_by_networkcidroption

	def get_l2uuid(self):
		for l2_network in res_ops.get_resource(self.get_l2_query_resource()):
			if l2_network.type == self.get_l2_type():
				self.l2_uuid = l2_network.uuid
		return self.l2_uuid

        def add_ip_range(self, name, start_ip, end_ip, gateway, netmask, systemTags = []):
                self.ip_range_option.set_name(name)
                self.ip_range_option.set_startIp(start_ip)
                self.ip_range_option.set_endIp(end_ip)
                self.ip_range_option.set_gateway(gateway)
                self.ip_range_option.set_netmask(netmask)
                self.ip_range_option.set_ipVersion(self.get_ipVersion())
                self.ip_range_option.set_system_tags(systemTags)
                self.ip_range_option.set_l3_uuid(self.get_l3uuid())
                return net_ops.add_ip_range(self.ip_range_option).uuid

        def add_ipv6_range(self, name ,start_ip, end_ip, gateway, prefixLen, systemTags = [],  addressMode = "Stateful-DHCP",netmask = None):
                self.ipv6_range_option.set_name(name)
                self.ipv6_range_option.set_startIp(start_ip)
                self.ipv6_range_option.set_endIp(end_ip)
                self.ipv6_range_option.set_gateway(gateway)
                self.ipv6_range_option.set_ipVersion(self.get_ipVersion())
                self.ipv6_range_option.set_system_tags(systemTags)
                self.ipv6_range_option.set_addressMode(addressMode)
                self.ipv6_range_option.set_prefixLen(prefixLen)
                self.ipv6_range_option.set_l3_uuid(self.get_l3uuid())
                if netmask:
                        self.ipv6_range_option.set_netmask(netmask)
                return net_ops.add_ipv6_range(self.ipv6_range_option)

        def add_ip_by_networkcidr(self, name, networkcidr, systemTags = []):
                self.ip_by_networkcidroption.set_name(name)
                self.ip_by_networkcidroption.set_ipVersion(self.get_ipVersion())
                self.ip_by_networkcidroption.set_networkCidr(networkcidr)
                self.ip_by_networkcidroption.set_system_tags(systemTags)
                self.ip_by_networkcidroption.set_l3_uuid(self.get_l3uuid())
                return net_ops.add_ip_by_networkcidr(self.ip_by_networkcidroption).uuid

        def add_ipv6_by_networkcidr(self, name, networkcidr, systemTags = [], addressMode = "Stateful-DHCP"):
                self.ipv6_by_networkcidroption.set_name(name)
                self.ipv6_by_networkcidroption.set_ipVersion(self.get_ipVersion())
                self.ipv6_by_networkcidroption.set_networkCidr(networkcidr)
                self.ipv6_by_networkcidroption.set_system_tags(systemTags)
                self.ipv6_by_networkcidroption.set_addressMode(addressMode)
                self.ipv6_by_networkcidroption.set_l3_uuid(self.get_l3uuid())
                return net_ops.add_ipv6_by_networkcidr(self.ipv6_by_networkcidroption)

class Public_Ip_For_Dhcp(Dhcp_Ip_Server):
	def __init__(self):
		super(Public_Ip_For_Dhcp, self).__init__()
		self.l3_uuid = None
		self.category = "Public"
		self.l3_DHCP = "DHCP"
		self.l3_SecurityGroup = "SecurityGroup" 
		self.l3_Userdata = "Userdata"
		self.networkservice_type = ["Flat","SecurityGroup"]

	def create_l3uuid(self,name):
		self.l3_uuid = net_ops.create_l3(name,self.get_l2uuid(),self.get_ipVersion(),self.category).uuid
	
	def get_l3uuid(self):
		return self.l3_uuid
	
	def del_l3uuid(self):
		net_ops.delete_l3(self.get_l3uuid())

	def set_category(self, category):
		self.category = category
	
	def get_category(self):
		return self.category

	def set_l3_DHCP(self, l3_DHCP):
		self.l3_DHCP = l3_DHCP

	def get_l3_DHCP(self):
		return self.l3_DHCP

	def set_l3_SecurityGroup(self, l3_SecurityGroup):
		self.l3_SecurityGroup = l3_SecurityGroup

	def get_l3_SecurityGroup(self):
		return self.l3_SecurityGroup

	def set_l3_Userdata(self, l3_Userdata):
		self.l3_Userdata = l3_Userdata

	def get_l3_Userdata(self):
		return self.l3_Userdata

	def add_service_to_l3network(self):
		for networkservice in self.networkservice_type:
			if networkservice == "Flat":
				allservices = [self.l3_DHCP,self.l3_Userdata]
				cond = res_ops.gen_query_conditions("type", "=", networkservice)
			elif networkservice == "SecurityGroup":
				allservices = [self.l3_SecurityGroup]
				cond = res_ops.gen_query_conditions("type", "=", networkservice)
			network_service_provider_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER,cond)[0].uuid
			test_util.test_logger("%s" %(network_service_provider_uuid))
			aut_ops.AttachNetworkServiceToL3Network(self.get_l3uuid(),allservices,network_service_provider_uuid)

	def check_dhcp_ipaddress(self):
		cond = res_ops.gen_query_conditions("resourceUuid", "=", self.get_l3uuid())
		return res_ops.query_resource(res_ops.SYSTEM_TAG,cond)[0].tag
		

class Private_IP_For_Dhcp(Dhcp_Ip_Server):
	def __init__(self):
		super(Private_IP_For_Dhcp, self).__init__()
		self.l3_uuid = None
		self.category = "Private"
		self.l3_DHCP = "DHCP"
		self.l3_SecurityGroup = "SecurityGroup" 
		self.l3_Userdata = "Userdata"
		self.l3_DNS = "DNS"
		self.l3_SNAT = "SNAT"
		self.l3_LoadBalancer = "LoadBalancer"
		self.l3_PortForwarding = "PortForwarding"
		self.l3_Eip = "Eip"
		self.l3_CentralizedDNS = "CentralizedDNS"
		self.l3_VRouterRoute = "VRouterRoute"
		self.l3_IPsec = "IPsec"
		self.networkservice_type = ["Flat", "SecurityGroup"]
		self.networkservice_type_vr = ["vrouter", "SecurityGroup", "Flat"]

	def create_l3uuid(self,name):
		self.l3_uuid = net_ops.create_l3(name,self.get_l2uuid(),self.get_ipVersion(),self.category).uuid
	
	def get_l3uuid(self):
		return self.l3_uuid
	
	def del_l3uuid(self):
		net_ops.delete_l3(self.get_l3uuid())

	def set_category(self, category):
		self.category = category
	
	def get_category(self):
		return self.category

	def set_l3_DHCP(self, l3_DHCP):
		self.l3_DHCP = l3_DHCP

	def get_l3_DHCP(self):
		return self.l3_DHCP

	def set_l3_SecurityGroup(self, l3_SecurityGroup):
		self.l3_SecurityGroup = l3_SecurityGroup

	def get_l3_SecurityGroup(self):
		return self.l3_SecurityGroup

	def set_l3_Userdata(self, l3_Userdata):
		self.l3_Userdata = l3_Userdata

	def get_l3_Userdata(self):
		return self.l3_Userdata

	def set_l3_DNS(self, l3_DNS):
		self.l3_DNS = l3_DNS

	def get_l3_DNS(self):
		return self.l3_DNS

	def set_l3_SNAT(self, l3_SNAT):
		self.l3_SNAT = l3_SNAT

	def get_l3_SNAT(self):
		self.l3_SNAT = l3_SNAT

	def set_l3_LoadBalancer(self, l3_LoadBalancer):
		self.l3_LoadBalancer = l3_LoadBalancer

	def get_l3_LoadBalancer(self):
		return self.l3_LoadBalancer
	
	def set_l3_PortForwarding(self, l3_PortForwarding):
		self.l3_PortForwarding = l3_PortForwarding

	def get_l3_PortForwarding(self):
		return self.l3_PortForwarding

	def set_l3_Eip(self, l3_Eip):
		self.l3_Eip = l3_Eip

	def get_l3_Eip(self):
		return self.l3_Eip

	def set_l3_CentralizedDNS(self, l3_CentralizedDNS):
		self.l3_CentralizedDNS = l3_CentralizedDNS

	def get_l3_CentralizedDNS(self):
		return self.l3_CentralizedDNS

	def set_l3_VRouterRoute(self, l3_VRouterRoute):
		self.l3_VRouterRoute = l3_VRouterRoute

	def get_l3_VRouterRoute(self):
		return self.l3_VRouterRoute

	def set_l3_IPsec(self, l3_IPsec):
		self.l3_IPsec = l3_IPsec
	
	def get_l3_IPsec(self):
		return self.l3_IPsec

	def add_service_to_l3network(self):
		for networkservice in self.networkservice_type:
			if networkservice == "Flat":
				allservices = [self.l3_DHCP,self.l3_Userdata]
				cond = res_ops.gen_query_conditions("type", "=", networkservice)
			elif networkservice == "SecurityGroup":
				allservices = [self.l3_SecurityGroup]
				cond = res_ops.gen_query_conditions("type", "=", networkservice)
			network_service_provider_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER,cond)[0].uuid
			test_util.test_logger("%s" %(network_service_provider_uuid))
			aut_ops.AttachNetworkServiceToL3Network(self.get_l3uuid(),allservices,network_service_provider_uuid)

	def add_service_to_l3network_vr(self):
		for networkservice in self.networkservice_type_vr:
			if networkservice == "vrouter":
				allservices = [self.l3_DNS , self.l3_SNAT, self.l3_LoadBalancer, self.l3_PortForwarding, self.l3_Eip, self.l3_IPsec, self.l3_VRouterRoute, self.l3_CentralizedDNS]
				cond = res_ops.gen_query_conditions("type", "=", networkservice)
			elif networkservice == "SecurityGroup":
				allservices = [self.l3_SecurityGroup]
				cond = res_ops.gen_query_conditions("type", "=", networkservice)
			elif networkservice == "Flat":
				allservices = [self.l3_Userdata, self.l3_DHCP]
                                cond = res_ops.gen_query_conditions("type", "=", networkservice)
			network_service_provider_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER,cond)[0].uuid
			test_util.test_logger("%s" %(network_service_provider_uuid))
			aut_ops.AttachNetworkServiceToL3Network(self.get_l3uuid(),allservices,network_service_provider_uuid)

	def check_dhcp_ipaddress(self):
		cond = res_ops.gen_query_conditions("resourceUuid", "=", self.get_l3uuid())
		return res_ops.query_resource(res_ops.SYSTEM_TAG,cond)[0].tag
		

class VpcNetwork_IP_For_Dhcp(Dhcp_Ip_Server):
	def __init__(self):
		super(VpcNetwork_IP_For_Dhcp, self).__init__()
		self.l3_uuid = None
                self.category = "Private"
		self.l3_type = "L3VpcNetwork"
                self.l3_DHCP = "DHCP"
                self.l3_SecurityGroup = "SecurityGroup"
                self.l3_Userdata = "Userdata"
		self.l3_IPsec = "IPsec"
		self.l3_VRouterRoute = "VRouterRoute"
		self.l3_CentralizedDNS = "CentralizedDNS"
		self.l3_VipQos = "VipQos"
		self.l3_DNS = "DNS"
		self.l3_SNAT = "SNAT"
		self.l3_LoadBalancer = "LoadBalancer"
		self.l3_PortForwarding = "PortForwarding"
		self.l3_Eip = "Eip"
		self.networkservice_type_vpc = ["vrouter", "SecurityGroup", "Flat"]

	def create_l3uuid(self,name):
		self.l3_uuid = net_ops.create_l3(name,self.get_l2uuid(),self.get_ipVersion(),self.get_category(), self.get_l3_type()).uuid

	def get_l3uuid(self):
		return self.l3_uuid

	def del_l3uuid(self):
		net_ops.delete_l3(self.get_l3uuid())

	def set_category(self, category):
                self.category = category

        def get_category(self):
                return self.category

	def set_l3_type(self, l3_type):
		self.l3_type = l3_type

	def get_l3_type(self):
		return self.l3_type

        def set_l3_DHCP(self, l3_DHCP):
                self.l3_DHCP = l3_DHCP

        def get_l3_DHCP(self):
                return self.l3_DHCP

	def set_l3_SecurityGroup(self, l3_SecurityGroup):
		self.l3_SecurityGroup = l3_SecurityGroup

	def get_l3_SecurityGroup(self):
		return self.l3_SecurityGroup

	def set_l3_Userdata(self, l3_Userdata):
		self.l3_Userdata = l3_Userdata

	def get_l3_Userdata(self):
		return self.l3_Userdata

	def set_l3_IPsec(self, l3_IPsec):
		self.l3_IPsec = l3_IPsec

	def get_l3_IPsec(self):
		return self.l3_IPsec

	def set_l3_VRouterRoute(self, l3_VRouterRoute):
		self.l3_VRouterRoute = l3_VRouterRoute

	def get_l3_VRouterRoute(self):
		return self.l3_VRouterRoute

	def set_l3_CentralizedDNS(self, l3_CentralizedDNS):
		self.l3_CentralizedDNS = l3_CentralizedDNS

	def get_l3_CentralizedDNS(self):
		return self.l3_CentralizedDNS

	def set_l3_VipQos(self, l3_VipQos):
		self.l3_VipQos = l3_VipQos
	
	def get_l3_VipQos(self):
		self.l3_VipQos = l3_VipQos

	def set_l3_DNS(self, l3_DNS):
		self.l3_DNS = l3_DNS

	def get_l3_DNS(self):
		return self.l3_DNS

	def set_l3_SNAT(self, l3_SNAT):
		self.l3_SNAT = l3_SNAT

	def get_l3_SNAT(self):
		return self.l3_SNAT

	def set_l3_LoadBalancer(self, l3_LoadBalancer):
		self.l3_LoadBalancer = l3_LoadBalancer

	def get_l3_LoadBalancer(self):
		return self.l3_LoadBalancer

	def set_l3_PortForwarding(self, l3_PortForwarding):
		self.l3_PortForwarding = l3_PortForwarding

	def get_l3_PortForwarding(self):
		return self.l3_PortForwarding

	def set_l3_Eip(self, l3_Eip):
		self.l3_Eip = l3_Eip

	def get_l3_Eip(self):
		return self.l3_Eip

        def add_service_to_l3_vpcnetwork(self):
                for networkservice in self.networkservice_type_vpc:
                        if networkservice == "Flat":
                                allservices = [self.l3_DHCP,self.l3_Userdata]
                                cond = res_ops.gen_query_conditions("type", "=", networkservice)
                        elif networkservice == "SecurityGroup":
                                allservices = [self.l3_SecurityGroup]
                                cond = res_ops.gen_query_conditions("type", "=", networkservice)
			elif networkservice == "vrouter":
                                allservices = [self.l3_IPsec, self.l3_VRouterRoute, self.l3_CentralizedDNS, self.l3_VipQos, self.l3_DNS, self.l3_SNAT, self.l3_LoadBalancer, self.l3_PortForwarding, self.l3_Eip]
                                cond = res_ops.gen_query_conditions("type", "=", networkservice)
                        network_service_provider_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER,cond)[0].uuid
                        test_util.test_logger("%s" %(network_service_provider_uuid))
                        aut_ops.AttachNetworkServiceToL3Network(self.get_l3uuid(),allservices,network_service_provider_uuid)

        def check_dhcp_ipaddress(self):
                cond = res_ops.gen_query_conditions("resourceUuid", "=", self.get_l3uuid())
                return res_ops.query_resource(res_ops.SYSTEM_TAG,cond)[0].tag

class Create_Vm_Instance():
	def __init__(self):
		pass
	def create_vm(self,l3_uuid,vm_creation_option=None, volume_uuids=None, root_disk_uuid=None, image_uuid=None, strategy_type='InstantStart', session_uuid=None):
		if not vm_creation_option:
			instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(os.environ.get('instanceOfferingName_s')).uuid
			cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
			cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
			image_uuid = res_ops.query_resource(res_ops.IMAGE, cond, session_uuid)[0].uuid
			vm_creation_option = test_util.VmOption()
			vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
			vm_creation_option.set_image_uuid(image_uuid)
			vm_creation_option.set_l3_uuids([l3_uuid])
		if volume_uuids:
			if isinstance(volume_uuids, list):
				vm_creation_option.set_data_disk_uuids(volume_uuids)
			else:
				test_util.test_fail('volume_uuids type: %s is not "list".' % type(volume_uuids))

		if root_disk_uuid:
			vm_creation_option.set_root_disk_uuid(root_disk_uuid)

		if image_uuid:
			vm_creation_option.set_image_uuid(image_uuid)

		if session_uuid:
			vm_creation_option.set_session_uuid(session_uuid)

		vm = test_vm.ZstackTestVm()
		vm.set_creation_option(vm_creation_option)
		vm.create()
		return vm	
