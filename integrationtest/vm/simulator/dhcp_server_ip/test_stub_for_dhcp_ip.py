'''
prepare  resource for dhcp ip feature

@author Antony WeiJiang

'''
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.deploy_operations as dep_ops
import zstackwoodpecker.test_util as test_util

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
		
	def set_ipVersion(self, ipVersion):
		self.ipVersion = ipVersion

	def get_ipVersion(self):
		return self.ipVersion

	def create_l3uuid(self,name):
		self.l3_uuid = net_ops.create_l3(name,self.get_l2uuid(),self.get_ipVersion(),self.category).uuid
	
	def get_l3uuid(self):
		return self.l3_uuid

	def add_ip_range(self, name, start_ip, end_ip, gateway, netmask, ipversion = 4, systemTags = []):
		self.ip_range_option.set_name(name)
		self.ip_range_option.set_startIp(start_ip)
		self.ip_range_option.set_endIp(end_ip)
		self.ip_range_option.set_gateway(gateway)
		self.ip_range_option.set_netmask(netmask)
		self.ip_range_option.set_ipVersion(ipversion)
		self.ip_range_option.set_system_tags(systemTags)
		self.ip_range_option.set_l3_uuid(self.get_l3uuid())	
		uuid = net_ops.add_ip_range(self.ip_range_option).uuid

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




		
