'''

Create an unified test_stub to share test operations

@author: fang.sun
'''

import zstackwoodpecker.operations.vpc_operations as vpc_ops
import zstackwoodpecker.operations.net_operations as net_ops
import os
import random
import zstackwoodpecker.test_util  as test_util
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.header.host as host_header
import apibinding.inventory as inventory
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstacklib.utils.xmlobject as xmlobject
import threading
import time
import sys
import telnetlib
import random
from contextlib import contextmanager
from functools import wraps
import itertools
#import traceback


def create_vpc_vrouter():

    vr_offering = res_ops.get_resource(res_ops.APPLIANCE_VM)[0]
    return vpc_ops.create_vpc_vrouter(name="test_vpc", virtualrouter_offering_uuid=vr_offering.uuid)


def attach_all_l3_to_vpc_vr(vpc_vr):
    conf = res_ops.gen_query_conditions("category", "=", "Private")
    conf = res_ops.gen_query_conditions("type", "=", "L3VpcNetwork", conf)
    l3_list = res_ops.query_resource(res_ops.L3_NETWORK, conf)
    for l3 in l3_list:
        net_ops.attach_l3(l3.uuid, vpc_vr.uuid)


