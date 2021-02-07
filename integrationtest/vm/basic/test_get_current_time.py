'''

Integration Test for get current time.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import time

def test():
    system_time1 = int(time.time())
    current_time = schd_ops.get_current_time().currentTime
    system_time2 = int(time.time())
    if system_time1 > current_time.Seconds and system_time2 < current_time.Seconds:
	    test_util.test_fail('get_current_time not get expected time[%s, %s]: %s' % (system_time1, system_time2, current_time.Seconds))
    test_util.test_pass('Create VM Test Success')

