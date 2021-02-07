# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import network

network_ops = None

def test():
    global network_ops
    network_ops = network.NETWORK()
    network_ops.create_network()
    network_ops.check_browser_console_log()
    test_util.test_pass('Create network Successful')

def env_recover():
    global network_ops
    network_ops.delete_network()
    network_ops.close()

def error_cleanup():
    global network_ops
    try:
        network_ops.delete_network()
        network_ops.close()
    except:
        pass
