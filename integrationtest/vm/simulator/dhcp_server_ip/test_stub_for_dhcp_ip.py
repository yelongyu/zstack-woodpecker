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
		self.ip_range_option = test_util.IpRangeOption()

	def set_ipversion(self, ip_verison):
		self.ip_version = ip_version

	def get_ipversion(self):
		return self.ip_verison
	
	def set_l2_type(self, l2_type):
		self.l2_type = l2_type

	def get_l2_type(self):
		return self.l2_type
	
	def set_ip_range_option(self,ip_range_option):
		self.ip_range_option = ip_range_option

	def get_L2network_type(self,):
		return res_ops.get_resource(self.get_l2_type)
	
		
		
		
class Public_Ip_For_Dhcp(Dhcp_Ip_Server):
	def __init__(self):
		super(Dhcp_Ip_Server, self).__init__()
	
	def add_ipv4_range(self,):
		
	def create_l3_network(self):
		
		

	

class Private_IP_For_Dhcp(Dhcp_Ip_Server):
	def __init__(self):
		super(Dhcp_Ip_Server, self).__init__()

class VpcNetwork_IP_For_Dhcp(Dhcp_Ip_Server):
	def __init__(self):
		super(Dhcp_Ip_Server, self).__init__()




		
