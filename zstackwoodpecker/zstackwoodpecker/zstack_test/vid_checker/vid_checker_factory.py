'''
Zstack IAM2 Virtual ID Checker Factory.


@author: Glody                   
'''

import zstackwoodpecker.zstack_test.vid_checker.zstack_vid_checker as vid_checker
import zstackwoodpecker.zstack_test.zstack_checker.zstack_db_checker as db_checker
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.test_util as test_util

class VidAttrCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj): 
        vid_attr_checker_chain = checker_header.CheckerChain()
        checker_dict = {}
        checker_dict[db_checker.zstack_vid_db_checker] = True
        checker_dict[vid_checker.zstack_vid_attr_checker] = True

        vid_attr_checker_chain.add_checker_dict(checker_dict, test_obj)
        test_util.test_logger('Add checker: %s for [user:] %s' % (vid_attr_checker_chain, test_obj.get_virtual_id_option().get_name()))
        return vid_attr_checker_chain

class VidPolicyCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        vid_policy_checker_chain = checker_header.CheckerChain()
        checker_dict = {}
        
        checker_dict[db_checker.zstack_vid_db_checker] = True
        checker_dict[vid_checker.zstack_vid_policy_checker] = True

        vid_policy_checker_chain.add_checker_dict(checker_dict, test_obj)
        test_util.test_logger('Add checker: %s for [user:] %s' % (vid_policy_checker_chain, test_obj.get_virtual_id_option().get_name()))
        return policy_checker_chain

