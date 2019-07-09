# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
from test_stub import *


class VM(MINI):
    def __init__(self, uri=None, initialized=False):
        self.vm_name = None
        self.vm_list = []
        if initialized:
            # if initialized is True, uri should not be None
            self.uri = uri
            return
        super(VM, self).__init__()

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
        vm_elem = self.create(vm_dict, 'vm', view=view, priority_dict=priority_dict)
        vm_inv = get_inv(self.vm_name, "vm")
        check_list = [self.vm_name, str(cpu), mem]
        if not isinstance(network, types.ListType):
            check_list.append(vm_inv.vmNics[0].ip)
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

    def delete_vm(self, vm_name=None, view='card', corner_btn=True, details_page=False, del_vol=False):
        vm_name = vm_name if vm_name else self.vm_list
        self.delete(vm_name, 'vm', view=view, corner_btn=corner_btn, details_page=details_page, del_vol=del_vol)

    def expunge_vm(self, vm_name=None, view='card', details_page=False):
        vm_name = vm_name if vm_name else self.vm_list
        self.delete(vm_name, 'vm', view=view, expunge=True, details_page=details_page)

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
        assert boot_order in self.get_element(INPUTROW).text
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
        while not self.get_elements('ant-dropdown'):
            self.get_elements(MOREOPERATIONBTN)[-1].click()
            time.sleep(0.5)
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
        while not self.get_elements('ant-dropdown'):
            self.get_elements(MOREOPERATIONBTN)[-1].click()
            time.sleep(0.5)
        self.operate(u'卸载')
        self.end_action(end_action)
        if end_action == 'confirm':
            self.check_res_item(volume_list, target='notDisplayed')
