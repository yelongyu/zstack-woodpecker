# -*- coding:utf-8 -*-
'''

Create an unified test_stub for E2E test operations

@author: Legion
'''

import os
import re
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
ANTITEM = 'ant-dropdown-menu-item|ant-menu-item'
VMACTIONSCONTAINER = 'actionsContainer___1Ce9C'
INPUTROW = 'ant-row ant-form-item'
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
    first_mn_ip = item_list[0].getAttribute('ip')
    second_mn_ip = item_list[1].getAttribute('ip')
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
                'eip': res_ops.EIP,
                'backup': res_ops.VOLUME_BACKUP}
    conditions = res_ops.gen_query_conditions('name', '=', name)
    inv = res_ops.query_resource(res_dict[res_type], conditions)
    if inv:
        return inv[0]
    else:
        test_util.test_fail('Can not find the [%s] with name [%s]' % (res_type, name.encode('utf-8')))


class MINI(E2E):
    def __init__(self):
        super(MINI, self).__init__()
        if os.getenv('ZSTACK_SIMULATOR'):
            self.mini_server_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
        else:
            self.mini_server_ip = os.getenv('zstackHaVip')
        self.url('http://%s:8200' % self.mini_server_ip)
        self.window_size(1600, 900)
        self.login()

    def login(self, password='password'):
        test_util.test_logger('Log in normally')
        self.get_element('#account').input('admin')
        self.get_element('#password').input(password)
        self.click_ok()

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
        self.get_element('#account').input('admin')
        passwordInput = self.get_element('#password')
        assert passwordInput.get_attribute('type') == 'password'
        self.get_element('ant-input-suffix').click()
        passwordInput.input('password')
        assert passwordInput.get_attribute('type') == 'text'
        self.click_ok()

    def login_without_account_or_password(self, with_account=False, with_password=False):
        test_util.test_logger('Log in without account or password')
        if with_account:
            self.get_element('#account').input('admin')
        if with_password:
            self.get_element('#password').input('password')
        # Login button
        self.get_element('button', 'tag name').click()
        time.sleep(1)
        # check
        if not with_account or not with_password:
            self.wait_for_element(FORMEXPLAIN)
        if not with_account and with_password:
            assert self.get_element(FORMEXPLAIN).text == u'请输入账户名'
        elif with_account and not with_password:
            assert self.get_element(FORMEXPLAIN).text == u'请输入密码'
        elif not with_account and not with_password:
            assert self.get_elements(FORMEXPLAIN)[0].text == u'请输入账户名'
            assert self.get_elements(FORMEXPLAIN)[1].text == u'请输入密码'

    def login_with_wrong_account_or_password(self, wrong_account=True, wrong_password=True):
        test_util.test_logger('Log in with wrong account or password')
        if wrong_account:
            self.get_element('#account').input('wrongadmin')
        else:
            self.get_element('#account').input('admin')
        if wrong_password:
            self.get_element('#password').input('wrongpassword')
        else:
            self.get_element('#password').input('password')
        # Login button
        self.get_element('button', 'tag name').click()
        self.wait_for_element(FORMEXPLAIN)
        assert self.get_element(FORMEXPLAIN).text == u'账户名或密码错误'

    def navigate(self, menu):
        current_url = self.get_url()
        if menu not in current_url.split('/')[-1]:
            test_util.test_logger('Navigate to [%s]' % menu)
            self.get_element(MENUDICT[menu]).click()
            self.wait_for_element(PRIMARYBTN)
            time.sleep(2)
        if menu == "image":
            pattern = re.compile(u'(镜像仓库剩余容量)\s\d+\.?\d*\s(GB，总容量)\s\d+\.?\d*\s(GB)')
            if re.search(pattern, self.get_elements("ant-row-flex-space-between")[0].text) is None:
                test_util.test_fail("Err: page image is not fully loaded")

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

    def operate(self, name):
        test_util.test_logger('Execute operation [%s]' % name.encode('utf-8'))
        _elem = self.get_elements(VMACTIONSCONTAINER)
        for op in _elem[0].get_elements('span', 'tag name') if _elem else self.get_elements(ANTITEM):
            if op.enabled and op.text == name:
                op.click()
                time.sleep(1)
                return True

    def click_ok(self, assure_success=True):
        test_util.test_logger('Click OK button')
        self.wait_for_page_render()
        self.get_elements(PRIMARYBTN)[-1].click()
        if assure_success:
            if not self.wait_for_element(OPS_SUCCESS, timeout=300):
                test_util.test_fail("Fail: Operation Failed!")
        self.wait_for_element(MESSAGETOAST, timeout=300, target='disappear')
        time.sleep(1)

    def click_cancel(self):
        test_util.test_dsc('Click cancel button')
        self.get_elements(BTN)[-1].click()
        if not self.wait_for_element(MODALCONTENT, target='disappear'):
            test_util.test_fail("Fail to click cancel btn")

    def click_close(self):
        test_util.test_logger('Click close button')
        self.get_element(EXITBTN).click()
        if not self.wait_for_element(MODALCONTENT, target='disappear'):
            test_util.test_fail("Fail to click close btn")

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

    def create(self, para_dict, res_type, view, priority_dict=None):
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

    def delete(self, res_name, res_type, view, corner_btn=False, expunge=False, details_page=False, del_vol=False):
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

    def input(self, label, content):
        css_selector = 'label[for="%s"]' % label
        selection_rendered = 'ant-select-selection__rendered'
        radio_group = 'ant-radio-group'
        title = None

        def select_opt(elem, opt_value):
            elem.get_element(selection_rendered).click()
            time.sleep(1)
            for opt in self.get_elements('li[role="option"]'):
                if opt.displayed() and opt_value in opt.text:
                    opt.click()
                    return

        def select_radio(elem, value):
            for opt in self.get_elements('input[type="radio"]'):
                if value == opt.get_attribute('value'):
                    opt.click()

        def input_content(elem, content):
            element = elem.get_element('input', 'tag name')
            element.clear()
            element.input(content)

        def textarea_content(elem, content):
            element = elem.get_element('textarea', 'tag name')
            element.clear()
            element.input(content)

        for _ in range(10):
            elems = self.get_elements(INPUTROW)
            if elems:
                break
            else:
                time.sleep(0.5)
        else:
            test_util.test_fail('Can not find elements with selector: [%s]' % INPUTROW)
        for elem in self.get_elements(INPUTROW):
            title_elem = elem.get_elements(css_selector)
            if title_elem:
                title = title_elem[0].text.encode('utf-8')
                break
        if isinstance(content, types.IntType):
            content = str(content)
        if isinstance(content, types.ListType):
            if isinstance(content[0], types.IntType):
                content[0] = str(content[0])
            test_util.test_logger('Input [%s] for [%s]' % (content[0].encode('utf-8'), title))
            test_util.test_logger('Select [%s] for [%s]' % (content[1].encode('utf-8'), title))
            input_content(elem, content[0])
            select_opt(elem, content[1])
        else:
            if elem.get_elements(selection_rendered):
                test_util.test_logger('Select [%s] for [%s]' % (content.encode('utf-8'), title))
                select_opt(elem, content)
            elif elem.get_elements(radio_group):
                test_util.test_logger('Select [%s] for [%s]' % (content.encode('utf-8'), title))
                select_radio(elem, content)
            elif elem.get_elements('textarea[id="description"]'):
                test_util.test_logger('Input [%s] for [%s]' % (content.encode('utf-8'), title))
                textarea_content(elem, content)
            else:
                test_util.test_logger('Input [%s] for [%s]' % (content.encode('utf-8'), title))
                input_content(elem, content)

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
        _elem = self.get_elements(VMACTIONSCONTAINER)
        for op in _elem[0].get_elements('span', 'tag name') if _elem else self.get_elements(ANTITEM):
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

    def update_info(self, res_type, res_name, new_name, new_dsc=None, corner_btn=False, details_page=False, view='card'):
        if res_type == 'host' and corner_btn:
            test_util.test_fail('Host do not support to update info by corner btn.')
        if res_type == 'minihost' and not details_page:
            test_util.test_fail('Cluster only support to update info by details_page.')
        check_list = []
        if res_type == 'host':
            self.navigate('minihost')
        else:
            self.navigate(res_type)
        self.switch_view(view)
        if res_type == 'host':
            for elem in self.get_elements('ant-row-flex-middle'):
                if res_name in elem.text:
                    if not details_page:
                        elem.get_element(CHECKBOX).click()
                    else:
                        elem.get_element('left-part').click()
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

    def create_backup(self, name, res_type, backup_name, backup_dsc=None, end_action='confirm'):
        test_util.test_logger('%s[%s] create backup[%s]' % (res_type.upper(), name, backup_name))
        self.navigate(res_type)
        self.enter_details_page(res_type, name)
        self.switch_tab(u'备份数据')
        self.get_elements(MOREOPERATIONBTN)[-1].click()
        self.operate(u'创建备份')
        self.input('name', backup_name)
        if backup_dsc is not None:
            self.input('description', backup_dsc)
        self.end_action(end_action)
        if end_action == 'confirm':
            backup_list = []
            backup_list.append(backup_name)
            self.check_res_item(backup_list)

    def delete_backup(self, name, res_type, backup_name, end_action='confirm'):
        backup_list = []
        if isinstance(backup_name, types.ListType):
            backup_list = backup_name
        else:
            backup_list.append(backup_name)
        test_util.test_logger('%s[%s] delete backup (%s)' % (res_type.upper(), name, ' '.join(backup_list)))
        self.navigate(res_type)
        self.enter_details_page(res_type, name)
        self.switch_tab(u'备份数据')
        self.get_table_row(backup_list)
        self.get_elements(MOREOPERATIONBTN)[-1].click()
        self.operate(u'删除备份')
        self.end_action(end_action)
        if end_action == 'confirm':
            self.check_res_item(backup_list, target='notDisplayed')

    def restore_backup(self, name, res_type, backup_name, end_action='confirm'):
        test_util.test_logger('%s[%s] restore backup[%s]' % (res_type.upper(), name, backup_name))
        self.navigate(res_type)
        checker = MINICHECKER(self, self.get_res_element(name))
        if res_type == 'vm':
            checker.vm_check(ops='stop')
        self.enter_details_page(res_type, name)
        self.switch_tab(u'备份数据')
        backup_list = []
        backup_list.append(backup_name)
        self.get_table_row(backup_list)
        self.get_elements(MOREOPERATIONBTN)[-1].click()
        self.operate(u'恢复备份')
        self.end_action(end_action)
        image_name = 'for-recover-volume-from-backup-' + str(get_inv(backup_name, 'backup').uuid)
        image_list = []
        image_list.append(image_name)
        if res_type == 'vm':
            self.navigate('image')
            self.check_res_item(image_list)

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

    def check_about_page(self):
        test_util.test_logger('Check about page')
        self.get_element(MENUSETTING).move_cursor_here()
        self.operate(u'关于')
        mn_ip_list = []
        mn_ip_1, mn_ip_2 = get_mn_ip()
        mn_ip_list.append(mn_ip_1)
        mn_ip_list.append(mn_ip_2)
        ha_vip = os.getenv('zstackHaVip')
        assert ha_vip == self.get_elements("ipAddress___japHh")[0].text
        for elem in self.get_elements("ipAddress___japHh")[1:]:
            assert elem.text in mn_ip_list

    def check_config_page(self):
        test_util.test_logger('Check config page')
        self.get_element(MENUSETTING).move_cursor_here()
        self.operate(u'设置')
        self.get_elements(PRIMARYBTN)[-1].click()
        self.wait_for_element(MODALCONTENT)
        self.click_cancel()
        self.switch_tab(u"邮箱服务器")
        self.get_elements(PRIMARYBTN)[-1].click()
        self.wait_for_element(MODALCONTENT)
        # if don't wait 1s, will fail to click close btn
        time.sleep(1)
        self.click_close()

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
                test_util.test_fail("Can not find %s in host checker" % v.encode('utf-8'))
            test_util.test_logger("Find %s in host checker successful" % v.encode('utf-8'))

    def eip_check(self, check_list=[]):
        for v in check_list:
            if v not in self.elem.text:
                test_util.test_fail("Can not find %s in eip checker" % v.encode('utf-8'))
            test_util.test_logger("Find %s in eip checker successful" % v.encode('utf-8'))
