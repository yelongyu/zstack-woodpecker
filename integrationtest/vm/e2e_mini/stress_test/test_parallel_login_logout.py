# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
from threading import Thread
import traceback

test_stub = test_lib.lib_get_test_stub()

mini_list = []
NUM = 10

class Login_logout(Thread):
    def __init__(self):
        super(Login_logout, self).__init__()
        self.exitcode = 0
        self.exception = None

    def run(self):
        try:
            self._run()
        except Exception as e:
            self.exitcode = 1
            self.exception = e
            test_util.test_logger(traceback.format_exc())

    def _run(self):
        mini = test_stub.MINI()
        mini_list.append(mini)
        mini.logout()
        mini.login()
        mini.check_browser_console_log()

    def join(self):
        Thread.join(self)
        if self.exitcode != 0:
            msg = "Thread '%s' threw an exception: %s" % (self.getName(), self.exception)
            raise Exception(msg)


def test():
    thread_list = []

    try:
        for _ in range(NUM):
            thread = Login_logout()
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()
    except Exception as e:
        test_util.test_logger(str(e))
        test_util.test_fail('Parallel Login Logout Failed')

    test_util.test_pass('Parallel Login Logout Successful')


def env_recover():
    global mini_list
    for mini in mini_list:
        mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini_list
    try:
        for mini in mini_list:
            mini.close()
    except:
        pass
