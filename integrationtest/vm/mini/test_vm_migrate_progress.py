'''

Test VM Live Migration via Longjob, check migration progress

@author: Legion
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops


test_stub = test_lib.lib_get_test_stub('virtualrouter')
longjob = test_stub.Longjob()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    longjob.create_vm()

    longjob.live_migrate_vm()
    test_util.test_pass('VM Live Migration with Progress Checking Test Success')

def env_recover():
    try:
        longjob.vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    try:
        longjob.vm.destroy()
    except:
        pass
