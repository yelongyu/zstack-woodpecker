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

MENUDICT = {'homepage': 'a[href="/web/"]',
            'monitor':  'a[href="/web/monitoringCenter"]',
            'vm':       'a[href="/web/vm"]',
            'host':     'a[href="/web/minihost"]',
            'ps':       'a[href="/web/primaryStorage"]',
            'volume':   'a[href="/web/volume"]',
            'image':    'a[href="/web/image"]',
            'network':  'a[href="/web/network"]',
            'alarm':    'a[href="/web/alarmMessage"]'}


def get_inv(name, res_type):
    conditions = res_ops.gen_query_conditions('name', '=', name)
    if res_type == 'vm':
        inv = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)
    elif res_type == 'volume':
        inv = res_ops.query_resource(res_ops.VOLUME, conditions)
    return inv

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

    def _create(self, para_dict, res_type):
        self.navigate(res_type)
        self.get_elements(PRIMARYBTN)[-1].click()
        for k, v in para_dict.iteritems():
            if v is not None:
                self.input(k, v)
        self.click_ok()
        for elem in self.get_elements(CARDCONTAINER):
            if para_dict['name'] in elem.text:
                break
        else:
            test_util.test_fail('Not found the [%s] with name [%s]' % (res_type, para_dict['name']))
        return elem

    def _del(self, res_name, res_type):
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

    def create_vm(self, name=None, dsc=None, image=None, cpu=2, mem='2 GB', data_size='2 GB',
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
                   'dataSize': data_size.split(),
                   'userData': user_data,
                   'l3NetworkUuids': network,
                   'clusterUuid': cluster,
                   'provisioning': provisioning }
        vm_elem = self._create(vm_dict, 'vm')
        vm_inv = get_inv(self.vm_name, "vm")
        check_list = [self.vm_name, str(cpu), mem, vm_inv[0].vmNics[0].ip]
        checker = MINICHECKER(self, vm_elem)
        checker.vm_check(check_list)

    def create_volume(self, name=None, dsc=None, size='2 GB', cluster=None, vm=None, provisioning=u'厚置备'):
        cluster = cluster if cluster else os.getenv('clusterName')
        self.volume_name = name if name else 'volume-' + POSTFIX
        volume_dict = {
                   'name': self.volume_name,
                   'description': dsc,
                   'dataSize': size.split(),
                   'clusterUuid': cluster,
                   'vmUuid' : vm,
                   'provisioning': provisioning }
        volume_elem = self._create(volume_dict, "volume")
        volume_inv = get_inv(self.volume_name, "volume")
        if vm:
            check_list = [self.volume_name, vm, size]
        else:
            check_list = [self.volume_name, size]
        checker = MINICHECKER(self, volume_elem)
        checker.volume_check(check_list, 'detached')

    def delete_vm(self, vm_name=None):
        vm_name = vm_name if vm_name else self.vm_name
        self._del(vm_name, 'vm')

    
    def delete_volume(self, volume_name=None):
        volume_name = volume_name if volume_name else self.volume_name
        self._del(volume_name, 'volume')

    def save_element_location(self, filename="location.tmpt"):
        for menu, page in MENUDICT.items():
            loc = {}
            loc[menu] = self.get_element(page).location
            json_loc = jsonobject.dumps(loc)
            try:
                with open(join(LOCATION_FILE_PATH, filename), 'ab') as f:
                    f.write(json_loc)
            except IOError:
                return False
        return True

    def enabled_status_checker(self):
        self.navigate('vm')
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

    def vm_check(self, check_list=[], ops='new_created'):
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

    def volume_check(self, check_list=[], ops='attached'):
        if ops == 'attached':
            for v in check_list:
                assert v in self.elem.text
        elif ops == 'detached':
            check_list.append(u'未加载')
            for v in check_list:
                assert v in self.elem.text
