'''

New Integration Test for checking MN listening port.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import commands

def test():
    wrong_ip = '0.0.0.0'
    port_list = '5000|25672|8009|3306|7758|8080|4369|15672|10843|53405'
    ret_val, ret_out = commands.getstatusoutput("netstat -pant | awk '$4 ~ /^%s:/' | awk '$4 ~ /:(%s)$/'" % (wrong_ip, port_list))
    if ret_out:
	test_util.test_fail('Check MN listening port Fail')
    else:
        test_util.test_pass('Check MN listening port Success')

#Will be called only if exception happens in test().
def error_cleanup():
    pass
