# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None


def test():
    global mini
    # path1:details page
    mini = test_stub.MINI()
    mini.del_network_segment()
    mini.add_network_segment(details_page=True)
    # path2:checkbox list
    mini.del_network_segment()
    mini.add_network_segment(details_page=False)
    # path3:cancel
    mini.add_network_segment(details_page=True, end_action='cancel')
    mini.add_network_segment(details_page=False, end_action='cancel')
    # path4:exit
    mini.add_network_segment(details_page=True, end_action='close')
    mini.add_network_segment(details_page=False, end_action='close')
    mini.check_browser_console_log()
    test_util.test_pass('Add and Delete NetWork Segment')


def env_recover():
    global mini
    mini.close()


def error_cleanup():
    global mini
    try:
        mini.close()
    except:
        pass
