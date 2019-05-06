# -*- coding:utf-8 -*-
'''

Create an unified test_stub for E2E test operations

@author: Legion
'''

import os
import time
import types
from os.path import join
from zstackwoodpecker.e2e_lib import E2E
import zstackwoodpecker.operations.resource_operations as res_ops 
from zstackwoodpecker import test_util
import zstacklib.utils.jsonobject as jsonobject

LOCATION_FILE_PATH = '/root/.zstackwoodpecker/integrationtest/vm/e2e_mini/'
POSTFIX = time.strftime('%y%m%d-%H%M%S', time.localtime())
MESSAGETOAST = 'ant-notification-notice-message'
CARDCONTAINER = 'ant-card|ant-table-row'
PRIMARYBTN = 'ant-btn-primary'
MOREOPERATIONBTN = 'ant-dropdown-trigger'
TABLEROW = 'ant-table-row ant-table-row-level-0'

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
    elif res_type == 'minihost':
        inv = res_ops.query_resource(res_ops.CLUSTER, conditions)
    elif res_type == 'image':
        inv = res_ops.query_resource(res_ops.IMAGE, conditions)
    elif res_type == 'network':
        inv = res_ops.query_resource(res_ops.L3_NETWORK, conditions)
    elif res_type == 'primaryStorage':
        inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE, conditions)
    if inv:
        return inv[0]
    else:
        test_util.test_fail('Not found the [%s] with name [%s]' % (res_type, name))

class MINI(E2E):
    def __init__(self):
        super(MINI, self).__init__()
        self.vm_name = None
        self.volume_name = None
        if os.getenv('ZSTACK_SIMULATOR'):
            self.mini_server_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
        else:
            self.mini_server_ip = os.getenv('zstackHaVip')
        self.url('http://%s:8200' % self.mini_server_ip)
        self.window_size(1600, 900)
        self.login()

    def login(self):
        self.get_element('#accountName').input('admin')
        self.get_element('#password').input('password')
        # Login button
        self.get_element('button', 'tag name').click()
        self.wait_for_element(MESSAGETOAST)
        assert self.get_elements(MESSAGETOAST)
        # root page
        assert self.get_elements('content___3mo4D ant-layout-content')

    def login_with_cleartext_password(self):
        self.get_element('#accountName').input('admin')
        passwordInput = self.get_element('#password')
        assert passwordInput.get_attribute('type') == 'password'
        self.get_element('ant-input-suffix').click()
        passwordInput.input('password')
        assert passwordInput.get_attribute('type') == 'text'
        # Login button
        self.get_element('button', 'tag name').click()
        self.wait_for_element(MESSAGETOAST)
        assert self.get_elements(MESSAGETOAST)
        # root page
        assert self.get_elements('content___3mo4D ant-layout-content')

    def navigate(self, menu):
        self.get_element(MENUDICT[menu]).click()
        self.wait_for_element(PRIMARYBTN)
        time.sleep(1)

    def click_ok(self):
        self.get_elements(PRIMARYBTN)[-1].click()
        self.wait_for_element(MESSAGETOAST, timeout=120, target='disappear')

    def more_operate(self, op_name, res_type, res_name, details_page=False):
        res_list = []
        if isinstance(res_name, types.ListType):
            res_list = res_name
        else:
            res_list.append(res_name)
        if details_page:
            if len(res_list) == 1:
                self.enter_details_page(res_type, res_list[0])
            else:
                test_util.test_fail('Multiple resource can not enter details page together')
        else:
            for res in res_list:
                for _elem in self.get_elements(CARDCONTAINER):
                    if res in _elem.text:
                        if op_name == u"加载":
                            if u"未加载" in _elem.text:
                                break
                            else:
                                test_util.test_fail('The volume named [%s] is not attached' % res)
                        elif op_name == u"卸载":
                            if u"未加载" not in _elem.text:
                                break
                            else:
                                test_util.test_fail('The volume named [%s] is attached' % res)
                        break
                    else:
                        test_util.test_fail('Not found the element with name [%s]' % res)
                _elem.get_element('input[type="checkbox"]').click()
        self.get_element(MOREOPERATIONBTN).click()
        time.sleep(1)
        self.operate(op_name)
        time.sleep(1)

    def enter_details_page(self, res_type, name):
        inv = get_inv(name, res_type)
        lnk = 'a[href="/web/%s/%s"]' % (res_type, inv.uuid)
        self.get_element(lnk).click()

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

    def _del(self, res_name, res_type, corner_btn=False):
        self.navigate(res_type)
        for _elem in self.get_elements(CARDCONTAINER):
            if res_name in _elem.text:
                break
        else:
            test_util.test_fail('Not found the [%s] with name [%s]' % (res_type, res_name))
        if corner_btn:
            _elem.get_elements('button', 'tag name')[-1].click()
        else:
            self.more_operate(op_name=u'删除', res_type=res_type, res_name=res_name)
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
                   'dataSize': data_size.split() if data_size else None,
                   'userData': user_data,
                   'l3NetworkUuids': network,
                   'clusterUuid': cluster,
                   'provisioning': provisioning }
        vm_elem = self._create(vm_dict, 'vm')
        vm_inv = get_inv(self.vm_name, "vm")
        check_list = [self.vm_name, str(cpu), mem, vm_inv.vmNics[0].ip]
        checker = MINICHECKER(self, vm_elem)
        checker.vm_check(vm_inv, check_list, ops='new_created')

    def add_dns_to_l3(self, network=None, dns='8.8.8.8'):
        #network = network if network else os.getenv('l3PublicNetworkName')
        self.navigate('network')
        time.sleep(3)
        if self.get_elements(CARDCONTAINER):
            if network:
                for _elem in self.get_elements(CARDCONTAINER):
                    if network in _elem.text:
                        if dns not in _elem.text:
                            _elem.get_element('input[type="checkbox"]').click()
                            break
                        else:
                            test_util.test_fail('Network %s already have dns %s' % (network, dns))
                    else:
                        test_util.test_fail("Not found network %s" % network)
            else:
                for _elem in self.get_elements(CARDCONTAINER):
                    if dns not in _elem.text:
                        _elem.get_element('input[type="checkbox"]').click()
                        break
                    else:
                        test_util.test_fail('Network %s already have dns %s' % (network, dns))
        else:
            test_util.test_fail("No l3 network")
        time.sleep(1)
        self.more_operate(u'添加DNS')
        time.sleep(1)
        self.input('DNS',dns)
        time.sleep(1)
        self.confirm()

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

    def delete_vm(self, vm_name=None, corner_btn=False):
        vm_name = vm_name if vm_name else self.vm_name
        self._del(vm_name, 'vm', corner_btn=corner_btn)

    def delete_volume(self, volume_name=None, corner_btn=False):
        volume_name = volume_name if volume_name else self.volume_name
        self._del(volume_name, 'volume', corner_btn=corner_btn)

    def attach_volume(self, volume_name=[], dest_vm=None, details_page=False):
        emptyl = []
        volume_list = volume_name if volume_name != [] else self.volume_name
        if not isinstance(volume_list, types.ListType):
            emptyl.append(volume_list)
            volume_list = emptyl
        dest_vm = dest_vm if dest_vm else self.vm_name
        self.navigate('volume')
        self.more_operate(u'加载', res_type='volume', res_name=volume_list, details_page=details_page)
        for _row in self.get_elements(TABLEROW):
            if dest_vm in _row.text:
                break
        else:
            test_util.test_fail('Not found the dest-vm with name [%s]' % dest_vm)
        _row.get_element('input[type="radio"]').click()
        self.click_ok()
        check_list = [dest_vm]
        for vol in volume_list:
            for _elem in self.get_elements(CARDCONTAINER):
                if vol in _elem.text:
                    break
                MINICHECKER(self, _elem).volume_check(check_list, ops='attached')

    def detach_volume(self, volume_name=[], details_page=False):
        emptyl = []
        volume_list = volume_name if volume_name != [] else self.volume_name
        if not isinstance(volume_list, types.ListType):
            emptyl.append(volume_list)
            volume_list = emptyl
        self.navigate('volume')
        self.more_operate(u'卸载', res_type='volume', res_name=volume_list, details_page=details_page)        
        self.click_ok()
        for vol in volume_list:
            for _elem in self.get_elements(CARDCONTAINER):
                if vol in _elem.text:
                    break
                MINICHECKER(self, _elem).volume_check(ops='detached')

    def modify_info(self, res_type, res_name, new_name, new_dsc=None, corner_btn=False):
        check_list = []
        self.navigate(res_type)
        for _elem in self.get_elements(CARDCONTAINER):
            if res_name in _elem.text:
                break
        else:
            test_util.test_fail('Not found the [%s] with name [%s]' % (res_type, res_name))
        if corner_btn:
            _elem.get_elements('button', 'tag name')[-2].click()
        else:
            self.more_operate(u'修改信息', res_type=res_type, res_name=res_name)
        if new_name is not None:
            self.input('name', new_name)
            check_list.append(new_name)
        if new_dsc is not None:
            self.input('description', new_dsc)
        self.click_ok()
        for _elem in self.get_elements(CARDCONTAINER):
            if new_name in _elem.text:
                break
        checker = MINICHECKER(self, _elem)
        if res_type == 'volume':
            checker.volume_check()
        elif res_type == 'vm':
            checker.vm_check()
        else:
            pass

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

    def vm_check(self, inv, check_list=[], ops=None):
        if not ops:
            for v in check_list:
                assert v in self.elem.text
        elif ops == 'new_created':
            check_list.append(u'运行中')
            for v in check_list:
                assert v in self.elem.text
            # vm_lnk = 'a[href="/web/vm/%s"]' % inv.uuid
            # self.obj.get_element(vm_lnk).click()
        elif ops == 'start':
            check_list.append(u'运行中')
            pass
        elif ops == 'stop':
            pass
        elif ops == 'delete':
            pass

    def volume_check(self, check_list=[], ops=None):
        if not ops:
            for v in check_list:
                assert v in self.elem.text
        elif ops == 'attached':
            for v in check_list:
                assert v in self.elem.text
        elif ops == 'detached':
            check_list.append(u'未加载')
            for v in check_list:
                assert v in self.elem.text
