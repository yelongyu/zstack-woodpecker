# -*- coding:utf-8 -*-
'''

Create an unified test_stub for E2E test operations

@author: Legion
'''

import os
import time
import types
import random
from os.path import join
from zstackwoodpecker.e2e_lib import E2E
import zstackwoodpecker.operations.resource_operations as res_ops
from zstackwoodpecker import test_util
import zstacklib.utils.jsonobject as jsonobject

LOCATION_FILE_PATH = '/root/.zstackwoodpecker/integrationtest/vm/e2e_mini/'
COMMONIMAGE = 'http://172.20.1.28/mirror/diskimages/centos7-test.qcow2'
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
PRIMARYBTNNUM = 2


MENUDICT = {'homepage': 'a[href="/web/"]',
            'monitor':  'a[href="/web/monitoringCenter"]',
            'vm':       'a[href="/web/vm"]',
            'host':     'a[href="/web/minihost"]',
            'ps':       'a[href="/web/primaryStorage"]',
            'volume':   'a[href="/web/volume"]',
            'image':    'a[href="/web/image"]',
            'network':  'a[href="/web/network"]',
            'alarm':    'a[href="/web/alarmMessage"]'}

VIEWDICT = {'list': '#btn_listswitch_s',
            'card': '#btn_cardswitch_s'}


def get_time_postfix():
    rand_postfix = str(random.random()).split('.')[-1]
    return time.strftime('%y%m%d-%H%M%S', time.localtime()) + '-' + rand_postfix

def get_inv(name, res_type):
    res_dict = {'vm': res_ops.VM_INSTANCE,
                'volume': res_ops.VOLUME,
                'minihost': res_ops.CLUSTER,
                'network': res_ops.L3_NETWORK,
                'image': res_ops.IMAGE,
                'primaryStorage': res_ops.PRIMARY_STORAGE}
    conditions = res_ops.gen_query_conditions('name', '=', name)
    inv = res_ops.query_resource(res_dict[res_type], conditions)
    if inv:
        return inv[0]
    else:
        test_util.test_fail('Can not find the [%s] with name [%s]' % (res_type, name))


class MINI(E2E):
    def __init__(self):
        super(MINI, self).__init__()
        self.vm_name = None
        self.volume_name = None
        self.image_name = None
        self.network_name = None
        self.vm_list = []
        self.volume_list = []
        self.image_list = []
        self.network_list = []
        if os.getenv('ZSTACK_SIMULATOR'):
            self.mini_server_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
        else:
            self.mini_server_ip = os.getenv('zstackHaVip')
        self.url('http://%s:8200' % self.mini_server_ip)
        self.window_size(1600, 900)
        self.login()

    def login(self):
        test_util.test_logger('Log in normally')
        self.get_element('#accountName').input('admin')
        self.get_element('#password').input('password')
        # Login button
        self.get_element('button', 'tag name').click()
        self.wait_for_element(MESSAGETOAST)
        assert self.get_elements(MESSAGETOAST)
        # root page
        assert self.get_elements('ant-layout-content')

    def logout(self):
        test_util.test_logger('Log out')
        self.get_element('img', 'tag name').move_cursor_here()
        self.operate(u'登出')
        assert self.get_elements('#password')

    def switch_view(self, view='card'):
        test_util.test_logger('switch the view to %s' % view)
        for elem in self.get_elements('ant-btn square___3vP_2'):
            if elem.get_elements(VIEWDICT[view]):
                elem.click()
                break

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
        self.wait_for_element(MESSAGETOAST, timeout=300)
        assert 'wrong account name or password' in self.get_element('ant-notification-notice-description').text

    def navigate(self, menu):
        current_url = self.get_url()
        if menu not in current_url.split('/')[-1]:
            test_util.test_logger('Navigate to [%s]' % menu)
            self.get_element(MENUDICT[menu]).click()
            self.wait_for_element(PRIMARYBTN)
            time.sleep(2)

    def click_ok(self):
        test_util.test_logger('Click OK button')
        self.get_elements(PRIMARYBTN)[-1].click()
        self.wait_for_element(MESSAGETOAST, timeout=300, target='disappear')
        self.wait_for_page_render()
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
                test_util.test_logger('Select [%s]' % res)
                elem = self.get_res_element(res)
                elem.get_element(CHECKBOX).click()
        self.get_element(MOREOPERATIONBTN).move_cursor_here()
        self.operate(op_name)

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
        test_util.test_logger('Cancel more operation [%s] of %s' % (op_name, res_type))
        self.navigate(res_type)
        self.more_operate(op_name, res_name, res_type, details_page)
        if close:
            self.click_close()
        else:
            self.click_cancel()

    def get_res_element(self, res_name):
        test_util.test_logger('Get the element [%s]' % res_name)
        for _elem in self.get_elements(CARDCONTAINER):
            if res_name in _elem.text:
                return _elem
        test_util.test_fail('Can not find [%s]' % res_name)

    def _create(self, para_dict, res_type, view, priority_dict=None):
        self.navigate(res_type)
        self.get_elements(PRIMARYBTN)[-1].click()
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
        if view == 'list':
            self.switch_view(view)
        elem = self.get_res_element(para_dict['name'])
        return elem

    def _delete(self, res_name, res_type, corner_btn=False, expunge=False, details_page=False):
        primary_btn_num = len(self.get_elements(PRIMARYBTN))
        res_list = []
        if isinstance(res_name, types.ListType):
            res_list = res_name
            if len(res_list) > 1 and (corner_btn or details_page):
                test_util.test_fail("The args 'corner_btn' and 'details_page' are not for batch operation")
        else:
            res_list.append(res_name)
        self.navigate(res_type)
        test_util.test_logger('%s %s [name: (%s)]' % (('Expunge' if primary_btn_num < PRIMARYBTNNUM else 'Delete'),
                                                   res_type, ' '.join(res_list)))
        for res in res_list:
            _elem = self.get_res_element(res)
            if corner_btn:
                _elem.get_elements('button', 'tag name')[-1].click()
                break
            elif expunge and primary_btn_num < PRIMARYBTNNUM:
                if details_page:
                    self.more_operate(op_name=u'彻底删除',
                                      res_type=res_type,
                                      res_name=res_list,
                                      details_page=details_page)
                    break
                else:
                    _elem.get_element(CHECKBOX).click()
            else:
                self.more_operate(op_name=u'删除',
                                  res_type=res_type,
                                  res_name=res_list,
                                  details_page=details_page)
                break
        else:
            self.click_button(u'彻底删除')
        self.click_ok()
        self.check_res_item(res_list, target='notDisplayed')
        if primary_btn_num < PRIMARYBTNNUM:
            return True
        self.switch_tab(u'已删除')
        if res_type != 'network':
            # check deleted
            self.check_res_item(res_list)
        if expunge:
            self._delete(res_list, res_type, expunge=True, details_page=details_page)

    def resume(self, res_name, res_type, details_page=False):
        res_list = []
        if isinstance(res_name, types.ListType):
            res_list = res_name
        else:
            res_list.append(res_name)
        self.navigate(res_type)
        self.switch_tab(u'已删除')
        test_util.test_logger('Resume %s [name: (%s)]' % (res_type, ' '.join(res_list)))
        for res in res_list:
            _elem = self.get_res_element(res)
            if details_page:
                self.more_operate(op_name=u'恢复',
                                  res_type=res_type,
                                  res_name=res_list,
                                  details_page=details_page)
                break
            else:
                _elem.get_element(CHECKBOX).click()
        else:
            self.click_button(u'恢复')
            self.wait_for_element(MESSAGETOAST, timeout=30, target='disappear')
            self.switch_tab(u'已有')
        self.navigate(res_type)
        self.check_res_item(res_list)
        self.switch_tab(u'已删除')
        self.check_res_item(res_list, 'notDisplayed')
        self.switch_tab(u'已有')

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
                    return True
            else:
                time.sleep(1)
                return True

    def switch_tab(self, tab_name):
        test_util.test_logger('Switch to tab [%s]' % tab_name.encode('utf-8'))
        for tab in self.get_elements('ant-tabs-tab'):
            if tab_name in tab.text:
                tab.click()
        self.wait_for_page_render()

    def create_vm(self, name=None, dsc=None, image=None, root_size=None, cpu=1, mem='1 GB', data_size=None,
                  user_data=None, network=None, cluster=None, provisioning=u'厚置备', view='card'):
        image = image if image else os.getenv('imageName_s')
        network = network if network else os.getenv('l3PublicNetworkName')
        cluster = cluster if cluster else os.getenv('clusterName')
        self.vm_name = name if name else 'vm-' + get_time_postfix()
        self.vm_list.append(self.vm_name)
        test_util.test_logger('Create VM [%s]' % self.vm_name)
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
        test_util.test_logger('Create Volume [%s]' % self.volume_name)
        volume_dict = {'name': self.volume_name,
                       'description': dsc,
                       'dataSize': size.split(),
                       'clusterUuid': cluster,
                       'vmUuid' : vm,
                       'provisioning': provisioning}
        volume_elem = self._create(volume_dict, "volume", view=view)
        checker = MINICHECKER(self, volume_elem)
        if vm:
            check_list = [self.volume_name, vm, size]
            checker.volume_check(check_list)
        else:
            check_list = [self.volume_name, size]
            checker.volume_check(check_list=check_list, ops='detached')

    def create_network(self, name=None, dsc=None, vlan=None, physical_interface=None,
                       start_ip=None, end_ip=None, netmask=None, gateway=None, dhcp_server=None, dns=None, view='card'):
        self.network_name = name if name else 'network-' + get_time_postfix()
        self.netwok_list.append(self.network_name)
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
        if dhcp_server or dns:
            self.get_element('[style~=cursor]').click()
        else:
            network_dict.pop('dhcpServer')
            network_dict.pop('dns')
        network_elem = self._create(network_dict, "network", view=view)
        ip_num = int(start_ip.split('.')[-1]) - int(end_ip.split('.')[-1]) + 1
        check_list = [self.network_name, physical_interface, str(ip_num)]
        if vlan:
            check_list.append(vlan)
        else:
            check_list.append('-')
        checker = MINICHECKER(self, network_elem)
        checker.network_check(check_list)

    def add_image(self, name=None, dsc=None, adding_type='url', url=COMMONIMAGE, local_file=None, platform='Linux', view='card'):
        self.image_name = name if name else 'image-' + get_time_postfix()
        self.image_list.append(self.image_name)
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

    def vm_ops(self, vm_name, action='stop', details_page=False):
        vm_list = []
        if isinstance(vm_name, types.ListType):
            vm_list = vm_name
        else:
            vm_list.append(vm_name)
        for vm in vm_list:
            vm_elem = self.get_res_element(vm)
            vm_elem.get_element(CHECKBOX).click()
        if action == 'start':
            if details_page:
                self.more_operate(u'启动', vm_list, res_type='vm', details_page=True)
                self.click_ok()
            else:
                self.click_button(u'启动')
        elif action == 'reboot':
            self.more_operate(u'重启', vm_list, res_type='vm', details_page=details_page)
            self.click_ok()
        elif action == 'stop':
            if details_page:
                self.more_operate(u'停止', vm_list, res_type='vm', details_page=True)
                self.click_ok()
            else:
                self.click_button(u'停止')

    def delete_vm(self, vm_name=None, corner_btn=True, details_page=False):
        vm_name = vm_name if vm_name else self.vm_list
        self._delete(vm_name, 'vm', corner_btn=corner_btn, details_page=details_page)

    def expunge_vm(self, vm_name=None, details_page=False):
        vm_name = vm_name if vm_name else self.vm_list
        self._delete(vm_name, 'vm', expunge=True, details_page=details_page)

    def delete_volume(self, volume_name=None, corner_btn=True, details_page=False):
        volume_name = volume_name if volume_name else self.volume_list
        self._delete(volume_name, 'volume', corner_btn=corner_btn, details_page=details_page)

    def expunge_volume(self, volume_name=None, details_page=False):
        volume_name = volume_name if volume_name else self.volume_list
        self._delete(volume_name, 'volume', expunge=True, details_page=details_page)

    def delete_image(self, image_name=None, corner_btn=True, details_page=False):
        image_name = image_name if image_name else self.image_list
        self._delete(image_name, 'image', corner_btn=corner_btn, details_page=details_page)

    def expunge_image(self, image_name=None, details_page=False):
        image_name = image_name if image_name else self.image_list
        self._delete(image_name, 'image', expunge=True, details_page=details_page)

    def delete_network(self, network_name=None, corner_btn=True, details_page=False):
        network_name = network_name if network_name else self.network_list
        self._delete(network_name, 'network', corner_btn=corner_btn, details_page=details_page)

    def set_ha_level(self, vm_name, ha=True, details_page=False):
        test_util.test_logger('Set [%s] ha leval [%s]' % (vm_name, ha))
        check_list = []
        self.navigate('vm')
        self.more_operate(u'高可用级别', res_type='vm', res_name=vm_name, details_page=details_page)
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

    def update_info(self, res_type, res_name, new_name, new_dsc=None, corner_btn=False, details_page=False, view='card'):
        check_list = []
        self.navigate(res_type)
        self.switch_view(view)
        _elem = self.get_res_element(res_name)
        if corner_btn:
            _elem.get_elements('button', 'tag name')[0].click()
        else:
            self.more_operate(u'修改信息', res_name=res_name, res_type=res_type, details_page=True)
        if new_name is not None:
            test_util.test_logger('Update the name of [%s] to %s' % (res_name, new_name))
            self.input('name', new_name)
            check_list.append(new_name)
        if new_dsc is not None:
            test_util.test_logger('Update the dsc of [%s] to %s' % (res_name, new_dsc))
            self.input('description', new_dsc)
        self.click_ok()
        _elem = self.get_res_element(new_name)
        checker = MINICHECKER(self, _elem)
        if res_type == 'volume':
            checker.volume_check(check_list)
        elif res_type == 'vm':
            checker.vm_check(check_list)
        elif res_type == 'image':
            checker.image_check(check_list)
        else:
            pass

    def end_action(self, action_name):
        if action_name == 'confirm':
            self.click_ok()
        elif action_name == 'cancel':
            self.click_cancel()
        elif action_name == 'close':
            self.click_close()

    def add_dns_to_l3(self, network=None, dns='8.8.8.8', details_page=True, end_action='confirm'):
        test_util.test_logger('Add dns [%s] to l3 [%s]' % (dns, network))
        network = network if network else os.getenv('l3PublicNetworkName')
        self.navigate('network')
        self.more_operate(u'添加DNS', res_type='network', res_name=network, details_page=details_page)
        if dns in get_inv(network, 'network').dns:
            test_util.test_fail('fail: there has been a DNS[%s] on L3 network[%s]' % (dns, network))
        self.input('DNS',dns)
        self.end_action(end_action)

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
        check_list.append(ops_dict[ops])
        for v in check_list:
            if v not in self.elem.text:
                test_util.test_fail("Can not find %s in vm checker" % v)

    def volume_check(self, check_list=[], ops=None):
        if ops == 'detached':
            check_list.append(u'未加载')
        for v in check_list:
            if v not in self.elem.text:
                test_util.test_fail("Can not find %s in volume checker" % v)

    def image_check(self, check_list=[]):
        check_list.append(u'就绪')
        for v in check_list:
            if v not in self.elem.text:
                test_util.test_fail("Can not find %s in image checker" % v)

    def network_check(self, check_list=[]):
        for v in check_list:
            if v not in self.elem.text:
                test_util.test_fail("Can not find %s in network checker" % v)
