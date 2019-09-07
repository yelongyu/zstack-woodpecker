'''

Test VM Live Migration via Longjob, check migration progress while VM cpu/mem high load

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
    longjob.create_vm(l3_name=os.environ.get('l3PublicNetworkName'))

    longjob.add_stress()
    longjob.live_migrate_vm()
    # time.sleep(30)
    longjob.vm.check()

    longjob.check_data_integrity()
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
