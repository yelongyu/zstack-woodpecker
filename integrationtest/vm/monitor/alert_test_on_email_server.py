'''

Test about email sever

@author: Haochen

'''

import os
import test_stub
import random
import time
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.monitor_operations as mon_ops

def test():
    global media
    send_email = test_stub.create_email_media()
    media = send_email.uuid
    mail_list = test_stub.receive_email()
    keywords = "ZStack"
    mail_flag = test_stub.check_email(mail_list, keywords, trigger, host.uuid)
    if mail_flag == 0:
        test_util.test_fail('Failed to Get Target: %s for: %s Trigger Mail' % (host.uuid, test_item))
