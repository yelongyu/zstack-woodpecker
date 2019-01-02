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
		self.ip_version = None
		self.l2_type = None
		self.l2_query_resource = None
		self.ip_range_option = test_util.IpRangeOption()
		self.ipv6_range_option = test_util.IpV6RangeOption()
		self.ip_by_networkcidroption = test_util.Ip_By_NetworkCidrOption()
		self.ipv6_by_networkcidroption = test_util.IpV6_By_NetworkCidrOption()
		self.l2_uuid = None

	def set_ipversion(self, ip_verison):
		self.ip_version = ip_version

	def get_ipversion(self):
		return self.ip_verison
	
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

class Public_Ip_For_Dhcp(Dhcp_Ip_Server):
	def __init__(self):
		super(Public_Ip_For_Dhcp, self).__init__()
		self.ipVersion = None
		self.l3_uuid = None
		self.category = "Public"
		self.l3_DHCP = "DHCP"
		self.l3_SecurityGroup = "SecurityGroup" 
		self.l3_Userdata = "Userdata"
		self.networkservice_type = ["Flat","SecurityGroup"]

	def set_ipVersion(self, ipVersion):
		self.ipVersion = ipVersion

	def get_ipVersion(self):
		return self.ipVersion

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
		
	def add_ip_range(self, name, start_ip, end_ip, gateway, netmask, ipversion = 4, systemTags = []):
		self.ip_range_option.set_name(name)
		self.ip_range_option.set_startIp(start_ip)
		self.ip_range_option.set_endIp(end_ip)
		self.ip_range_option.set_gateway(gateway)
		self.ip_range_option.set_netmask(netmask)
		self.ip_range_option.set_ipVersion(ipversion)
		self.ip_range_option.set_system_tags(systemTags)
		self.ip_range_option.set_l3_uuid(self.get_l3uuid())	
		return net_ops.add_ip_range(self.ip_range_option).uuid

	def add_ipv6_range(self):
		net_ops.add_ipv6_range(self.ipv6_range_option)		

	def add_ip_by_networkcidr(self):
		net_ops.add_ip_by_networkcidr(self.ip_by_networkcidroption)

	def add_ipv6_by_networkcidr(self):
		net_ops.add_ipv6_by_networkcidr(self.ipv6_by_networkcidroption)

		
class Private_IP_For_Dhcp(Dhcp_Ip_Server):
	def __init__(self):
		super(Private_IP_For_Dhcp, self).__init__()

class VpcNetwork_IP_For_Dhcp(Dhcp_Ip_Server):
	def __init__(self):
		super(VpcNetwork_IP_For_Dhcp, self).__init__()

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
