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
REFRESHCSS = 'ant-btn square___3vP_2 ant-btn-primary'
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
        # Login button
        self.get_element('ant-btn ant-btn-primary ant-btn-block').click()
        self.wait_for_element(MESSAGETOAST)
        # root page
        assert self.get_elements('content___3mo4D ant-layout-content')

    def create_vm(self, name=None, dsc=None, image=os.getenv('imageName_s'), cpu=2, mem='2 GB', data_size='2 GB', user_data=None,
                  network=os.getenv('l3PublicNetworkName'), cluster=os.getenv('clusterName'), provisioning=u'厚置备'):
        self.get_element('a[href="/web/vm"]').click()
        self.wait_for_element(REFRESHCSS)
        time.sleep(3)
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
                   u'置备类型': provisioning
                   }
        for k, v in vm_dict.iteritems():
            if v:
                if k == u'内存' or k == u'数据盘容量':
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

    def create_volume(self, name=None, dsc=None, size='2 GB', cluster=os.getenv('clusterName'), vm=None, provisioning=u'厚置备'):
        self.get_element('a[href="/web/volume"]').click()
        self.wait_for_element(REFRESHCSS)
        time.sleep(5)
        self.click_button(u'创建数据盘')
        self.volume_name = name if name else 'volume-' + POSTFIX
        volume_dict = {
            u'名称': self.volume_name,
            u'简介': dsc,
            u'容量': size,
            u'一体机': cluster,
            u'云主机' : vm,
            u'置备类型': provisioning
        }
        for k, v in volume_dict.iteritems():
            if v:
                if k == u'容量':
                    val = v.split()
                    val.reverse()
                    self.input(k, val)
                else:
                    self.input(k, v)
        self.confirm()
        self.wait_for_element(MESSAGETOAST, timeout=60, target='disappear')
        for volume_elem in self.get_elements(CARDCONTAINER):
            if self.volume_name in volume_elem.text:
                break
        else:
            test_util.test_fail('Not found the volume [name: %s]' % self.volume_name)
        attr_elems = volume_elem.get_elements('labelContainer___10VVH')
        assert attr_elems[0].text == u'就绪', "Excepted: u'就绪', actual: %s" % attr_elems[0].text
        if vm:
            assert attr_elems[1].text == vm, "Excepted: %s, actual: %s" % (vm, attr_elems[1].text)
        else:
            assert attr_elems[1].text == u'未加载', "Excepted: u'未加载', actual: %s" % attr_elems[1].text
        assert attr_elems[2].text == size, "Excepted: %s, actual: %s" % (size, attr_elems[2].text)

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
        self.confirm()
        self.wait_for_element(MESSAGETOAST, timeout=60, target='disappear')
        for vm_elem in self.get_elements(CARDCONTAINER):
            if vm_elem.text == vm_name:
                test_util.test_fail('VM [%s] is still displayed!' % vm_name)

    def delete_volume(self, volume_name=None):
        self.get_element('a[href="/web/volume"]').click()
        self.wait_for_element(CARDCONTAINER)
        volume_name = volume_name if volume_name else self.volume_name
        for volume_elem in self.get_elements(CARDCONTAINER):
            if volume_name in volume_elem.text:
                break
        else:
            test_util.test_fail('Not found the volume [name: %s]' % volume_name)
        volume_elem.get_element('input[type="checkbox"]').click()
        self.click_button(u"更多操作")
        self.operate(u'删除')
        self.confirm()
        self.wait_for_element(MESSAGETOAST, timeout=60, target='disappear')
        for volume_elem in self.get_elements(CARDCONTAINER):
            if volume_elem in self.get_elements(CARDCONTAINER):
                if volume_elem.text == volume_name:
                    test_util.test_fail('Volume [%s] is still displayed!' % volume_name)

