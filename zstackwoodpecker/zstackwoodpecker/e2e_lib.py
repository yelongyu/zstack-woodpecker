# -*- coding:utf-8 -*-
'''
Selenium wrapper

@author: Legion
'''

import os
import re
import time
import types
import base64
import traceback
from os.path import join
from zstackwoodpecker import test_util
from zstacklib.utils.http import json_post
import zstacklib.utils.jsonobject as jsonobject

HEADERS = {'charset': 'utf-8'}

def jsonify_rsp(rsp):
    return jsonobject.loads(rsp.replace('null', '"null"'))

class StaleElementException(Exception):
    pass


class E2E(object):
    def __init__(self):
        with open('/home/upload_test_result/test_target', 'r') as f:
            test_browser = f.readline().strip()
        test_browser = test_browser if test_browser in ['chrome', 'firefox'] else 'chrome'
        with open('/home/mn_node_ip', 'r') as nip_file:
            selenium_server = nip_file.read()
        self.uri = 'http://%s:4444/wd/hub/session' % selenium_server
#         self.uri = 'http://%s:4444/wd/hub/session' % os.getenv('SELENIUM_SERVER')
        body = '{"desiredCapabilities":{"browserName":"%s"}}' % test_browser
        session = self._post(self.uri, body=body)
        self.session_id = session.sessionId
        self.uri = join(self.uri, self.session_id)

    def url(self, url):
        test_util.test_logger('Navigate to %s' % url)
        rsp = self._post(join(self.uri, 'url'), body='{"url": "%s"}' % url)
        if rsp.status == 0:
            return True
        else:
            test_util.test_fail('Failed to open url "%s"' % url)

    def get_url(self):
        rsp = self._get(join(self.uri, 'url'))
        return rsp.value

    def get_active_element(self):
        rsp = self._post(join(self.uri, 'element', 'active'))
        elem_id = rsp.value
        return Element(join(self.uri, 'element', elem_id))

    def get_console_log(self):
        uri = join(self.uri, 'log')
        rsp = self._post(uri, body='{"type":"browser"}')
        return rsp.value

    def _post(self, uri, body=None, exp_if_stale=False):
        _rsp = json_post(uri=uri, body=body, headers=HEADERS, fail_soon=True)
        rsp = jsonify_rsp(_rsp)
        if rsp.status != 0:
            test_util.test_logger('URL request encountered error {uri: "%s", body: %s, reason: %s}' % (uri, body, rsp.value.message))
            if exp_if_stale:
                raise StaleElementException
        return rsp

    def _get(self, uri):
        _rsp = json_post(uri=uri, headers=HEADERS, method='GET', fail_soon=True)
        rsp = jsonify_rsp(_rsp)
        if rsp.status != 0:
            test_util.test_logger('URL request encountered error {uri: %s, reason: %s}' % (uri, rsp.value.message))
        return rsp

    def _del(self, uri):
        return json_post(uri=uri, headers=HEADERS, method='DELETE', fail_soon=True)

    def get_screenshot(self):
        rsp = self._get(join(self.uri, 'screenshot'))
        return rsp.value

    def save_screenshot(self):
        data = self.get_screenshot().encode('ascii')
        png_file = '.'.join([os.getenv('CASELOGPATH')[:-4], ''.join(str(time.time()).split('.')), 'png'])
        png = base64.b64decode(data)
        with open(png_file, 'wb') as pf:
            pf.write(png)

    def go_forward(self):
        self._post(join(self.uri, 'forward'))

    def go_backward(self):
        self._post(join(self.uri, 'back'))

    def refresh_page(self):
        test_util.test_logger('Refresh page')
        rsp = self._post(join(self.uri, 'refresh'))
        if rsp.status == 0:
            return True

    def get_page_title(self):
        rsp = self._get(join(self.uri, 'title'))
        return rsp.value

    def get_source(self):
        rsp = self._get(join(self.uri, 'source'))
        return rsp.value

    def _get_element(self, uri, value, strategy, exp_if_stale=False):
        if strategy == 'css selector' and len(re.split('[#=]', value)) == 1:
            _value = value.split(' ')
            _value.insert(0, '')
            value = '.'.join(_value)
        if '=' in value:
            value = value.replace('"', '\\"')
        rsp = self._post(uri, body='{"using": "%s", "value":"%s"}' % (strategy, value), exp_if_stale=exp_if_stale)
        return (rsp, uri[:uri.index('element') + 7])

    def get_element(self, value, strategy='css selector', par_uri=None, check_result=False, exp_if_stale=False):
        '''
        strategy: 'css selector', 'tag name', 'id', 'link text', 'partial link text'
        reference: https://github.com/SeleniumHQ/selenium/wiki/JsonWireProtocol
        If result is empty, return error with error code no such element. Otherwise, return the first element of result.
        DO NOT use this method to check if an element exist.
        '''
        par_uri = par_uri if par_uri else self.uri
        val_list = value.split('|')
        for i in xrange(len(val_list)):
            rsp, uri = self._get_element(join(par_uri, 'element'), value=val_list[i], strategy=strategy, exp_if_stale=exp_if_stale)
            if rsp.value is not None:
                break
        element = rsp.value.ELEMENT
        if element is None:
            if check_result:
                test_util.test_fail('Can not find the element [strategy="%s", value="%s"]' % (strategy, value))
            else:
                return None
        return Element(join(uri, element), par_uri, strategy, val_list[i])

    def get_elements(self, value, strategy='css selector', par_uri=None, check_result=False):
        '''
        If result is empty, return empty list
        USE this method to check if an element exist.
        '''
        par_uri = par_uri if par_uri else self.uri
        val_list = value.split('|')
        for i in xrange(len(val_list)):
            rsp, uri = self._get_element(join(self.uri, 'elements'), value=val_list[i], strategy=strategy)
            if rsp.value:
                break
        element_list = []
        uri = uri.replace('elements', 'element')
        elements = rsp.value
        if elements:
            for elem in elements:
                element_list.append(Element(join(uri, elem.ELEMENT), par_uri, strategy, value))
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
            test_util.test_logger('The element[strategy: "%s", value: "%s"] is not %s within [%s]s' % (strategy, value, target, timeout))
            return False
        test_util.test_logger('The element[strategy: "%s", value: "%s"] is %s' % (strategy, value, target))
        return True

    def click_button(self, btn_name):
        elements = self.get_elements('button', 'tag name', check_result=True)
        for element in elements:
            if element.text == btn_name and element.displayed():
                if element.click():
                    time.sleep(1)
                    return True

    @property
    def window_handle(self):
        uri = join(self.uri, 'window_handles')
        window_handles = self._get(uri).value
        return window_handles[0]

    def get_window_handles(self):
        uri = join(self.uri, 'window_handles')
        window_handles = self._get(uri).value
        return window_handles

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

    def change_window(self, handle):
        uri = join(self.uri, 'window')
        self._post(uri, body='{"name": "%s"}' % handle)

    def close_window(self):
        uri = join(self.uri, 'window')
        self._del(uri)

    # Delete the session.
    def close(self):
        self._del(self.uri)

    def input(self):
        pass

    def operate(self):
        pass

    def execute_script(self, script):
        test_util.test_logger('Execute the script[%s]' % script)
        uri = join(self.uri, 'execute')
        self._post(uri, body='{"script": "%s", "args": %s}' % (script, list("")))


class Element(E2E):
    def __init__(self, uri, par_uri=None, par_strategy=None, par_value=None):
        self.uri = uri
        self.par_uri = par_uri
        self.par_strategy = par_strategy
        self.par_value = par_value

    # Returns the visible text for the element.
    @property
    def text(self):
        uri = join(self.uri, 'text')
        rsp = self._get(uri)
        if rsp.status == 10:
            self.refresh_uri()
            return self.text
        else:
            return rsp.value

    # Get the value of an element's attribute.
    @property
    def name(self):
        uri = join(self.uri, 'name')
        rsp = self._get(uri)
        if rsp.status == 10:
            self.refresh_uri()
            return self.name
        else:
            return rsp.value

    @property
    def selected(self):
        '''
        Determine if an OPTION element, or an INPUT element
        of type checkbox or radiobutton is currently selected.
        '''
        uri = join(self.uri, 'selected')
        rsp = self._get(uri)
        if rsp.status == 10:
            self.refresh_uri()
            return self.selected
        else:
            return rsp.value

    @property
    def enabled(self):
        uri = join(self.uri, 'enabled')
        rsp = self._get(uri)
        if rsp.status == 10:
            self.refresh_uri()
            return self.enabled
        else:
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

    def refresh_uri(self):
        new_elem = self.get_element(self.par_value, self.par_strategy, self.par_uri, exp_if_stale=True)
        self.uri = new_elem.uri

    def move_cursor_here(self):
        uri = join(self.uri.split('element')[0], 'moveto')
        rsp = self._post(uri, body='{"element": "%s"}' % self.uri.split('/')[-1])
        time.sleep(0.5)
        if rsp.status == 10:
            self.refresh_uri()
            return self.move_cursor_here()
        else:
            return True

    def clear(self):
        uri = join(self.uri, 'clear')
        rsp = self._post(uri)
        if rsp.status == 10:
            self.refresh_uri()
            return self.clear()
        else:
            return True

    def get_attribute(self, name):
        uri = join(self.uri, 'attribute', name)
        rsp = self._get(uri)
        if rsp.status == 10:
            self.refresh_uri()
            return self.get_attribute(name)
        else:
            return rsp.value

    def click(self):
        uri = join(self.uri, 'click')
        rsp = self._post(uri)
        if rsp.status == 10:
            self.refresh_uri()
            return self.click()
        else:
            return True

    def input(self, value):
        uri = join(self.uri, 'value')
        if isinstance(value, types.IntType):
            value = str(value)
        # _value = [v.encode('utf-8') for v in value]
        # body='{"value": %s}' % _value
        body='{"value": ['
        for val in value:
            body += '"%s"' % val.encode('utf-8') + ','
        body = body[:-1] + ']}'
        rsp = self._post(uri, body=body.replace("'", '"'))
        if rsp.status == 10:
            self.refresh_uri()
            return self.input(value)
        else:
            return True

    def submit(self):
        uri = join(self.uri, 'submit')
        rsp = self._post(uri)
        if rsp.status == 10:
            self.refresh_uri()
            return self.submit()
        else:
            return rsp.value

    def displayed(self):
        uri = join(self.uri, 'displayed')
        rsp = self._get(uri)
        if rsp.status == 10:
            self.refresh_uri()
            return self.displayed()
        else:
            return rsp.value
