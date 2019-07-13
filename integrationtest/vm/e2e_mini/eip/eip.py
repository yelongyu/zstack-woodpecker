# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
from test_stub import *


class EIP(MINI):
    def __init__(self, uri=None, initialized=False):
        self.eip_name = None
        self.eip_list = []
        if initialized:
            # if initialized is True, uri should not be None
            self.uri = uri
            return
        super(EIP, self).__init__()

    def create_eip(self, name=None, dsc=None, network=None, required_ip=None, view='card'):
        self.eip_name = name if name else 'EIP-' + get_time_postfix()
        self.eip_list.append(self.eip_name)
        network = network if network else os.getenv('l3PublicNetworkName')
        test_util.test_logger('Create EIP[%s]' % self.eip_name)
        priority_dict = {'l3NetworkUuid': network}
        eip_dict = {'name': self.eip_name,
                    'description': dsc,
                    'requiredIp': required_ip}
        eip_elem = self.create(eip_dict, "eip", view=view, priority_dict=priority_dict)
        check_list = [self.eip_name]
        if required_ip is not None:
            check_list.append(required_ip)
        checker = MINICHECKER(self, eip_elem)
        checker.eip_check(check_list)

    def delete_eip(self, eip_name=None, view='card', corner_btn=True, details_page=False):
        eip_name = eip_name if eip_name else self.eip_list
        self.delete(eip_name, 'eip', view=view, corner_btn=corner_btn, details_page=details_page)

    def eip_binding(self, eip_name, vm_name):
        test_util.test_logger("Bind %s to %s" % (eip_name, vm_name))
        vm_inv = get_inv(vm_name, "vm")
        vm_nic_ip = vm_inv.vmNics[0].ip
        self.navigate('eip')
        self.more_operate(u'绑定', eip_name)
        self.input('resourceUuid', vm_name)
        self.input('vmNicUuid', vm_nic_ip)
        self.click_ok()
        eip_elem = self.get_res_element(eip_name)
        checker = MINICHECKER(self, eip_elem)
        checker.eip_check([vm_nic_ip])

    def eip_unbinding(self, eip_name):
        test_util.test_logger("Unbind %s" % eip_name)
        self.navigate('eip')
        self.more_operate(u'解绑', eip_name)
        self.click_ok()
        eip_elem = self.get_res_element(eip_name)
        assert self.get_detail_info(eip_name, 'eip', u'私网IP:') == '-'
