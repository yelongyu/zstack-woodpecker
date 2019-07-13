# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import network

network_ops = None


def test():
    global network_ops
    # path1:details page
    network_ops = network.NETWORK()
    network_ops.del_network_segment()
    network_ops.add_network_segment(details_page=True)
    # path2:checkbox list
    network_ops.del_network_segment()
    network_ops.add_network_segment(details_page=False)
    # path3:cancel
    network_ops.add_network_segment(details_page=True, end_action='cancel')
    network_ops.add_network_segment(details_page=False, end_action='cancel')
    # path4:exit
    network_ops.add_network_segment(details_page=True, end_action='close')
    network_ops.add_network_segment(details_page=False, end_action='close')
    network_ops.check_browser_console_log()
    test_util.test_pass('Add and Delete NetWork Segment')


def env_recover():
    global network_ops
    network_ops.close()


def error_cleanup():
    global network_ops
    try:
        network_ops.close()
    except:
        pass
