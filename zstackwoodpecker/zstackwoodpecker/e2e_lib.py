# -*- coding:utf-8 -*-
'''
Selenium wrapper

@author: Legion
'''

import os
import sys
import re
import time
import types
import traceback
from os.path import join
from zstackwoodpecker import test_util
from zstacklib.utils.http import json_post
import zstacklib.utils.jsonobject as jsonobject

HEADERS = {'charset': 'utf-8'}


def jsonify_rsp(rsp):
    return jsonobject.loads(rsp.replace('null', '"null"'))


class E2E(object):
    def __init__(self):
        with open('/home/upload_test_result/test_target', 'r') as f:
            target_browser = f.readline().strip()
        self.uri = 'http://%s:4444/wd/hub/session' % os.getenv('SELENIUM_SERVER')
        body = '{"desiredCapabilities":{"browserName":"%s"}}' % target_browser
        session = self._post(self.uri, body=body)
        self.session_id = session.sessionId
        self.uri = join(self.uri, self.session_id)

    def url(self, url):
        rsp = self._post(join(self.uri, 'url'), body='{"url": "%s"}' % url)
        if rsp.status == 0:
            return True

    def get_url(self):
        rsp = self._get(join(self.uri, 'url'))
        return rsp.value

    def _post(self, uri, body=None):
        _rsp = json_post(uri=uri, body=body, headers=HEADERS, fail_soon=True)
        rsp = jsonify_rsp(_rsp)
        if rsp.status != 0:
            test_util.test_fail('URL request failed! uri: %s, body: %s, reason: %s' % (uri, body, rsp.value.message))
        else:
            return rsp

    def _get(self, uri):
        _rsp = json_post(uri=uri, headers=HEADERS, method='GET', fail_soon=True)
        rsp = jsonify_rsp(_rsp)
        if rsp.status != 0:
            test_util.test_fail('URL request failed! uri: %s, reason: %s' % (uri, rsp.value.message))
        else:
            return rsp

    def _del(self, uri):
        return json_post(uri=uri, headers=HEADERS, method='DELETE', fail_soon=True)

    def go_forward(self):
        self._post(join(self.uri, 'forward'))

    def go_backward(self):
        self._post(join(self.uri, 'back'))

    def refresh_page(self):
        self._post(join(self.uri, 'refresh'))

    def get_page_title(self):
        rsp = self._get(join(self.uri, 'title'))
        return rsp.value

    def get_source(self):
        rsp = self._get(join(self.uri, 'source'))
        return rsp.value

    def _get_element(self, uri, value, strategy):
        if strategy == 'css selector' and len(re.split('[#=]', value)) == 1:
            _value = value.split(' ')
            _value.insert(0, '')
            value = '.'.join(_value)
        if '=' in value:
            value = value.replace('"', '\\"')
        rsp = self._post(uri, body='{"using": "%s", "value":"%s"}' % (strategy, value))
        return (rsp, uri[:uri.index('element') + 7])

    def get_element(self, value, strategy='css selector'):
        '''
        strategy: 'css selector', 'tag name', 'id', 'link text', 'partial link text'
        reference: https://github.com/SeleniumHQ/selenium/wiki/JsonWireProtocol
        '''
        rsp, uri = self._get_element(join(self.uri, 'element'), value=value, strategy=strategy)
        element = rsp.value.ELEMENT
        return Element(join(uri, element))

    def get_elements(self, value, strategy='css selector', check_result=False):
        val_list = value.split('|')
        rsp, uri = self._get_element(join(self.uri, 'elements'), value=val_list[0], strategy=strategy)
        if len(val_list) > 1 and not rsp.value:
            rsp, uri = self._get_element(join(self.uri, 'elements'), value=val_list[1], strategy=strategy)
        element_list = []
        uri = uri.replace('elements', 'element')
        elements = rsp.value
        if elements:
            for elem in elements:
                element_list.append(Element(join(uri, elem.ELEMENT)))
        elif check_result:
            test_util.test_fail('Can not find the elements [strategy="%s", value="%s"]' % (strategy, value))
        return element_list

    def wait_for_element(self, value, strategy='css selector', timeout=10, target='appear'):
        if target == 'appear':
            criteria = 'self.get_elements(value, strategy)'
        else:
            criteria = 'not self.get_elements(value, strategy)'
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if eval(criteria):
                break
            else:
                time.sleep(0.5)
        else:
            test_util.test_logger('The element[strategy: "%s", value: "%s"] was not displayed within [%s]s' % (strategy, value, timeout))

    def click_button(self, btn_name):
        elements = self.get_elements('button', 'tag name', check_result=True)
        for element in elements:
            if element.text == btn_name and element.displayed():
                if element.click():
                    time.sleep(1)
                    return True

    def input(self, label, content):
        css_selector = 'label[for="%s"]' % label
        selection_rendered = 'ant-select-selection__rendered'
        def select_opt(elem, opt_value):
            elem.get_element(selection_rendered).click()
            for opt in self.get_elements('li[role="option"]'):
                if opt.displayed() and opt_value in opt.text:
                    opt.click()
        def input_content(elem, content):
            element = elem.get_element('input', 'tag name')
            element.clear()
            element.input(content)
        def textarea_content(elem, content):
            element = elem.get_element('textarea', 'tag name')
            element.clear()
            element.input(content)
        title = None
        for elem in self.get_elements('ant-row ant-form-item'):
            title_elem = elem.get_elements(css_selector)
            if title_elem:
                title = title_elem[0].text.encode('utf-8')
                break
        if isinstance(content, types.ListType):
            input_content(elem, content[0])
            select_opt(elem, content[1])
        else:
            if elem.get_elements(selection_rendered):
                select_opt(elem, content)
            elif elem.get_elements('textarea[id="description"]'):
                test_util.test_dsc('input [%s] for [%s]' % (content, title))
                textarea_content(elem, content)
            else:
                test_util.test_dsc('input [%s] for [%s]' % (content, title))
                input_content(elem, content)

    @property
    def window_handle(self):
        uri = join(self.uri, 'window_handles')
        window_handles = self._get(uri).value
        return window_handles[0]

    def window_size(self, width, height):
        uri = join(self.uri, 'window', self.window_handle, 'size')
        self._post(uri, body='{"width": %s , "height": %s}' % (int(width), int(height)))

    def implicit_wait(self, sec=10):
        sec = int(sec) * 1000
        uri = join(self.uri, 'timeouts', 'implicit_wait')
        self._post(uri, body='{"ms": %s}' % sec)
        
    def maximize_window(self):
        uri = join(self.uri, 'window', self.window_handle, 'maximize')
        self._post(uri)

    def close_window(self):
        uri = join(self.uri, 'window')
        self._del(uri)

    # Delete the session.
    def close(self):
        self._del(self.uri)

    def operate(self, name):
        op_selector = 'ant-dropdown-menu-item|ant-menu-item'
        self.wait_for_element(op_selector)
        for op in self.get_elements(op_selector):
            if op.enabled and op.text == name:
                op.click()
                return True

class Element(E2E):
    def __init__(self, uri):
        self.uri = uri

    # Returns the visible text for the element.
    @property
    def text(self):
        uri = join(self.uri, 'text')
        rsp = self._get(uri)
        return rsp.value

    # Get the value of an element's attribute.
    @property
    def name(self):
        uri = join(self.uri, 'name')
        rsp = self._get(uri)
        return rsp.value

    @property
    def selected(self):
        '''
        Determine if an OPTION element, or an INPUT element 
        of type checkbox or radiobutton is currently selected.
        '''
        uri = join(self.uri, 'selected')
        rsp = self._get(uri)
        return rsp.value 

    @property
    def enabled(self):
        uri = join(self.uri, 'enabled')
        rsp = self._get(uri)
        return rsp.value

    @property
    def location(self):
        uri = join(self.uri, 'location')
        rsp = self._get(uri).value
        loc = {
            "x": round(rsp['x']),
            "y": round(rsp['y'])
        }
        return loc   

    def clear(self):
        uri = join(self.uri, 'clear')
        self._post(uri)
        return True

    def get_attribute(self, name):
        uri = join(self.uri, 'attribute', name)
        rsp = self._get(uri)
        return rsp.value

    def click(self):
        uri = join(self.uri, 'click')
        rsp = self._post(uri)
        if rsp.status == 0:
            time.sleep(1)
            return True

    def input(self, value):
        uri = join(self.uri, 'value')
        if isinstance(value, types.IntType):
            value = str(value)
        _value = [v for v in value]
        body='{"value": %s}' % _value
        self._post(uri, body=body.replace("'", '"'))
        return True

    def displayed(self):
        uri = join(self.uri, 'displayed')
        rsp = self._get(uri)
        return rsp.value
