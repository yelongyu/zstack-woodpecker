'''

New Integration Test for check default gateway ip conflict.

@author: xiaoshuang
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import time
import os

def test():
    gateway_ip = os.environ.get('ipRangeGateway')
    #test_util.test_logger('gateway_ip:%s' % gateway_ip)


    cmd = "ip a | grep 172 | awk '{print $5}'"
    ethernet = os.popen(cmd).read()
    cmd = 'arping -I ' + ethernet.strip() + ' 172.20.0.1 -c 5'
    print cmd
    reply = os.popen(cmd).read()
    test_util.test_logger('reply: %s' % reply)

    if reply.count('Received 5 response(s)') == 1:
        test_util.test_pass('Check gateway ip conflict Test Success')
    else:
        test_util.test_fail("gateway IP conflict check failed: %s" % (reply))