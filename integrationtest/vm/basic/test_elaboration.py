'''

New Integration Test for error code elaboration

@author: Glody
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.operations.errorcode_operations as err_ops
import os

def check(results):
    filename_suffix_check = False
    regex_segment_check = False
    regex_exist_check = False
    errorcode_exist_check = False
    errorcode_dup_check = False
    categories_not_same_check = False
    for ret in results:
       if ret.reason == "file name must endWith '.json'":
           filename_suffix_check = True
       if ret.reason == "can not found regex for the segment":
           regex_segment_check = True
       if ret.reason == "regex already existed in zstack":
           regex_exist_check = True
       if ret.reason == "error code already existed in zstack":
           errorcode_exist_check = True
       if ret.reason == "error code duplicated at least twice":
           errorcode_dup_check = True
       if ret.reason == "not all categories are same in 1 input file":
           categories_not_same_check = True
    return [filename_suffix_check, regex_segment_check, regex_exist_check, \
	errorcode_exist_check, errorcode_dup_check, categories_not_same_check] 

def test():
    categories = err_ops.get_elaboration_categories()
    if categories == []:
        test_util.test_fail('Get elaboration categories failed')
    for category in ["Elaboration", "MN", "BS", "ACCOUNT", "VM", "HOST", "L2Network", "LICENSE"]:
        has_category = False
        for cg in categories:
            if cg.category == category:
                has_category = True
        if not has_category:
            test_util.test_fail('Category %s does not list in categories' %category)
    elaborations = err_ops.get_elaborations(category="ACCOUNT")
    if elaborations == []:
        test_util.test_fail('Get elaboration of [Category: %s] failed' %category)
    elaborations = err_ops.get_elaborations(regex="wrong account name or password")
    if elaborations == []:
        test_util.test_fail('Get elaboration of [Regex: %s] failed' %regex)

    missed_elaboration = err_ops.get_missed_elaboration()

    json_folder = "/tmp/elaboration/"
    json_file = "ACCOUNT"
    test_stub.construct_elaboration_json(os.path.join(json_folder, json_file))
    check_ret =  err_ops.check_elaboration_content(elaborate_file=os.path.join(json_folder, json_file))
    ret_lst = check(check_ret)
    for ret in ret_lst:
        if not ret:
            test_util.test_fail("Check elaboration content failed, [file: %s] "%os.path.join(json_folder, json_file)) 
    check_ret = err_ops.check_elaboration_content(elaborate_file=json_folder)
    ret_lst = check(check_ret)
    for ret in ret_lst:
        if not ret:
            test_util.test_fail("Check elaboration content failed, [folder: %s]"%json_folder)

    test_util.test_pass('Error Code Elaboration Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    pass
