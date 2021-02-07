# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import eip

eip_ops = None

def test():
    global eip_ops
    eip_ops = eip.EIP()
    eip_ops.create_eip()
    eip_ops.check_browser_console_log()
    test_util.test_pass('Create EIP Successful')

def env_recover():
    global eip_ops
    eip_ops.delete_eip()
    eip_ops.close()

def error_cleanup():
    global eip_ops
    try:
        eip_ops.delete_eip()
        eip_ops.close()
    except:
        pass
