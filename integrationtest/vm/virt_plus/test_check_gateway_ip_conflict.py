'''

New Integration Test for check default gateway ip conflict.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import time
import os

def test():
    gateway_ip = os.environ.get('ipRangeGateway')
    if os.popen("nping --arp 172.20.0.1 | grep RCVD | awk '{print $NF}' | sort | uniq | wc -l").read().strip() != "1":
        test_util.test_fail("gateway IP conflict check failed: %s" % (os.popen("nping --arp 172.20.0.1").read()))
    test_util.test_pass('Check gateway ip conflict Test Success')
