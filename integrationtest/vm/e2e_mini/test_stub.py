# -*- coding:utf-8 -*-
'''

Create an unified test_stub for E2E test operations

@author: Legion
'''

import os
import time
from os.path import join
from zstackwoodpecker.e2e_lib import E2E
import zstackwoodpecker.operations.resource_operations as res_ops 
from zstackwoodpecker import test_util
import zstacklib.utils.jsonobject as jsonobject

LOCATION_FILE_PATH = '/root/.zstackwoodpecker/integrationtest/vm/e2e_mini/'
POSTFIX = time.strftime('%y%m%d-%H%M%S', time.localtime())
MESSAGETOAST = 'ant-notification-notice-message'
REFRESHCSS = 'ant-btn square___3vP_2 ant-btn-primary'
CARDCONTAINER = 'ant-list-item cardContainer___1TO4m'
PRIMARYBTN = 'ant-btn ant-btn-primary'
MOREOPERATIONBTN = 'ant-btn ant-dropdown-trigger'

MENUDICT = {'vm':       'a[href="/web/vm"]',
            'host':     'a[href="/web/minihost"]',
            'ps':       'a[href="/web/primaryStorage"]',
            'volume':   'a[href="/web/volume"]',
            'image':    'a[href="/web/image"]',
            'network':  'a[href="/web/network"]'}


def get_vm_inv(vm_name):
    conditions = res_ops.gen_query_conditions('name', '=', vm_name)
    vm_inv = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)
    return vm_inv

class MINI(E2E):
    def __init__(self):
        super(MINI, self).__init__()
        self.vm_name = None
        self.volume_name = None
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
        assert self.get_elements(MESSAGETOAST)
        # root page
        assert self.get_elements('content___3mo4D ant-layout-content')

    def navigate(self, menu):
        self.get_element(MENUDICT[menu]).click()
        self.wait_for_element(REFRESHCSS)
        time.sleep(1)

    def click_ok(self):
        self.get_elements(PRIMARYBTN)[-1].click()
        self.wait_for_element(MESSAGETOAST, timeout=60, target='disappear')

    def more_operate(self, op_name):
        self.get_element(MOREOPERATIONBTN).click()
        time.sleep(1)
        self.operate(op_name)
        time.sleep(1)

    def _create(self, para_dict, res_type='vm'):
        self.navigate(res_type)
        self.get_elements(PRIMARYBTN)[-1].click()
        for k, v in para_dict.iteritems():
            if v is not None:
                self.input(k, v)
        self.click_ok()
        for vm_elem in self.get_elements(CARDCONTAINER):
            if para_dict['name'] in vm_elem.text:
                break
        else:
            test_util.test_fail('Not found the [%s] with name [%s]' % (res_type, para_dict['name']))
        return vm_elem

    def _del(self, res_name, res_type='vm'):
        self.navigate(res_type)
        for _elem in self.get_elements(CARDCONTAINER):
            if res_name in _elem.text:
                break
        else:
            test_util.test_fail('Not found the [%s] with name [%s]' % (res_type, res_name))
        _elem.get_element('input[type="checkbox"]').click()
        self.more_operate(u'删除')
        self.click_ok()
        for _elem in self.get_elements(CARDCONTAINER):
            if _elem.text == res_name:
                test_util.test_fail('[%s] is still displayed!' % res_name)

    def create_vm(self, name=None, dsc=None, image=None, cpu=2, mem='2 GB', data_size=None,
                  user_data=None, network=None, cluster=None, provisioning=u'厚置备'):
        image = image if image else os.getenv('imageName_s')
        network = network if network else os.getenv('l3PublicNetworkName')
        cluster = cluster if cluster else os.getenv('clusterName')
        self.vm_name = name if name else 'vm-' + POSTFIX
        vm_dict = {'name': self.vm_name,
                   'description': dsc,
                   'imageUuid': image,
                   'cpuNum': cpu,
                   'memorySize': mem.split(),
                   'dataSize': data_size,
                   'userData': user_data,
                   'l3NetworkUuids': network,
                   'clusterUuid': cluster,
                   'provisioning': provisioning }
        vm_elem = self._create(vm_dict, 'vm')
        vm_inv = get_vm_inv(self.vm_name)
        check_list = [self.vm_name, cpu, mem, vm_inv.vmNics[0].ip]
        checker = MINICHECKER(self, vm_elem)
        checker.vm_check(check_list)

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
        vm_name = vm_name if vm_name else self.vm_name
        self._del(vm_name, 'vm')

    
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

    def save_element_location(self, filename="location.tmpt"):
        page_list = ["", "monitoringCenter", "minihost", "primaryStorage", "vm", "volume", "image", "network", "alarmMessage"]
        for page in page_list:
            loc = {}
            loc[page] = self.get_element('a[href="/web/%s"]' % page).location
            json_loc = jsonobject.dumps(loc)
            try:
                with open(join(LOCATION_FILE_PATH, filename), 'ab') as f:
                    f.write(json_loc)
            except IOError:
                return False
        return True

    def enabled_status_checker(self):
        self.get_element('a[href="/web/vm"]').click()
        self.wait_for_element(CARDCONTAINER)

        btn_elems = self.get_elements('button', 'tag name')
        start_btn = [btn_elem for btn_elem in btn_elems if btn_elem.text == u'启动'][0]
        stop_btn = [btn_elem for btn_elem in btn_elems if btn_elem.text == u'停止'][0]
        assert start_btn.enabled == False
        assert start_btn.enabled == False

        vm_elems = self.get_elements(CARDCONTAINER)
        vm_checkboxs = self.get_elements('input[type="checkbox"]')

        # the checkboxs clicked will detach to the page document
        def update_checkboxs():
            return self.get_elements('input[type="checkbox"]')
        
        assert len(vm_elems) == len(vm_checkboxs)
        vm_checkboxs[0].click()
        vm_checkboxs = update_checkboxs()
        assert vm_checkboxs[0].selected == True
        first_vm_status = vm_elems[0].get_elements('labelContainer___10VVH')[0].text
        if first_vm_status == u"运行中":
            assert start_btn.enabled == False
            assert stop_btn.enbled == True
        elif first_vm_status == u"已停止":
            assert start_btn.enabled == True
            assert stop_btn.enabled == False
        
        if len(vm_elems) > 1:
            vm_checkboxs = update_checkboxs()
            vm_checkboxs[1].click()
            vm_checkboxs = update_checkboxs()
            assert vm_checkboxs[0].selected == True
            assert vm_checkboxs[1].selected == True
            second_vm_status = vm_elems[1].get_elements('labelContainer___10VVH')[0].text    
            if first_vm_status != second_vm_status:
                assert start_btn.enabled == False
                assert stop_btn.enabled == False
        return True



class MINICHECKER(object):
    def __init__(self, obj, elem):
        self.obj = obj
        self.elem = elem

    def vm_check(self, check_list=[], ops='create'):
        if ops == 'new_created':
            check_list.append(u'运行中')
            for v in check_list:
                assert v in self.elem.text
        elif ops == 'start':
            check_list.append(u'运行中')
            pass
        elif ops == 'stop':
            pass
        elif ops == 'delete':
            pass

    def volume_check(self):
        pass