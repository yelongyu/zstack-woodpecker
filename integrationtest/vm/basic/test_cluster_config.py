'''

New Integration Test for change cluster memory CPU reservedMemory PS overProvisioning.

@author: pengtao.zhang
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops

_config_ = {
        'timeout' : 360,
        'noparallel' : False
        }

vm = None

def test():
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    print "cluster_uuid : %s" % cluster_uuid
    conf_ops.change_cluster_config('host', 'cpu.overProvisioning.ratio', '3', cluster_uuid)
    set_ps_value = conf_ops.get_cluster_config('host', 'cpu.overProvisioning.ratio', cluster_uuid)[0].value
    print "pengtao cpu.overProvisioning.ratio value : %s" % set_ps_value
    if set_ps_value == '3':
        test_util.test_logger('change cluster cpu.overProvisioning.ratio successfully')
    else:
        test_util.test_fail('change cluster cpu.overProvisioning.ratio failed')

    conf_ops.change_cluster_config('mevoco', 'overProvisioning.memory', '3', cluster_uuid)
    set_ps_value = conf_ops.get_cluster_config('mevoco', 'overProvisioning.memory', cluster_uuid)[0].value
    print "set_ps_value : %s" % set_ps_value
    if set_ps_value == '3':
        test_util.test_logger('change cluster overProvisioning.memory successfully')
    else:
        test_util.test_fail('change cluster overProvisioning.memory failed')

    conf_ops.change_cluster_config('kvm', 'reservedMemory', '3', cluster_uuid)
    set_ps_value = conf_ops.get_cluster_config('kvm', 'reservedMemory', cluster_uuid)[0].value
    print "set_ps_value : %s" % set_ps_value
    if set_ps_value == '3':
        test_util.test_logger('change cluster reservedMemory successfully')
    else:
        test_util.test_fail('change cluster reservedMemory failed')

    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    conf_ops.change_cluster_config('mevoco', 'overProvisioning.primaryStorage', '3', ps_uuid)

    set_ps_value = conf_ops.get_cluster_config('mevoco', 'overProvisioning.primaryStorage', ps_uuid)[0].value
    print "set_ps_value : %s" % set_ps_value
    if set_ps_value == '3':
        test_util.test_logger('change cluster ps overProvisioning successfully')
    else:
        test_util.test_fail('change cluster ps overProvisioning failed')

    conf_ops.change_cluster_config('host', 'cpu.overProvisioning.ratio', '5', cluster_uuid)
    set_ps_value = conf_ops.get_cluster_config('host', 'cpu.overProvisioning.ratio', cluster_uuid)[0].value
    print "pengtao cpu.overProvisioning.ratio value : %s" % set_ps_value
    if set_ps_value == '5':
        test_util.test_logger('change cluster cpu.overProvisioning.ratio successfully')
    else:
        test_util.test_fail('change cluster cpu.overProvisioning.ratio failed')

    conf_ops.change_cluster_config('mevoco', 'overProvisioning.memory', '5', cluster_uuid)
    set_ps_value = conf_ops.get_cluster_config('mevoco', 'overProvisioning.memory', cluster_uuid)[0].value
    print "set_ps_value : %s" % set_ps_value
    if set_ps_value == '5':
        test_util.test_logger('change cluster overProvisioning.memory successfully')
    else:
        test_util.test_fail('change cluster overProvisioning.memory failed')

    conf_ops.change_cluster_config('kvm', 'reservedMemory', '5', cluster_uuid)
    set_ps_value = conf_ops.get_cluster_config('kvm', 'reservedMemory', cluster_uuid)[0].value
    print "set_ps_value : %s" % set_ps_value
    if set_ps_value == '5':
        test_util.test_logger('change cluster reservedMemory successfully')
    else:
        test_util.test_fail('change cluster reservedMemory failed')

    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    conf_ops.change_cluster_config('mevoco', 'overProvisioning.primaryStorage', '5', ps_uuid)

    set_ps_value = conf_ops.get_cluster_config('mevoco', 'overProvisioning.primaryStorage', ps_uuid)[0].value
    print "set_ps_value : %s" % set_ps_value
    if set_ps_value == '5':
        test_util.test_logger('change cluster ps overProvisioning successfully')
    else:
        test_util.test_fail('change cluster ps overProvisioning failed')
    
    conf_ops.delete_cluster_config('mevoco', 'overProvisioning.primaryStorage', ps_uuid)
    conf_ops.delete_cluster_config('host', 'cpu.overProvisioning.ratio', cluster_uuid)
    conf_ops.delete_cluster_config('kvm', 'reservedMemory', cluster_uuid)
    conf_ops.delete_cluster_config('mevoco', 'overProvisioning.memory', cluster_uuid)
#Will be called only if exception happens in test().
def error_cleanup():
    pass
