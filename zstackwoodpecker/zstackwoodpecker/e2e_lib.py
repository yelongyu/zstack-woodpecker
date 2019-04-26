# -*- coding:utf-8 -*-
'''
Selenium wrapper

@author: Legion
'''

import os
import sys
import types
import traceback
from os.path import join
from zstackwoodpecker import test_util
from zstacklib.utils.http import json_post
import zstacklib.utils.jsonobject as jsonobject


class E2E(object):
    def __init__(self):
        with open('/home/upload_test_result/test_target', 'r') as f:
            target_browser = f.readline().strip()
        self.uri = 'http://%s:4444/wd/hub/session' % os.getenv('SELENIUM_SERVER')
        body = '{"desiredCapabilities":{"browserName":"%s"}}' % target_browser
        session = self._post(self.uri, body=body)
        self.session_id = jsonobject.loads(session).sessionId
        self.uri = join(self.uri, self.session_id)

    def route(self, url):
        self._post(join(self.uri, 'url'), body='{"url": "%s"}' % url)

    def _post(self, uri, body=None):
        return json_post(uri=uri, body=body, headers={'charset': 'utf-8'}, fail_soon=True)

    def _get(self, uri):
        return json_post(uri=uri, headers={'charset': 'utf-8'}, method='GET', fail_soon=True)

    def refresh_page(self):
        self._post(join(self.uri, 'refresh'))

    def _get_element(self, uri, value, strategy):
        if strategy == 'css selector' and '#' not in value:
            _value = value.split(' ')
            _value.insert(0, '')
            value = '.'.join(_value)
        _rsp = self._post(uri, body='{"using": "%s", "value":"%s"}' % (strategy, value))
        rsp = jsonobject.loads(_rsp)
        if rsp.status != 0:
            test_util.test_logger('Not found the element strategy [%s] with value [%s]' % (strategy, value))
        return (rsp, uri[:uri.index('element') + 7])

    def get_element(self, value, strategy='css selector'):
        '''
        strategy: 'css selector', 'tag name', 'id', 'link text', 'partial link text'
        reference: https://github.com/SeleniumHQ/selenium/wiki/JsonWireProtocol
        '''
        rsp, uri = self._get_element(join(self.uri, 'element'), value=value, strategy=strategy)
        if rsp.status != 0:
            test_util.test_logger(rsp.value.message)
        else:
            element = rsp.value.ELEMENT
            return Element(join(uri, element))

    def get_elements(self, value, strategy='css selector', check_element=True):
        rsp, uri = self._get_element(join(self.uri, 'elements'), value=value, strategy=strategy)
        uri = uri.replace('elements', 'element')
        elements = rsp.value
        element_list = []
        if elements:
            for elem in elements:
                element_list.append(Element(join(uri, elem.ELEMENT)))
        return element_list

    def click_button(self, btn_name, retry=3):
        elements = self.get_elements('button', 'tag_name')
        for element in elements:
            if element.text == btn_name and element.displayed():
                if element.click():
                    return True
                else:
                    retry -= 1
                    self.click_button(btn_name, retry)

    def input(self, item_name, content):
        for elem in self.get_elements('ant-row ant-form-item'):
            if item_name in elem.text:
                if elem.get_elements('input', 'tag name'):
                    elem.input(content)
                else:
                    elem.get_element('.ant-select-selection__rendered').click()
                    for opt in self.get_elements('li[role="option"]'):
                        if opt.text == content:
                            opt.click()


class Element(E2E):
    def __init__(self, uri):
        self.uri = uri

    @property
    def text(self):
        uri = join(self.uri, 'text')
        _rsp = self._get(uri)
        rsp = jsonobject.loads(_rsp.replace('null', '"null"'))
        if rsp.status != 0:
            print rsp.value.message
        else:
            return rsp.value

    def click(self):
        uri = join(self.uri, 'click')
        _rsp = self._post(uri)
        rsp = jsonobject.loads(_rsp.replace('null', '"null"'))
        if rsp.status != 0:
            print rsp.value.message
        else:
            return True

    def input(self, value):
        uri = join(self.uri, 'value')
        if isinstance(value, types.IntType):
            value = str(value)
        _value = [v for v in value]
        body='{"value": %s}' % _value
        _rsp = self._post(uri, body=body.replace("'", '"'))
        rsp = jsonobject.loads(_rsp.replace('null', '"null"'))
        if rsp.status != 0:
            print rsp.value.message
        else:
            return True

    def displayed(self):
        uri = join(self.uri, 'displayed')
        _rsp = self._get(uri)
        rsp = jsonobject.loads(_rsp)
        if rsp.status != 0:
            print rsp.value.message
        else:
            return rsp.value
