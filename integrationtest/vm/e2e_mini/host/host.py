# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
from test_stub import *


class HOST(MINI):
    def __init__(self, uri=None, initialized=False):
        self.host_name = None
        self.host_list = []
        if initialized:
            # if initialized is True, uri should not be None
            self.uri = uri
            return
        super(HOST, self).__init__()

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
                    'light': u'识别灯亮'}
        test_util.test_logger('Host (%s) execute action[%s]' % (' '.join(host_list), action))
        for host in host_list:
            for elem in self.get_elements('ant-row-flex-middle'):
                if host in elem.text:
                    if not details_page:
                        if not elem.get_element(CHECKBOX).selected:
                            elem.get_element(CHECKBOX).click()
                    else:
                        elem.get_element('left-part').click()
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
