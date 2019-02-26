'''
Zstack checker header classes


@author: YYK                   
'''
import zstackwoodpecker.test_util as test_util
import time
class TestChecker(object):
    def __init__(self):
        import os
        self.exp_result = True
        self.real_result = None
        self.retry_count = 5
        self.test_obj = None
        self.start = None
        self.end = None
        retry_env = os.environ.get('WOODPECKER_TEST_FAILURE_RETRY')
        if retry_env and retry_evn.isdigit():
            self.retry_count = int(retry_env)

    def __repr__(self):
        return self.__class__.__name__

    def set_exp_result(self, exp_result):
        self.exp_result = exp_result

    def set_test_object(self, test_obj):
        self.test_obj = test_obj

    def set_retry_count(self, retry_count):
        self.retry_count = retry_count

    def check(self):
        '''
        The sub class check() function usually will call this super function. 
        And after the real checking, it should call self.judge(TEST_RESULT). 

        The inheritance class, should not add more params to this function.
        '''
        self.start = time.time()
        test_util.test_logger('Checker: [%s] begins.'% self.__class__.__name__)

    def judge(self, result):
        self.end = time.time()
        dlt = self.end - self.start

        self.real_result = result
        if self.exp_result == result:
            test_util.test_logger('\
                    Checker: [%s] PASS. Expected result: %s. Test result: %s. Spent: %.5f s.' \
                % (self.__class__.__name__, self.exp_result, self.real_result, dlt))

            return True

        else:
            if self.retry_count:
                test_util.test_logger('\
                        Checker: [%s] FAIL. Expected result: %s. Test result: %s. Spent: %.5f s. Try again. The left \
retry times: %s' % (self.__class__.__name__, self.exp_result, \
                        self.real_result, dlt, str(self.retry_count)))
                self.retry_count -= 1
                time.sleep(1)
                self.test_obj.update()
                self.check()
            else:
                test_util.test_fail('\
                        Checker: [%s] FAIL. Expected result: %s. Test result: %s. Spent: %.5f s. No Retry' \
                    % (self.__class__.__name__, \
                        self.exp_result, self.real_result, dlt))

class CheckerFactory(object):
    def create_checker(self):
        pass

class CheckerChain(object):
    def __init__(self):
        self.checker_chain = []

    def __repr__(self):
        class_str = 'CheckerChain:'

        for checker in self.checker_chain:
            class_str = '%s [%s]' % (class_str, checker.__class__.__name__)

        if not self.checker_chain:
            class_str = '%s None' % class_str

        return class_str

    def add_checker(self, checker, exp_result, test_obj):
        checker.set_test_object(test_obj)
        checker.set_exp_result(exp_result)
        self.checker_chain.append(checker)

    def add_checker_dict(self, checker_dict, test_obj):
        for key, value in checker_dict.iteritems():
            checker = key()
            checker.set_exp_result(value)
            checker.set_test_object(test_obj)
            self.checker_chain.append(checker)

    def remove_checker(self, checker):
        self.checker_chain.remove(checker)

    def check(self):
        if not self.checker_chain:
            test_util.test_warn('Not find any checker!')
            return

        for checker in self.checker_chain:
            checker.check()
