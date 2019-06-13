# -*- coding:utf-8 -*-
'''

Create an unified test_stub for E2E test operations

@author: Legion
'''

import os
import time
import types
import random
import xml.dom.minidom as minidom
from os.path import join
from zstackwoodpecker.e2e_lib import E2E
import zstackwoodpecker.operations.resource_operations as res_ops
from zstackwoodpecker import test_util
import zstacklib.utils.jsonobject as jsonobject

LOG_FILE_PATH = '/root/.zstackwoodpecker/integrationtest/vm/e2e_mini/'
MESSAGETOAST = 'ant-notification-notice-message'
CARDCONTAINER = 'ant-card|ant-table-row'
MODALCONTENT = 'ant-modal-content'
PRIMARYBTN = 'ant-btn-primary'
BTN = 'ant-btn'
EXITBTN = 'ant-modal-close-x'
MOREOPERATIONBTN = 'ant-dropdown-trigger'
TABLEROW = 'ant-table-row ant-table-row-level-0'
CHECKBOX = 'input[type="checkbox"]'
FORMEXPLAIN = 'ant-form-explain'
SPINCONTAINER = 'ant-spin-container'
CONFIRMITEM = 'confirmItem___1ZEQE'
MENUSETTING = 'ant-menu-horizontal'
OPS_ONGOING = '#operationhint_ongoing'
OPS_SUCCESS = '#operationhint_success'
OPS_FAIL = '#operationhint_fail'
PRIMARYBTNNUM = 2


MENUDICT = {'homepage': 'a[href="/web/"]',
            'monitor': 'a[href="/web/monitoringCenter"]',
            'vm': 'a[href="/web/vm"]',
            'minihost': 'a[href="/web/minihost"]',
            'ps': 'a[href="/web/primaryStorage"]',
            'volume': 'a[href="/web/volume"]',
            'image': 'a[href="/web/image"]',
            'network': 'a[href="/web/network"]',
            'alarm': 'a[href="/web/alarmMessage"]',
            'eip': 'a[href="/web/eip"]',
            'log': 'a[href="/web/operationLog"]'}

VIEWDICT = {'list': '#btn_listswitch_s',
            'card': '#btn_cardswitch_s'}


def get_mn_ip():
    dom_path = '/'.join(os.getcwd().split('/')[:3]) + "/scenario-file.xml"
    dom = minidom.parse(dom_path)
    root = dom.documentElement
    item_list = root.getElementsByTagName('vm')
    first_mn_ip = item_list[0].getAttribute('managementIp')
    second_mn_ip = item_list[1].getAttribute('managementIp')
    return str(first_mn_ip), str(second_mn_ip)

def get_time_postfix():
    rand_postfix = str(random.random()).split('.')[-1]
    return time.strftime('%y%m%d-%H%M%S', time.localtime()) + '-' + rand_postfix

def get_inv(name, res_type):
    res_dict = {'vm': res_ops.VM_INSTANCE,
                'volume': res_ops.VOLUME,
                'minihost': res_ops.CLUSTER,
                'network': res_ops.L3_NETWORK,
                'image': res_ops.IMAGE,
                'primaryStorage': res_ops.PRIMARY_STORAGE,
                'eip': res_ops.EIP}
    conditions = res_ops.gen_query_conditions('name', '=', name)
    inv = res_ops.query_resource(res_dict[res_type], conditions)
    if inv:
        return inv[0]
    else:
        test_util.test_fail('Can not find the [%s] with name [%s]' % (res_type, name.encode('utf-8')))


class MINI(E2E):
    def __init__(self):
        super(MINI, self).__init__()
        self.vm_name = None
        self.volume_name = None
        self.image_name = None
        self.network_name = None
        self.eip_name = None
        self.vm_list = []
        self.volume_list = []
        self.image_list = []
        self.network_list = []
        self.eip_list = []
        if os.getenv('ZSTACK_SIMULATOR'):
            self.mini_server_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
        else:
            self.mini_server_ip = os.getenv('zstackHaVip')
        self.url('http://%s:8200' % self.mini_server_ip)
        self.window_size(1600, 900)
        self.login()

    def login(self, password='password'):
        test_util.test_logger('Log in normally')
        self.get_element('#accountName').input('admin')
        self.get_element('#password').input(password)
        # Login button
        self.get_element('button', 'tag name').click()
        self.wait_for_element(MESSAGETOAST, target='notDisappear')
        # root page
        if not self.wait_for_element('ant-layout-content'):
            test_util.test_fail('Fail to Login')

    def logout(self):
        test_util.test_logger('Log out')
        self.get_element(MENUSETTING).move_cursor_here()
        self.operate(u'退出登录')
        if not self.wait_for_element('#password'):
            test_util.test_fail('Fail to Logout')

    def change_mini_password(self, password='123456'):
        test_util.test_logger('Change the MINI password to [%s]' % password)
        self.get_element(MENUSETTING).move_cursor_here()
        self.operate(u'修改密码')
        self.get_element('#newPassword').input(password)
        self.get_element('#confirmPassword').input(password)
        self.click_ok()

    def login_with_cleartext_password(self):
        test_util.test_logger('Log in with clear-text password')
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
        assert self.get_elements('ant-layout-content')

    def login_without_accountname_or_password(self, with_accountName=False, with_password=False):
        test_util.test_logger('Log in without account name or password')
        if with_accountName:
            self.get_element('#accountName').input('admin')
        if with_password:
            self.get_element('#password').input('password')
        # Login button
        self.get_element('button', 'tag name').click()
        time.sleep(1)
        # check
        if not with_accountName or not with_password:
            self.wait_for_element(FORMEXPLAIN)
        if not with_accountName and with_password:
            assert self.get_element(FORMEXPLAIN).text == u'请输入用户名'
        elif with_accountName and not with_password:
            assert self.get_element(FORMEXPLAIN).text == u'请输入密码'
        elif not with_accountName and not with_password:
            assert self.get_elements(FORMEXPLAIN)[0].text == u'请输入用户名'
            assert self.get_elements(FORMEXPLAIN)[1].text == u'请输入密码'

    def login_with_wrong_accountname_or_password(self, waccountName=True, wpassword=True):
        test_util.test_logger('Log in with wrong account name or password')
        if waccountName:
            self.get_element('#accountName').input('wrongadmin')
        else:
            self.get_element('#accountName').input('admin')
        if wpassword:
            self.get_element('#password').input('wrongpassword')
        else:
            self.get_element('#password').input('password')
        # Login button
        self.get_element('button', 'tag name').click()
        self.wait_for_element('logintips___2GMLw')
        assert self.get_element('logintips___2GMLw').text == u'用户名或密码错误！'

    def navigate(self, menu):
        current_url = self.get_url()
        if menu not in current_url.split('/')[-1]:
            test_util.test_logger('Navigate to [%s]' % menu)
            self.get_element(MENUDICT[menu]).click()
            self.wait_for_element(PRIMARYBTN)
            time.sleep(2)

    def switch_view(self, view='card'):
        test_util.test_logger('switch the view to %s' % view)
        for elem in self.get_elements('ant-btn square___3vP_2'):
            if elem.get_elements(VIEWDICT[view]):
                elem.click()
                break
        time.sleep(1)

    def switch_tab(self, tab_name):
        test_util.test_logger('Switch to tab [%s]' % tab_name.encode('utf-8'))
        self.wait_for_page_render()
        for tab in self.get_elements('ant-tabs-tab'):
            if tab_name in tab.text:
                tab.click()
        time.sleep(1)

    def click_ok(self, assure_success=True):
        test_util.test_logger('Click OK button')
        self.wait_for_page_render()
        self.get_elements(PRIMARYBTN)[-1].click()
        if assure_success:
            if not self.wait_for_element(OPS_SUCCESS):
                test_util.test_fail("Fail: Operation Failed!")
        self.wait_for_element(MESSAGETOAST, timeout=300, target='disappear')
        time.sleep(1)

    def click_cancel(self):
        test_util.test_dsc('Click cancel button')
        self.get_elements(BTN)[-1].click()
        self.wait_for_element(MODALCONTENT, target='disappear')

    def click_close(self):
        test_util.test_logger('Click close button')
        self.get_element(EXITBTN).click()
        self.wait_for_element(MODALCONTENT, target='disappear')

    def more_operate(self, op_name, res_name, res_type=None, details_page=False):
        test_util.test_logger('Start more operate')
        res_list = []
        self.wait_for_element(CARDCONTAINER)
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
                elem = self.get_res_element(res)
                time.sleep(1)
                if not elem.get_element(CHECKBOX).selected:
                    test_util.test_logger('Select [%s]' % res.encode('utf-8'))
                    elem.get_element(CHECKBOX).click()
        self.get_element(MOREOPERATIONBTN).click()
        time.sleep(1)
        self.operate(op_name)
        test_util.test_logger('Finish more operate')

    def enter_details_page(self, res_type, name):
        inv = get_inv(name, res_type)
        lnk = 'a[href="/web/%s/%s"]' % (res_type, inv.uuid)
        test_util.test_logger('Enter into details page')
        self.get_element(lnk).click()
        time.sleep(1)

    def cancel_create_operation(self, res_type, close=False):
        test_util.test_logger('Cancel create operation of %s' % res_type)
        self.navigate(res_type)
        self.get_elements(PRIMARYBTN)[-1].click()
        if close:
            self.click_close()
        else:
            self.click_cancel()

    def cancel_more_operation(self, op_name, res_name, res_type, details_page=False, close=False):
        test_util.test_logger('Cancel more operation [%s] of %s' % (op_name.encode('utf-8'), res_type))
        self.navigate(res_type)
        self.more_operate(op_name, res_name, res_type, details_page)
        if close:
            self.click_close()
        else:
            self.click_cancel()

    def _create(self, para_dict, res_type, view, priority_dict=None):
        self.navigate(res_type)
        self.get_elements(PRIMARYBTN)[-1].click()
        time.sleep(1)
        for _elem in self.get_element(MODALCONTENT).get_elements('span', 'tag name'):
            if _elem.text == u'高级':
                _elem.click()
                break
        if priority_dict:
            for k, v in priority_dict.iteritems():
                if v is not None:
                    self.input(k, v)
        for k, v in para_dict.iteritems():
            if v is not None:
                self.input(k, v)
        self.click_ok()
        if not self.wait_for_element(MODALCONTENT, target='disappear'):
            if self.wait_for_element(FORMEXPLAIN):
                for elem in self.get_elements(FORMEXPLAIN):
                    test_util.test_logger('Error:' + elem.text.encode('utf-8'))
                test_util.test_fail('Create Error: check the previous error message')
        self.switch_view(view)
        elem = self.get_res_element(para_dict['name'])
        return elem

    def _delete(self, res_name, res_type, view, corner_btn=False, expunge=False, details_page=False, del_vol=False):
        isExpunge = False
        res_list = []
        if isinstance(res_name, types.ListType):
            res_list = res_name
            if len(res_list) > 1 and (corner_btn or details_page):
                test_util.test_fail("The args 'corner_btn' and 'details_page' are not for batch operation")
        else:
            res_list.append(res_name)
        if corner_btn and details_page:
            test_util.test_fail("The args 'corner_btn' and 'details_page' can not be both True")
        self.navigate(res_type)
        self.switch_view(view)
        primary_btn_num = len(self.get_elements(PRIMARYBTN))
        test_util.test_logger('%s %s [name: (%s)]' % (('Expunge' if primary_btn_num < PRIMARYBTNNUM else 'Delete'), res_type, ' '.join(res_list).encode('utf-8')))
        for res in res_list:
            _elem = self.get_res_element(res)
            if corner_btn:
                _elem.get_elements('button', 'tag name')[-1].click()
                break
            elif expunge and (primary_btn_num < PRIMARYBTNNUM):
                isExpunge = True
                if details_page:
                    self.more_operate(op_name=u'彻底删除', res_type=res_type, res_name=res_list, details_page=details_page)
                    break
                else:
                    _elem.get_element(CHECKBOX).click()
            else:
                self.more_operate(op_name=u'删除', res_type=res_type, res_name=res_list, details_page=details_page)
                self.check_confirm_item(res_list)
                break
        else:
            self.click_button(u'彻底删除')
            self.check_confirm_item(res_list)
        if del_vol:
            vol_check = self.get_element('#deleteVolume')
            if vol_check:
                vol_check.click()
        self.click_ok()
        if details_page:
            self.navigate(res_type)
        self.switch_tab(u'已删除')
        if isExpunge:
            self.check_res_item(res_list, target='notDisplayed')
            return True
        if res_type not in ['network', 'eip']:
            # check deleted
            self.check_res_item(res_list)
        if expunge:
            self._delete(res_list, res_type, view=view, expunge=True, details_page=details_page)

    def resume(self, res_name, res_type, view='card', details_page=False):
        res_list = []
        if isinstance(res_name, types.ListType):
            res_list = res_name
            if len(res_list) > 1 and details_page:
                test_util.test_fail("The args 'details_page' are not for batch operation")
        else:
            res_list.append(res_name)
        self.navigate(res_type)
        self.switch_tab(u'已删除')
        self.switch_view(view)
        test_util.test_logger('Resume %s [name: (%s)]' % (res_type, ' '.join(res_list)))
        for res in res_list:
            _elem = self.get_res_element(res)
            if details_page:
                self.more_operate(op_name=u'恢复',
                                  res_type=res_type,
                                  res_name=res_list,
                                  details_page=details_page)
                self.click_ok()
                break
            else:
                _elem.get_element(CHECKBOX).click()
        else:
            self.click_button(u'恢复')
            self.click_ok()
            self.wait_for_element(MESSAGETOAST, timeout=30, target='disappear')
        self.navigate(res_type)
        self.switch_tab(u'已有')
        self.check_res_item(res_list)

    def get_res_element(self, res_name):
        test_util.test_logger('Get the element [%s]' % res_name.encode('utf-8'))
        for _elem in self.get_elements(CARDCONTAINER):
            if res_name in _elem.text:
                return _elem
        test_util.test_fail('Can not find [%s]' % res_name.encode('utf-8'))

    def get_table_row(self, res_list):
        for res in res_list:
            for _row in self.get_elements(TABLEROW):
                if res in _row.text:
                    _row.get_element('input[type="checkbox"]').click()
                    break
            else:
                test_util.test_fail('Can not find the res with name [%s]' % res)

    def get_detail_info(self, res_name, res_type, info_name):
        test_util.test_logger('Get the detail info of [%s] with info name [%s]' % (res_name, info_name.encode('utf-8')))
        self.enter_details_page(res_type, res_name)
        for elem in self.get_elements("cardField___2SE_p"):
            if info_name in elem.text:
                info = elem.get_element('ant-typography-ellipsis').text
                self.go_backward()
                return info
        test_util.test_fail('Can not find the detail info of [%s] with info name [%s]' % (res_name, info_name.encode('utf-8')))

    def check_res_item(self, res_list, target='displayed'):
        test_util.test_logger('Check if %s %s' % (res_list, target))
        if not isinstance(res_list, types.ListType):
            test_util.test_fail("The first parameter of function[check_res_item] expected list_type")
        for res in res_list:
            expected = '[%s] is expected to be [%s]!' % (res, target)
            all_res_text = self.get_element(SPINCONTAINER).text
            if target == 'displayed':
                assert res in all_res_text, expected
            else:
                assert res not in all_res_text, expected
        test_util.test_logger('%s %s, check Pass' % (res_list, target))

    def check_confirm_item(self, res_list):
        test_util.test_logger('Check if %s confirmed' % res_list)
        self.wait_for_element(MODALCONTENT)
        confirm_items = self.get_elements(CONFIRMITEM)
        for res in res_list:
            for item in confirm_items:
                if res == item.text:
                    break
            else:
                test_util.test_fail('%s should to be confirmed' % res)

    def check_menu_item_disabled(self, name, res_type, op_name):
        self.navigate(res_type)
        elem = self.get_res_element(name)
        if not elem.get_element(CHECKBOX).selected:
            elem.get_element(CHECKBOX).click()
        self.get_element(MOREOPERATIONBTN).click()
        op_selector = 'ant-dropdown-menu-item|ant-menu-item'
        _elem = self.get_element('actionsContainer___1Ce9C')
        if _elem is not None:
            op_selector = 'span'
            strategy = 'tag name'
        for op in _elem.get_elements(op_selector, strategy) if _elem else self.get_elements(op_selector):
            if op.text == op_name:
                if _elem:
                    assert op.get_attribute('class') == 'actionDisabled___1Bze5'
                else:
                    assert op.enabled == False
                # recover
                self.get_element(MOREOPERATIONBTN).click()

    def check_browser_console_log(self):
        errors = []
        logs = self.get_console_log()
        for log in logs:
            if log.level == 'SEVERE':
                errors.append(log.messge)
        if errors:
            if os.getenv('FailWhenConsoleError'):
                test_util.test_fail("Browser console errors: %s" % errors)
            else:
                test_util.test_logger("Browser console errors: %s" % errors)

    def wait_for_page_render(self):
        for _ in xrange(10):
            # Refresh button element: get_elements(PRIMARYBTN)[0]
            if self.get_elements(PRIMARYBTN):
                if self.get_elements(PRIMARYBTN)[0].get_attribute('disabled') == 'true':
                    test_util.test_logger('The page rendering is not finished, check again')
                    time.sleep(0.5)
                else:
                    time.sleep(1)
                    return True
            else:
                time.sleep(1)

    def end_action(self, action_name):
        if action_name == 'confirm':
            self.click_ok()
        elif action_name == 'cancel':
            self.click_cancel()
        elif action_name == 'close':
            self.click_close()

    def create_vm(self, name=None, dsc=None, image=None, root_size=None, cpu=1, mem='1 GB', data_size=None,
                  user_data=None, network=None, cluster=None, provisioning=u'厚置备', view='card'):
        image = image if image else os.getenv('imageName_s')
        network = network if network else os.getenv('l3PublicNetworkName')
        cluster = cluster if cluster else os.getenv('clusterName')
        self.vm_name = name if name else 'vm-' + get_time_postfix()
        self.vm_list.append(self.vm_name)
        test_util.test_logger('Create VM [%s]' % self.vm_name.encode('utf-8'))
        priority_dict = {'imageUuid': image}
        vm_dict = {'name': self.vm_name,
                   'description': dsc,
                   'rootSize': root_size.split() if root_size else None,
                   'cpuNum': cpu,
                   'memorySize': mem.split(),
                   'dataSize': data_size.split() if data_size else None,
                   'userData': user_data,
                   'l3NetworkUuids': network,
                   'clusterUuid': cluster,
                   'provisioning': provisioning}
        vm_elem = self._create(vm_dict, 'vm', view=view, priority_dict=priority_dict)
        vm_inv = get_inv(self.vm_name, "vm")
        check_list = [self.vm_name, str(cpu), mem, vm_inv.vmNics[0].ip]
        checker = MINICHECKER(self, vm_elem)
        checker.vm_check(vm_inv, check_list, ops='new_created')
        if data_size:
            test_util.test_logger('Create Volume [%s]' % self.volume_name)
            self.volume_name = 'Disk-' + self.vm_name
            self.volume_list.append(self.volume_name)
            volume_check_list = [self.volume_name, data_size, self.vm_name]
            self.navigate('volume')
            elem = self.get_res_element(self.volume_name)
            checker = MINICHECKER(self, elem)
            checker.volume_check(volume_check_list, ops='attached')

    def create_volume(self, name=None, dsc=None, size='2 GB', cluster=None, vm=None, provisioning=u'厚置备', view='card'):
        cluster = cluster if cluster else os.getenv('clusterName')
        self.volume_name = name if name else 'volume-' + get_time_postfix()
        self.volume_list.append(self.volume_name)
        test_util.test_logger('Create Volume [%s]' % self.volume_name)
        volume_dict = {'name': self.volume_name,
                       'description': dsc,
                       'dataSize': size.split(),
                       'clusterUuid': cluster,
                       'vmUuid': vm,
                       'provisioning': provisioning}
        volume_elem = self._create(volume_dict, "volume", view=view)
        checker = MINICHECKER(self, volume_elem)
        if vm:
            check_list = [self.volume_name, vm, size]
            checker.volume_check(check_list)
        else:
            check_list = [self.volume_name, size]
            checker.volume_check(check_list=check_list, ops='detached')

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
        network_elem = self._create(network_dict, "network", view=view)
        ip_num = abs(int(start_ip.split('.')[-1]) - int(end_ip.split('.')[-1])) + 1
        check_list = [self.network_name, physical_interface, str(ip_num)]
        if vlan:
            check_list.append(vlan)
        else:
            check_list.append('-')
        checker = MINICHECKER(self, network_elem)
        checker.network_check(check_list)

    def add_image(self, name=None, dsc=None, adding_type='url', url=None, local_file=None, platform='Linux', view='card'):
        self.image_name = name if name else 'image-' + get_time_postfix()
        self.image_list.append(self.image_name)
        url = url if url else os.getenv('imageUrl_net')
        test_util.test_logger('Add Image [%s]' % self.image_name)
        priority_dict = {'type': adding_type}
        image_dict = {'name': self.image_name,
                      'description': dsc,
                      'url': url,
                      'file': local_file,
                      'platform': platform}
        if adding_type == 'url':
            image_dict.pop('file')
        elif adding_type == 'file':
            image_dict.pop('url')
        image_elem = self._create(image_dict, "image", view=view, priority_dict=priority_dict)
        check_list = [self.image_name, url.split('.')[-1]]
        checker = MINICHECKER(self, image_elem)
        checker.image_check(check_list)

    def create_eip(self, name=None, dsc=None, network=None, required_ip=None, view='card'):
        self.eip_name = name if name else 'EIP-' + get_time_postfix()
        self.eip_list.append(self.eip_name)
        network = network if network else os.getenv('l3PublicNetworkName')
        test_util.test_logger('Create EIP[%s]' % self.eip_name)
        priority_dict = {'l3NetworkUuid': network}
        eip_dict = {'name': self.eip_name,
                    'description': dsc,
                    'requiredIp': required_ip}
        eip_elem = self._create(eip_dict, "eip", view=view, priority_dict=priority_dict)
        check_list = [self.eip_name]
        if required_ip is not None:
            check_list.append(required_ip)
        checker = MINICHECKER(self, eip_elem)
        checker.eip_check(check_list)

    def delete_vm(self, vm_name=None, view='card', corner_btn=True, details_page=False, del_vol=False):
        vm_name = vm_name if vm_name else self.vm_list
        self._delete(vm_name, 'vm', view=view, corner_btn=corner_btn, details_page=details_page, del_vol=del_vol)

    def expunge_vm(self, vm_name=None, view='card', details_page=False):
        vm_name = vm_name if vm_name else self.vm_list
        self._delete(vm_name, 'vm', view=view, expunge=True, details_page=details_page)

    def delete_volume(self, volume_name=None, view='card', corner_btn=True, details_page=False):
        volume_name = volume_name if volume_name else self.volume_list
        self._delete(volume_name, 'volume', view=view, corner_btn=corner_btn, details_page=details_page)

    def expunge_volume(self, volume_name=None, view='card', details_page=False):
        volume_name = volume_name if volume_name else self.volume_list
        self._delete(volume_name, 'volume', view=view, expunge=True, details_page=details_page)

    def delete_image(self, image_name=None, view='card', corner_btn=True, details_page=False):
        image_name = image_name if image_name else self.image_list
        self._delete(image_name, 'image', view=view, corner_btn=corner_btn, details_page=details_page)

    def expunge_image(self, image_name=None, view='card', details_page=False):
        image_name = image_name if image_name else self.image_list
        self._delete(image_name, 'image', view=view, expunge=True, details_page=details_page)

    def delete_network(self, network_name=None, view='card', corner_btn=True, details_page=False):
        network_name = network_name if network_name else self.network_list
        self._delete(network_name, 'network', view=view, corner_btn=corner_btn, details_page=details_page)

    def delete_eip(self, eip_name=None, view='card', corner_btn=True, details_page=False):
        eip_name = eip_name if eip_name else self.eip_list
        self._delete(eip_name, 'eip', view=view, corner_btn=corner_btn, details_page=details_page)

    def update_info(self, res_type, res_name, new_name, new_dsc=None, corner_btn=False, details_page=False, view='card'):
        if res_type == 'minihost' and corner_btn:
            test_util.test_fail('Minihost do not support to update info by corner btn.')
        check_list = []
        self.navigate(res_type)
        self.switch_view(view)
        if res_type == 'minihost':
            for elem in self.get_elements('ant-row-flex-middle'):
                if res_name in elem.text:
                    if not details_page:
                        elem.get_element(CHECKBOX).click()
                    else:
                        self.get_element('left-part').click()
                        time.sleep(1)
                    break
            self.get_element(MOREOPERATIONBTN).click()
            time.sleep(1)
            self.operate(u'修改信息')
        else:
            _elem = self.get_res_element(res_name)
            if corner_btn:
                _elem.get_elements('button', 'tag name')[1].click()
            else:
                self.more_operate(u'修改信息', res_name=res_name, res_type=res_type, details_page=details_page)
        if new_name is not None:
            test_util.test_logger('Update the name of [%s] to %s' % (res_name, new_name))
            self.input('name', new_name)
            check_list.append(new_name)
        if new_dsc is not None:
            test_util.test_logger('Update the dsc of [%s] to %s' % (res_name, new_dsc))
            self.input('description', new_dsc)
        self.click_ok()
        if res_type == 'minihost':
            for _elem in self.get_elements('ant-row-flex-middle'):
                if new_name in _elem.text:
                    break
        else:
            _elem = self.get_res_element(new_name)
        checker = MINICHECKER(self, _elem)
        if res_type == 'volume':
            checker.volume_check(check_list)
        elif res_type == 'vm':
            checker.vm_check(check_list)
        elif res_type == 'image':
            checker.image_check(check_list)
        elif res_type == 'minihost':
            checker.host_check(check_list)
        else:
            pass

    def search(self, value, search_by=u'名称', type='vm', tab_name=u'已有', not_null=False):
        test_util.test_logger('Search %s by %s' % (value.encode('utf-8'), search_by.encode('utf-8')))
        self.navigate(type)
        self.switch_tab(tab_name)
        self.get_element('ant-input-group-addon').click()
        self.wait_for_element('ul[role="listbox"]')
        time.sleep(1)
        for op in self.get_elements('li[role="option"]'):
            if op.text == search_by:
                op.click()
                break
        else:
            test_util.test_fail("Failed: Search by [%s] is not supported" % search_by.encode('utf-8'))
        self.get_element('ant-input').clear()
        # u'\ue007' means sending enter key
        self.get_element('ant-input').input(u'\ue007')
        self.wait_for_page_render()
        self.get_element('ant-input').input(value + u'\ue007')
        self.wait_for_page_render()
        # check
        for _elem in self.get_elements(CARDCONTAINER):
            assert value.lower() in _elem.text.lower()
        res_num = len(self.get_elements(CARDCONTAINER))
        if not_null:
            assert res_num > 0
        for tab in self.get_elements('ant-tabs-tab'):
            if tab_name in tab.text:
                assert str(res_num) in tab.text

    def upgrade_capacity(self, name, res_type, new_capacity, details_page=False):
        self.navigate(res_type)
        capacity = self.get_detail_info(name, res_type, u'容量')
        test_util.test_logger('Upgrade system capacity of [%s] from %s to %s' % (name, capacity, new_capacity))
        if res_type == 'vm':
            self.more_operate(u'系统扩容', res_type=res_type, res_name=name, details_page=details_page)
        elif res_type == 'volume':
            self.more_operate(u'数据盘扩容', res_type=res_type, res_name=name, details_page=details_page)
        self.input('dataSize', new_capacity.split())
        self.click_ok()
        capacity = self.get_detail_info(name, res_type, u'容量')
        if capacity != new_capacity:
            test_util.test_fail("Failed to upgrade capacity of [%s] to %s" % (name, new_capacity))

    def vm_ops(self, vm_name, action='stop', details_page=False):
        self.navigate('vm')
        vm_list = []
        if isinstance(vm_name, types.ListType):
            vm_list = vm_name
        else:
            vm_list.append(vm_name)
        ops_dic = {'start': u'启动',
                   'stop': u'停止',
                   'reboot': u'重启'
                   }
        test_util.test_logger('VM (%s) execute action[%s]' % (' '.join(vm_list), action))
        if not details_page:
            for vm in vm_list:
                vm_elem = self.get_res_element(vm)
                vm_elem.get_element(CHECKBOX).click()
        if action == 'reboot':
            self.more_operate(ops_dic[action], vm_list, res_type='vm', details_page=details_page)
            self.click_ok()
        else:
            if details_page:
                self.more_operate(ops_dic[action], vm_list, res_type='vm', details_page=True)
            else:
                self.click_button(ops_dic[action])
        self.wait_for_element(MESSAGETOAST, timeout=300, target='disappear')

    def set_ha_level(self, vm_name, ha=True, details_page=False):
        test_util.test_logger('Set [%s] ha leval [%s]' % (vm_name, ha))
        check_list = []
        self.navigate('vm')
        self.more_operate(u'高可用', res_type='vm', res_name=vm_name, details_page=details_page)
        if ha:
            check_list.append('NeverStop')
        else:
            check_list.append('None')
        if ha and (self.get_element('ant-switch-inner').text == u"关闭"):
            self.get_element("button[id='haLevel']").click()
        elif not ha and (self.get_element('ant-switch-inner').text == u"打开"):
            self.get_element("button[id='haLevel']").click()
        self.click_ok()
        self.switch_view('list')
        vm_elem = self.get_res_element(vm_name)
        checker = MINICHECKER(self, vm_elem)
        checker.vm_check(check_list)

    def set_qga(self, vm_name, qga=True, details_page=False):
        test_util.test_logger('Set [%s] QGA [%s]' % (vm_name, qga))
        self.navigate('vm')
        self.more_operate('QGA', res_type='vm', res_name=vm_name, details_page=details_page)
        if qga and (self.get_element('ant-switch-inner').text == u"关闭"):
            self.get_element("button[id='qga']").click()
        elif not qga and (self.get_element('ant-switch-inner').text == u"打开"):
            self.get_element("button[id='qga']").click()
        self.click_ok()
        # check
        if not qga:
            self.check_menu_item_disabled(vm_name, 'vm', u'修改云主机密码')

    def change_vm_password(self, vm_name, account='root', password='123456', details_page=False):
        test_util.test_logger('Change the password of [%s] to %s' % (vm_name, password))
        self.navigate('vm')
        self.more_operate(u'修改云主机密码', vm_name, res_type='vm', details_page=details_page)
        self.get_element('#account').input(account)
        self.get_element('#password').input(password)
        self.click_ok()

    def live_migrate(self, vm_name, details_page=False):
        test_util.test_logger('Live migrate VM')
        self.navigate('vm')
        old_host = self.get_detail_info(vm_name, 'vm', u'所在物理机:')
        self.more_operate(u'迁移', res_type='vm', res_name=vm_name, details_page=details_page)
        self.click_ok()
        new_host = self.get_detail_info(vm_name, 'vm', u'所在物理机:')
        test_util.test_logger('Live migrate [%s] from host[%s] to host[%s] Successful' % (vm_name, old_host, new_host))

    def create_vm_image(self, vm_name, image_name, dsc=None, platform='Linux'):
        test_util.test_logger('Create the vm image named[%s] for vm[%s]' % (image_name, vm_name))
        image_list = []
        image_list.append(image_name)
        input_dict = {'name': image_name,
                      'description': dsc,
                      'platform': platform}
        self.more_operate(u'创建镜像', vm_name, res_type='vm', details_page=True)
        for k, v in input_dict.iteritems():
            if v is not None:
                self.input(k, v)
        self.click_ok()
        self.navigate('image')
        self.check_res_item(image_list)

    def open_vm_console(self, vm_name, details_page=False):
        test_util.test_logger('Open the console of [%s]' % vm_name)
        self.navigate('vm')
        if details_page:
            self.enter_details_page('vm', vm_name)
            self.get_elements('button', 'tag name')[0].click()
        else:
            _elem = self.get_res_element(vm_name)
            _elem.get_elements('button', 'tag name')[0].click()
        while True:
            if len(self.get_window_handles()) == 1:
                time.sleep(0.5)
            else:
                break
        old_handle = self.window_handle
        for handle in self.get_window_handles():
            if handle != old_handle:
                self.change_window(handle)
        self.wait_for_element('noVNC_status_normal')
        self.close_window()
        self.change_window(self.window_handle)

    def set_console_password(self, vm_name, password='123456', details_page=False, end_action='confirm'):
        test_util.test_logger('Set the console password of [%s]' % vm_name)
        self.navigate('vm')
        self.more_operate(u'设置控制台密码', vm_name, res_type='vm', details_page=details_page)
        self.get_element('#newpassword').input(password)
        self.get_element('#confirmpassword').input(password)
        self.get_elements(CHECKBOX)[-1].click()
        self.end_action(end_action)
        # check
        if end_action == 'confirm':
            self.check_menu_item_disabled(vm_name, 'vm', u'设置控制台密码')

    def cancel_console_password(self, vm_name, details_page=False, end_action='confirm'):
        test_util.test_logger('Cancel the console password of [%s]' % vm_name)
        self.navigate('vm')
        self.more_operate(u'取消控制台密码', vm_name, res_type='vm', details_page=details_page)
        self.end_action(end_action)
        # check
        if end_action == 'confirm':
            self.check_menu_item_disabled(vm_name, 'vm', u'取消控制台密码')

    def set_boot_order(self, vm_name, cd_first=True, details_page=False):
        test_util.test_logger('Set the boot order of [%s]' % vm_name)
        self.navigate('vm')
        self.more_operate(u'设置启动顺序', vm_name, res_type='vm', details_page=details_page)
        boot_order = u'光盘，硬盘' if cd_first else u'硬盘，光盘'
        self.input('bootOrder', boot_order)
        self.get_elements(CHECKBOX)[-1].click()
        self.click_ok()
        # check
        self.more_operate(u'设置启动顺序', vm_name, res_type='vm', details_page=details_page)
        assert boot_order in self.get_element('ant-row ant-form-item').text
        self.click_cancel()

    def vm_attach_volume(self, vm_name, volume_name, end_action='confirm'):
        volume_list = []
        if isinstance(volume_name, types.ListType):
            volume_list = volume_name
        else:
            volume_list.append(volume_name)
        test_util.test_logger('VM[%s] attach volume (%s)' % (vm_name, ' '.join(volume_list)))
        self.navigate('vm')
        self.enter_details_page('vm', vm_name)
        self.switch_tab(u'配置信息')
        self.get_elements(MOREOPERATIONBTN)[-1].move_cursor_here()
        self.operate(u'加载')
        self.get_table_row(volume_list)
        self.end_action(end_action)
        if end_action == 'confirm':
            self.check_res_item(volume_list)

    def vm_detach_volume(self, vm_name, volume_name, end_action='confirm'):
        volume_list = []
        if isinstance(volume_name, types.ListType):
            volume_list = volume_name
        else:
            volume_list.append(volume_name)
        test_util.test_logger('VM[%s] detach volume (%s)' % (vm_name, ' '.join(volume_list)))
        self.navigate('vm')
        self.enter_details_page('vm', vm_name)
        self.switch_tab(u'配置信息')
        self.get_table_row(volume_list)
        self.get_elements(MOREOPERATIONBTN)[-1].move_cursor_here()
        self.operate(u'卸载')
        self.end_action(end_action)
        if end_action == 'confirm':
            self.check_res_item(volume_list, target='notDisplayed')

    def volume_attach_to_vm(self, volume_name=[], dest_vm=None, details_page=False):
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
            test_util.test_fail('Can not find the dest-vm with name [%s]' % dest_vm)
        _row.get_element('input[type="radio"]').click()
        self.click_ok()
        check_list = [dest_vm]
        for vol in volume_list:
            _elem = self.get_res_element(vol)
            MINICHECKER(self, _elem).volume_check(check_list)
            test_util.test_logger('[%s] attach to [%s] successfully' % (vol, dest_vm))

    def volume_detach_from_vm(self, volume_name=[], details_page=False):
        emptyl = []
        volume_list = volume_name if volume_name != [] else self.volume_name
        if not isinstance(volume_list, types.ListType):
            emptyl.append(volume_list)
            volume_list = emptyl
        self.navigate('volume')
        self.more_operate(u'卸载', res_type='volume', res_name=volume_list, details_page=details_page)
        self.click_ok()
        for vol in volume_list:
            _elem = self.get_res_element(vol)
            MINICHECKER(self, _elem).volume_check(ops='detached')
            test_util.test_logger('[%s] detach from vm successfully' % vol)

    def add_dns_to_l3(self, network=None, dns='8.8.8.8', details_page=True, end_action='confirm'):
        network = network if network else os.getenv('l3PublicNetworkName')
        test_util.test_logger('Add dns [%s] to l3 [%s]' % (dns, network))
        self.navigate('network')
        if details_page:
            self.enter_details_page('network', network)
            self.switch_tab('DNS')
            self.get_elements(MOREOPERATIONBTN)[-1].move_cursor_here()
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
        self.get_elements(MOREOPERATIONBTN)[-1].move_cursor_here()
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
            self.get_elements(MOREOPERATIONBTN)[-1].move_cursor_here()
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
        self.get_elements(MOREOPERATIONBTN)[-1].move_cursor_here()
        self.operate(u'删除网络段')
        self.click_ok()
        check_list = []
        check_list.append(start_ip)
        check_list.append(end_ip)
        self.check_res_item(check_list, target='notDisplayed')

    def host_ops(self, host_name, action, details_page=False):
        self.navigate('minihost')
        host_list = []
        if isinstance(host_name, types.ListType):
            host_list = host_name
        else:
            host_list.append(host_name)
        ops_list = {'enable': u'启用',
                    'disable': u'停用',
                    'reconnect': u'重连',
                    'maintenance': u'维护模式',
                    'light': u'维修灯亮'}
        test_util.test_logger('Host (%s) execute action[%s]' % (' '.join(host_list), action))
        for host in host_list:
            for elem in self.get_elements('ant-row-flex-middle'):
                if host in elem.text:
                    if not details_page:
                        if not elem.get_element(CHECKBOX).selected:
                            elem.get_element(CHECKBOX).click()
                    else:
                        self.get_element('left-part').click()
                        time.sleep(1)
                        break
        if details_page:
            self.get_element(MOREOPERATIONBTN).click()
            time.sleep(1)
            self.operate(ops_list[action])
        else:
            if action in ['enable', 'disable']:
                self.click_button(ops_list[action])
            else:
                self.get_element(MOREOPERATIONBTN).click()
                time.sleep(1)
                self.operate(ops_list[action])
        self.wait_for_element(MESSAGETOAST, timeout=300, target='disappear')

    def eip_binding(self, eip_name, vm_name):
        test_util.test_logger("Bind %s to %s" % (eip_name, vm_name))
        vm_inv = get_inv(self.vm_name, "vm")
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

    def get_err_log(self, filename=None):
        filename = '.'.join(['err_log-' + get_time_postfix(), 'tmpt']) if filename is None else filename
        test_util.test_logger("Get err log")
        self.navigate('log')
        next_btn = self.get_elements("button", "tag name")[-1]
        while next_btn.enabled:
            for line in self.get_elements('ant-table-row-level-0'):
                if u"失败" in line.text:
                    arrow = line.get_element('anticon-down')
                    arrow.click()
                    for log_content in self.get_elements('ant-table-expanded-row-level-1'):
                        if log_content.displayed():
                            log_body = log_content.get_element('body___2c2z6')
                            break
                    try:
                        with open(join(LOG_FILE_PATH, filename), 'ab') as f:
                            f.write(line.text.encode("utf-8"))
                            f.write("\n")
                            f.write(log_body.text.encode("utf-8"))
                            f.write("\n----------*----------\n")
                    except IOError:
                        test_util.test_fail("Fail: IOError")
                    arrow.click()
            next_btn.click()

    def save_element_location(self, filename=None):
        filename = '.'.join(['elem_location-' + get_time_postfix(), 'tmpt']) if filename is None else filename
        for menu, page in MENUDICT.items():
            loc = {}
            loc[menu] = self.get_element(page).location
            json_loc = jsonobject.dumps(loc)
            try:
                with open(join(LOG_FILE_PATH, filename), 'ab') as f:
                    f.write(json_loc)
            except IOError:
                test_util.test_fail("Fail: IOError")

    def enabled_status_checker(self):
        self.navigate('vm')
        btn_elems = self.get_elements('button', 'tag name')
        start_btn = [btn_elem for btn_elem in btn_elems if btn_elem.text == u'启动'][0]
        stop_btn = [btn_elem for btn_elem in btn_elems if btn_elem.text == u'停止'][0]
        assert start_btn.enabled == False
        assert start_btn.enabled == False

        vm_elems = self.get_elements(CARDCONTAINER)
        vm_checkboxs = self.get_elements(CHECKBOX)

        # the checkboxs clicked will detach to the page document
        def update_checkboxs():
            return self.get_elements(CHECKBOX)

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
        test_util.test_logger('Elemnet text to check:\n%s' % elem.text.encode('utf-8'))

    def vm_check(self, inv=None, check_list=[], ops=None):
        ops_dict = {'new_created': u'运行中',
                    'start': u'运行中',
                    'stop': u'已停止',
                    'resume': u'已停止'}
        if ops:
            check_list.append(ops_dict[ops])
        for v in check_list:
            not_ready_list = [u'重启中']
            if any(x in self.elem.text for x in not_ready_list):
                time.sleep(1)
                continue
            elif v not in self.elem.text:
                test_util.test_fail("Can not find %s in vm checker" % v.encode('utf-8'))
            test_util.test_logger("Find %s in vm checker successful" % v.encode('utf-8'))

    def volume_check(self, check_list=[], ops=None):
        if ops == 'detached':
            check_list.append(u'未加载')
        for v in check_list:
            if v not in self.elem.text:
                test_util.test_fail("Can not find %s in volume checker" % v.encode('utf-8'))
            test_util.test_logger("Find %s in volume checker successful" % v.encode('utf-8'))

    def image_check(self, check_list=[]):
        check_list.append(u'就绪')
        for v in check_list:
            not_ready_list = [u'下载中', u'计算中', u'解析中']
            if any(x in self.elem.text for x in not_ready_list):
                time.sleep(1)
                continue
            elif v not in self.elem.text:
                test_util.test_fail("Can not find %s in image checker" % v.encode('utf-8'))
            test_util.test_logger("Find %s in image checker successful" % v.encode('utf-8'))

    def network_check(self, check_list=[]):
        for v in check_list:
            if v not in self.elem.text:
                test_util.test_fail("Can not find %s in network checker" % v.encode('utf-8'))
            test_util.test_logger("Find %s in network checker successful" % v.encode('utf-8'))

    def host_check(self, check_list=[]):
        for v in check_list:
            if v not in self.elem.text:
                test_util.test_fail("Can not find %s in network checker" % v.encode('utf-8'))
            test_util.test_logger("Find %s in host checker successful" % v.encode('utf-8'))

    def eip_check(self, check_list=[]):
        for v in check_list:
            if v not in self.elem.text:
                test_util.test_fail("Can not find %s in eip checker" % v.encode('utf-8'))
            test_util.test_logger("Find %s in eip checker successful" % v.encode('utf-8'))
