'''
Multi node checker.
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.operations.node_operations as node_ops

class NodeChecker(checker_header.TestChecker):
    def __init__(self):
        super(NodeChecker, self).__init__()

    def check(self):
        super(NodeChecker, self).check()
        test_result = True
        test_node_option = self.test_obj.get_node_option()
        host_ip = test_node_option.get_management_ip()
        test_node = node_ops.get_management_node_by_host_ip(host_ip)
        if not test_node:
            test_result = False
            test_util.test_logger('Check result: Not find node on [host:] %s' % host_ip)
            return self.judge(test_result)

        test_node = test_node[0]
        test_util.test_logger('Check result: Find node on [host:] %s' % host_ip)

        if self.test_obj.node and self.test_obj.node.uuid == test_node.uuid:
            test_util.test_logger('node [id:] %s is sync with db' % test_node.uuid)
        else:
            test_result = False
            test_util.test_logger('Check result: Not find node on [host:] %s' % host_ip)
            return self.judge(test_result)

        if node_ops.is_management_node_ready(test_node.uuid):
            test_util.test_logger('node [id:] %s is ready' % test_node.uuid)
        else:
            test_result = False
            test_util.test_logger('Check result: [node:] %s is not ready' % test_node.uuid)
            return self.judge(test_result)

        test_util.test_logger('Check result: [node:] %s is ready on [host:] %s.' % (test_node.uuid, host_ip))
        return self.judge(test_result)

