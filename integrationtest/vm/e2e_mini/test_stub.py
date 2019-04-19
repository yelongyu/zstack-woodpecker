'''

Create an unified test_stub to share test operations

@author: Legion
'''

import os
from zstackwoodpecker.e2e import E2E
from zstackwoodpecker.thirdparty.selenium.webdriver.common.action_chains import ActionChains
from zstackwoodpecker import test_util


class MINI(E2E):
    def __init__(self):
        super(MINI, self).__init__()
        self.driver.get('http://172.20.0.201:8200')
        self.driver.set_window_size(1600, 900)
        self.login()

    def login(self):
        self.get_element('#accountName').send_keys('admin')
        self.get_element('#password').send_keys('password')
        self.click_button(u'µÇ Â¼')
        self.wait_for_element_appear(css='.ant-notification-notice-message')
        assert self.get_element('.ant-notification-notice-message').text == u'µÇÂ¼³É¹¦', 'The notification of successful login was not displayed! '
        elem = self.get_element('.active')
        if elem.text != u'Ê×Ò³':
            test_util.test_logger(elem.err_msg)
            test_util.test_fail('Login failed! %s')

    def click_button(self, btn_name):
        elements = self.get_elements('button', 'tag_name')
        for element in elements:
            if element in self.get_elements('button', 'tag_name'):
                if element.text == btn_name and element.is_displayed():
                    element.click()
                    break
            else:
                break
                self.click_button(self, btn_name)

    def select_option(self, placeholder, option):
        for element in self.get_elements('.ant-select-selection__placeholder'):
            if element.text == placeholder:
                element.click()
                break
        for element in self.get_elements('.ant-select-dropdown-menu-item'):
            if element.text == option:
                element.click()
                break

