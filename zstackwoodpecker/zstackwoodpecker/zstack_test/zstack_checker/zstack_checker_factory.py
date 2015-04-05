'''
Zstack KVM Checker Factory.        


@author: YYK                   
'''

import zstackwoodpecker.zstack_test.zstack_checker.zstack_db_checker as db_checker
import zstackwoodpecker.zstack_test.zstack_checker.zstack_node_checker as node_checker
import zstackwoodpecker.zstack_test.zstack_test_node as zstack_test_node
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.test_util as test_util

class NodeCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj): 
        node_checker_chain = checker_header.CheckerChain()
        checker_dict = {}

        if test_obj.state == zstack_test_node.RUNNING:
            checker_dict[node_checker.NodeChecker] = True
        elif test_obj.state == zstack_test_node.STOPPED:
            checker_dict[node_checker.NodeChecker] = False

        node_checker_chain.add_checker_dict(checker_dict, test_obj)
        test_util.test_logger('Add checker: %s for [node:] %s' % (node_checker_chain, test_obj.get_node_option().get_name()))
        return node_checker_chain

