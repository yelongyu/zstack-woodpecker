# -*- coding:utf-8 -*-
'''

Create an unified test_stub for E2E test operations

@author: Legion
'''

import os
import time
from zstackwoodpecker.e2e_lib import E2E
import zstackwoodpecker.operations.resource_operations as res_ops 
from zstackwoodpecker import test_util

POSTFIX = time.strftime('%y%m%d-%H%M%S', time.localtime())
MESSAGETOAST = 'ant-notification-notice-message'
CARDCONTAINER = 'ant-list-item cardContainer___1TO4m'

class MINI(E2E):
    def __init__(self):
        super(MINI, self).__init__()
        self.vm_name = None
        if os.getenv('ZSTACK_SIMULATOR'):
            self.mini_server_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
        else:
            self.mini_server_ip = os.getenv('zstackHaVip')
        self.route('http://%s:8200' % self.mini_server_ip)
        self.window_size(1600, 900)
        self.login()

    def login(self):
        self.get_element('#accountName').input('admin')
        self.get_element('#password').input('password')
        self.click_button(u'登 录')
        self.wait_for_element(MESSAGETOAST)
        assert self.get_element(MESSAGETOAST).text == u'登录成功', \
        'The notification of successful login was not displayed!'
        elem = self.get_element('active')
        if elem.text != u'首页':
            test_util.test_logger(elem.err_msg)
            test_util.test_fail('Login failed! %s')

    def create_vm(self, name=None, dsc=None, image=os.getenv('imageName_s'), cpu=2, mem='2 GB', data_size=None,user_data=None,
                  network=os.getenv('l3PublicNetworkName'), cluster=os.getenv('clusterName'), provisioning=u'厚置备'):
        self.get_element('a[href="/web/vm"]').click()
        self.wait_for_element(CARDCONTAINER)
        self.click_button(u'创建云主机')
        self.vm_name = name if name else 'vm-' + POSTFIX
        vm_dict = {u'名称': self.vm_name,
                   u'简介': dsc,
                   u'镜像': image,
                   u'CPU': cpu,
                   u'内存': mem,
                   u'数据盘容量': data_size,
                   u'Userdata': user_data,
                   u'网络': network,
                   u'一体机': cluster,
                   u'置备类型': provisioning}
        for k, v in vm_dict.iteritems():
            if v:
                if k == u'内存':
                    val = v.split()
                    val.reverse()
                    self.input(k, val)
                else:
                    self.input(k, v)
        self.confirm()
        self.wait_for_element(MESSAGETOAST, timeout=60, target='disappear')
        for vm_elem in self.get_elements(CARDCONTAINER):
            if self.vm_name in vm_elem.text:
                break
        else:
            test_util.test_fail('Not found the vm [name: %s]' % self.vm_name)
        attr_elems = vm_elem.get_elements('labelContainer___10VVH')
        vm_offering = u'%s核 %s' % (cpu, mem)
        assert attr_elems[0].text == u'运行中', "Excepted: u'运行中', actual: %s" % attr_elems[0].text
        assert attr_elems[1].text == vm_offering, "Excepted: %s, actual: %s" % (vm_offering, attr_elems[1].text)
        assert attr_elems[2].text == 'Linux', "Excepted: 'Linux', actual: %s" % attr_elems[2].text
        assert len(attr_elems[3].text.split('.')) == 4, "Actual vm ip is [%s]" % attr_elems[3].text

    def delete_vm(self, vm_name=None):
        self.get_element('a[href="/web/vm"]').click()
        self.wait_for_element(CARDCONTAINER)
        vm_name = vm_name if vm_name else self.vm_name
        for vm_elem in self.get_elements(CARDCONTAINER):
            if vm_name in vm_elem.text:
                break
        else:
            test_util.test_fail('Not found the vm [name: %s]' % vm_name)
        vm_elem.get_element('input[type="checkbox"]').click()
        self.click_button(u'更多操作')
        self.operate(u'删除')
        for vm_elem in self.get_elements(CARDCONTAINER):
            if vm_elem.text == vm_name:
                test_util.test_fail('VM [%s] is still displayed!' % vm_name)

