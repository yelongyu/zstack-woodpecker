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
    reply = os.popen("nping --arp 172.20.0.1").read()
    if reply.count('RCVD') > 5:
        test_util.test_fail("gateway IP conflict check failed: %s" % (reply))
    test_util.test_pass('Check gateway ip conflict Test Success')
