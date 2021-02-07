'''

New Integration Test for check default gateway ip conflict.

@author: xiaoshuang

update:jinling
The same deterministic gateway with the MAC of the backpack does not conflict
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import time
import os

def test():

    cmd = "ip a | grep 172 | awk '{print $NF}'"
    ethernet = os.popen(cmd).read()
    cmd = 'arping -I ' + ethernet.strip() + ' 172.24.0.1 -c 5'
    print cmd
    cmd = cmd + ' |gerp Unicast |cut -d" " -f5 >a.txt'
#gat the mac of first reply
    cmd1 = 'cat a.txt |head -n 1 |tail -n 1'
    a = os.popen(cmd1).read()
#gat the mac of second reply
    cmd2 = 'cat a.txt |head -n 2 |tail -n 1'
    b = os.popen(cmd2).read()
#gat the mac of third reply
    cmd3 = 'cat a.txt |head -n 3 |tail -n 1'
    c = os.popen(cmd3).read()

#    reply = os.popen(cmd).read()
#    test_util.test_logger('reply: %s' % reply)
# to be sure the three mac are the same
    if a == b and b == c :
        test_util.test_pass('Check gateway ip conflict Test Success')
    else:
        test_util.test_fail("gateway IP conflict check failed")
