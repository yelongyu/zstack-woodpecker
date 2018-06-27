'''

@author: YYK
'''

import os.path
import traceback
import sys
import imp
import zstackwoodpecker.test_util as test_util
import zstacklib.utils.debug as debug
import signal

cleanup_times = 0
TEST_CASE_CONFIG = '_config_'
TIME_OUT = 'timeout'
NO_PARALLEL = 'noparallel'

def get_case_config(test_case_path):
    sys.path.append(os.path.dirname(test_case_path))
        
    #Find an issue, if using same module name. When doing loop importing, if 
    # the latter test case don't have some attributes, while previous test case
    # has, the later test case loading module will have previous test case's 
    # attributes. So need assign an alone case module name for each case.
    module_name = os.path.basename(test_case_path)[:-3]
    module_name = '%s_%s' % (os.path.basename(os.path.dirname(test_case_path)), module_name)
    test_case = imp.load_source(module_name, test_case_path)
    if hasattr(test_case, TEST_CASE_CONFIG):
        return test_case._config_

def get_case_doc(test_case_path):
    module_name = os.path.basename(test_case_path)[:-3]
    module_name = '%s_%s' % (os.path.basename(os.path.dirname(test_case_path)), module_name)
    test_case = imp.load_source(module_name, test_case_path)
    return test_case.__doc___

def main(argv):
    def sigint_handler(signum, frame):
        print 'receive ctrl-c signal, will stop current test case running, and call cleanup function.'
        cleanup(test_case)
        sys.exit(1)

    if len(argv) == 0:
        raise Exception('No Test Case Path was provided to execute. The right command is: #testcase.py test_case_path')

    test_case_path = argv[0]
    sys.path.append(os.path.dirname(test_case_path))
    test_case = imp.load_source('test_case', test_case_path)
    case_setup_path = os.path.dirname(test_case_path)+'/case_setup.py'
    case_setup = None
    if os.path.exists(case_setup_path):
        case_setup = imp.load_source('case_setup', case_setup_path)
    if case_setup == None:
        case_setup_path = os.path.dirname(os.path.dirname(test_case_path))+'/case_setup.py'
        if os.path.exists(case_setup_path):
            case_setup = imp.load_source('case_setup', case_setup_path)

    if not hasattr(test_case, 'test'):
        raise Exception('Not able to execute test case: %s, test case should at least define an entry function test()' % test_case_path)

    signal.signal(signal.SIGTERM, sigint_handler)
    try:
        if case_setup and 'suite_setup' not in test_case_path:
            try:
                case_setup.test()
            except:
                traceback.print_exc(file=sys.stdout)
                test_util.test_env_not_ready("Env not ready")
        ret = test_case.test()
        if ret == True or ret == None:
            sys.exit(0)
        else:
            cleanup(test_case)
    except Exception as e:
        if os.environ.get('WOODPECKER_START_DEBUGGER'):
            import rpdb
            rpdb.set_trace()
        traceback.print_exc(file=sys.stdout)
        cleanup(test_case)
    finally:
        recover(test_case)

def cleanup(test_case):
    global cleanup_times
    if cleanup_times != 0:
        return
    cleanup_times += 1

    test_util.test_dsc('^^^^^^^^^^^^^ Test Case Failure or Exception Point ^^^^^^^^^^^^^^^')
    print '-'*40
    #if not hasattr(test_case, 'error_cleanup') or os.environ.get('ZSTACK_WOODPECKER_NO_ERROR_CLEANUP'):
    if not hasattr(test_case, 'error_cleanup'):
        print "error_cleanup 1"
    if os.environ.get('WOODPECKER_NO_ERROR_CLEANUP'):
        print os.environ.get('WOODPECKER_NO_ERROR_CLEANUP')
        print "error_cleanup 2"
        print('Test case error cleanup function error_cleanup() is not defined or "--no-cleanup" ("-n") is set. Exception cleanup function will not be called.')
        raise Exception('Test Case Failed. Please look for "exception" happened early.')
    else:
        test_util.test_dsc('-------------Test Error Cleanup Function------------------')
        try:
            test_case.error_cleanup()
        except:
            print('Just for your information, there is an exception when calling test case error cleanup function. It might cause some test resource (e.g. VMs) are not cleanup successfully. The real test case Exception was happened before this one. Please look for the line: marked with "Test Case Failure or Exception Point" ')
            traceback.print_exc(file=sys.stdout)
        finally:
            raise Exception('Test Case Failed. Please look for exception happened early.')

def recover(test_case):
    test_util.test_dsc('Test Case Env Recover')
    print '-'*40
    if not hasattr(test_case, 'env_recover'):
        print "env_recover 1"
    test_util.test_dsc('-------------Test Env Recover Function------------------')
    try:
        test_case.env_recover()
    except:
        print('Just for your information, there is an exception when calling test case env recover function.')
        traceback.print_exc(file=sys.stdout)

if __name__ == '__main__':
    debug.install_runtime_tracedumper()
    main(sys.argv[1:])
