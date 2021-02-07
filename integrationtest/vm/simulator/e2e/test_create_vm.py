# -*- coding:utf-8 -*-

import os
import time
import random
from collections import OrderedDict
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
POSTFIX = time.strftime('%y%m%d-%H%M%S', time.localtime()) + '-' + str(random.random()).split('.')[-1]
zs = None
vm_info = OrderedDict()
vm_info['name'] = 'vm-%s' % POSTFIX
vm_info['instanceOffering'] = os.getenv('instanceOfferingName_s')
vm_info['image'] = os.getenv('imageName_net')
vm_info['network'] = os.getenv('l3VlanNetworkName1')


def test():
    global zs
    zs = test_stub.ZSTACK()
    zs.create('vminstance', vm_info)
    zs.delete('vminstance', vm_info['name'])
    test_util.test_pass('Create VM Successful')


def env_recover():
    global zs
    zs.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global zs
    try:
        zs.delete('vminstance', vm_info['name'])
        zs.close()
    except:
        pass
