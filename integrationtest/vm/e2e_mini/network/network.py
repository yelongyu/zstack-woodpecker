# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
from test_stub import *


class NETWORK(MINI):
    def __init__(self, uri=None, initialized=False):
        self.network_name = None
        self.network_list = []
        if initialized:
            # if initialized is True, uri should not be None
            self.uri = uri
            return
        super(NETWORK, self).__init__()

    def create_network(self, name=None, dsc=None, vlan=None, physical_interface='zsn0',start_ip='192.168.53.2',
                       end_ip='192.168.53.5', netmask='255.255.255.0', gateway='192.168.53.1', dhcp_server=None, dns=None, view='card'):
        self.network_name = name if name else 'network-' + get_time_postfix()
        self.network_list.append(self.network_name)
        test_util.test_logger('Create Network [%s]' % self.network_name)
        network_dict = {'name': self.network_name,
                        'description': dsc,
                        'vlan': vlan,
                        'physicalInterface': physical_interface,
                        'startIp': start_ip,
                        'endIp': end_ip,
                        'netmask': netmask,
                        'gateway': gateway,
                        'dhcpServer': dhcp_server,
                        'dns': dns}
        if dhcp_server is None:
            network_dict.pop('dhcpServer')
        if dns is None:
            network_dict.pop('dns')
        network_elem = self.create(network_dict, "network", view=view)
        ip_num = abs(int(start_ip.split('.')[-1]) - int(end_ip.split('.')[-1])) + 1
        check_list = [self.network_name, physical_interface, str(ip_num)]
        if vlan:
            check_list.append(vlan)
        else:
            check_list.append('-')
        checker = MINICHECKER(self, network_elem)
        checker.network_check(check_list)

    def delete_network(self, network_name=None, view='card', corner_btn=True, details_page=False):
        network_name = network_name if network_name else self.network_list
        self.delete(network_name, 'network', view=view, corner_btn=corner_btn, details_page=details_page)

    def add_dns_to_l3(self, network=None, dns='8.8.8.8', details_page=True, end_action='confirm'):
        network = network if network else os.getenv('l3PublicNetworkName')
        test_util.test_logger('Add dns [%s] to l3 [%s]' % (dns, network))
        self.navigate('network')
        if details_page:
            self.enter_details_page('network', network)
            self.switch_tab('DNS')
            self.get_elements(MOREOPERATIONBTN)[-1].click()
            self.operate(u'添加DNS')
        else:
            self.more_operate(u'添加DNS', res_name=network)
        if dns in get_inv(network, 'network').dns:
            test_util.test_fail('Fail: There has been the DNS[%s] on L3 network[%s]' % (dns, network))
        self.input('dns', dns)
        self.end_action(end_action)
        if end_action == 'confirm':
            dns_list = []
            dns_list.append(dns)
            if not details_page:
                self.enter_details_page('network', network)
                self.switch_tab('DNS')
            self.check_res_item(dns_list)

    def del_dns_from_l3(self, dns, network=None):
        dns_list = []
        if isinstance(dns, types.ListType):
            dns_list = dns
        else:
            dns_list.append(dns)
        network = network if network else os.getenv('l3PublicNetworkName')
        test_util.test_logger('Delete dns [%s] from l3 [%s]' % (dns, network))
        self.navigate('network')
        self.enter_details_page('network', network)
        self.switch_tab('DNS')
        self.get_table_row(dns_list)
        self.get_elements(MOREOPERATIONBTN)[-1].click()
        self.operate(u'删除DNS')
        self.click_ok()
        self.check_res_item(dns_list, target='notDisplayed')

    def add_network_segment(self, network=None, start_ip=None, end_ip=None, netmask=None, gateway=None, details_page=True, end_action='confirm'):
        network = network if network else os.getenv('l3NoVlanNetworkName1')
        start_ip = start_ip if start_ip else os.getenv('noVlanIpRangeStart1')
        end_ip = end_ip if end_ip else os.getenv('noVlanIpRangeEnd1')
        netmask = netmask if netmask else os.getenv('noVlanIpRangeNetmask1')
        gateway = gateway if gateway else os.getenv('noVlanIpRangeGateway1')
        test_util.test_logger('Add network segment [%s] to [%s]' % (start_ip, end_ip))
        net_segment_dict = {'startIp': start_ip,
                            'endIp': end_ip,
                            'netmask': netmask,
                            'gateway': gateway}
        self.navigate('network')
        if details_page:
            self.enter_details_page('network', network)
            self.switch_tab(u'网络段')
            self.get_elements(MOREOPERATIONBTN)[-1].click()
            self.operate(u'添加网络段')
        else:
            self.more_operate(u'添加网络段', res_name=network)
        for k, v in net_segment_dict.iteritems():
            if v is not None:
                self.input(k, v)
        self.end_action(end_action)
        if end_action == 'confirm':
            check_list = [start_ip, end_ip, netmask, gateway]
            if not details_page:
                self.enter_details_page('network', network)
                self.switch_tab(u'网络段')
            self.check_res_item(check_list)

    def del_network_segment(self, network=None, start_ip=None, end_ip=None):
        network = network if network else os.getenv('l3NoVlanNetworkName1')
        start_ip = start_ip if start_ip else os.getenv('noVlanIpRangeStart1')
        end_ip = end_ip if end_ip else os.getenv('noVlanIpRangeEnd1')
        test_util.test_logger('Delete network segment [%s] to [%s]' % (start_ip, end_ip))
        self.navigate('network')
        self.enter_details_page('network', network)
        self.switch_tab(u'网络段')
        for _row in self.get_elements(TABLEROW):
            if (start_ip in _row.text) and (end_ip in _row.text):
                _row.get_element('input[type="checkbox"]').click()
                break
        else:
            test_util.test_fail('Can not find the network segment from %s to %s' % (start_ip, end_ip))
        self.get_elements(MOREOPERATIONBTN)[-1].click()
        self.operate(u'删除网络段')
        self.click_ok()
        check_list = []
        check_list.append(start_ip)
        check_list.append(end_ip)
        self.check_res_item(check_list, target='notDisplayed')
