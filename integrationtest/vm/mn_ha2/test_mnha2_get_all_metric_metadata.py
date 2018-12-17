'''
Test Steps:
test all metric metadata
api is GetAllMetricMetadata
api is GetAllEventMetadata

@author: ye.tian   2018-12-17
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import apibinding.inventory as inventory
import time

test_stub = test_lib.lib_get_test_stub()

def test():
    # test GetAllMetricmetadata and GetAllEventMetadata
    all_metric_metadata = zwt_ops.get_all_metric_metadata()
    test_util.test_dsc('total account of metric metadata:%s' % len(all_metric_metadata))
    all_event_metadata = zwt_ops.get_all_event_metadata()
    test_util.test_dsc('total account of event metadata:%s' % len(all_event_metadata))

    test_util.test_pass('Get all metric metadata Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    pass
