# -*- coding:utf-8 -*-
'''

ZStack E2E test operations

@author: Legion
'''

import os
import re
import time
import types
import random
from os.path import join
from zstackwoodpecker.e2e_lib import E2E, StaleElementException
import zstackwoodpecker.operations.resource_operations as res_ops
from zstackwoodpecker import test_util
import zstacklib.utils.jsonobject as jsonobject


PRIMARYBTN = 'button primary'
PRODUCTSERVICE = 'product-service'
CONTENTCONTAINER = 'list-dialog-content'

separator = 'n/'

POSTFIX = time.strftime('%y%m%d-%H%M%S', time.localtime()) + '-' + str(random.random()).split('.')[-1]

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


class ZSTACK(E2E):
    def __init__(self):
        super(ZSTACK, self).__init__()
        self.vm_name = None
        self.volume_name = None
        self.image_name = None
        if os.getenv('ZSTACK_SIMULATOR'):
            self.zs_management_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
        else:
            self.zs_management_ip = os.getenv('ZSTACK_BUILT_IN_HTTP_SERVER_IP')
        self.url('http://%s:5000' % self.zs_management_ip)
        self.wait_for_element('#account-login-button')
        self.window_size(1600, 900)
        self.login()
        self.current_url = self.get_url()

    def input(self, elem_id, text):
        self.get_element(elem_id).get_element('input', 'tag name').input(text)

    def login(self, password='password'):
        test_util.test_logger('Log in normally')
        self.input('#account-name', 'admin')
        self.input('#account-password', password)
        self.get_element('#account-login-button').click()
        self.wait_for_element(PRODUCTSERVICE)
        assert self.get_element(PRODUCTSERVICE), 'Login Failed!'

    def logout(self):
        test_util.test_logger('Log out')
        self.get_element('span user').move_cursor_here()
        time.sleep(0.5)
        self.get_element('#common-logout').click()
        if not self.wait_for_element('#account-login-button'):
            test_util.test_fail('Fail to Logout')

    def more_ops(self, res_name, operaton):
        res_elements = self.get_elements('table-row')
        for elem in res_elements:
            if res_name in elem.text:
                elem.get_element('checkbox').click()
        self.get_element('#common-moreActions').click()
        time.sleep(0.5)
        test_util.test_logger('Operate Action [%s] on [%s]' % (operaton, res_name))
        self.get_elements('#common-%s' % operaton)[-1].click()
        time.sleep(0.5)
        self.get_element('#common-ok').click()

    def select_content(self, row_elem, name, value, click=True):
        cnt_selected = False
        if not row_elem.get_element('content').text:
            if click:
                row_elem.get_element('content').click()
            self.wait_for_element(CONTENTCONTAINER)
            for _ in xrange(20):
                if value in self.get_element(CONTENTCONTAINER).text:
                    break
                else:
                    time.sleep(0.5)
            else:
                test_util.test_fail('The content [%s] was not found!' % value)
            row_elems = self.get_element(CONTENTCONTAINER).get_elements('table-row')
            for elem in row_elems:
                try:
                    if value in elem.text:
                        cnt_selected = elem.click()
                except StaleElementException:
                    test_util.test_logger('DOM updated, get elements again')
                    self.select_content(row_elem=row_elem, name=name, value=value, click=False)
                if cnt_selected:
                    if name in ['network']:
                        test_util.test_logger('Click OK after selecting')
                        self.get_element('bottom-toolbar').get_element('#common-ok').click()
                    break


    def create(self, path, kw):
        test_util.test_logger('Create %s with %s' % (path, kw))
        target_url = self.current_url.split(separator)[0] + separator + path
        self.url(target_url)
        self.wait_for_element(PRIMARYBTN)
        self.get_element(PRIMARYBTN).click()
        for k, v in kw.iteritems():
            selector = '#common-' + k
            ops_row_elem = self.get_element(selector)
            text_elem = ops_row_elem.get_elements('input', 'tag name')
            if text_elem:
                text_elem[0].input(v)
            else:
                self.select_content(ops_row_elem, k, v)
        self.get_element('#common-ok').click()
        assert self.wait_for_element('toast success')
        self.wait_for_element('toast', target='disappear')
        assert kw['name'] in self.get_elements('table-row')[0].text

    def delete(self, path, name):
        target_url = self.current_url.split(separator)[0] + separator + path
        self.url(target_url)
        time.sleep(1)
        self.more_ops(name, 'destroy')
        assert self.wait_for_element('toast success')
        self.wait_for_element('toast', target='disappear')
        assert name not in self.get_element('page-table').text
