import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as config_ops
import zstackwoodpecker.test_util as test_util
test_stub = test_lib.lib_get_test_stub()

def test():
    #templete config 1
    template_uuid = config_ops.query_template_config(name='ping.interval')[0].templateUuid
    config_ops.update_template_config(name='ping.interval', value='3', category='host', template_uuid=template_uuid)

    ping_interval = config_ops.query_template_config(name='ping.interval')[0].value
    if ping_interval != 3:
        print ping_interval
        test_util.test_fail('Failed to update template config ping.interval value to 3.')

    config_ops.apply_template_config(template_uuid)
    ping_interval = config_ops.get_global_config(name='ping.interval', category='host')
    if ping_interval != 3:
        test_util.test_fail('Failed to apply template config ping.interval value to 3.')

    config_ops.reset_template_config(template_uuid)
    ping_interval = config_ops.query_template_config(name='ping.interval')[0].value
    if ping_interval == 3:
        test_util.test_fail('Failed to reset template config.')
    ping_interval = config_ops.get_global_config(name='ping.interval', category='host')
    if ping_interval != 3:
        test_util.test_fail('Global config ping.interval value changed when reset template config.') 

    #template config 2
    template_uuid = config_ops.query_template_config(name='vm.cpuMode')[0].templateUuid
    config_ops.update_template_config(name='vm.cpuMode', value='host-model', category='kvm', template_uuid=template_uuid)

    vm_cpuMode = config_ops.query_template_config(name='vm.cpuMode')[0].value
    if vm_cpuMode != 'host-mudel':
        test_util.test_fail('Failed to update template config vm.cpuMode value to host-model.')

    config_ops.apply_template_config(template_uuid)
    vm_cpuMode = config_ops.get_global_config(name='vm.cpuMode', category='host')
    if vm_cpuMode != 'host-model':
        test_util.test_fail('Failed to apply template config vm.cpuMode value to host-model.')

    config_ops.reset_template_config(template_uuid)
    vm_cpuMode = config_ops.query_template_config(name='vm.cpuMode')[0].value
    if vm_cpuMode == 'host-model':
        test_util.test_fail('Failed to reset template config.')
    vm_cpuMode = config_ops.get_global_config(name='vm.cpuMode', category='host')
    if vm_cpuMode != 'host-model':
        test_util.test_fail('Global config vm.cpuMode value changed when reset template config.')

    #template config 3
    template_uuid = config_ops.query_template_config(name='reservedMemory')[0].templateUuid
    config_ops.update_template_config(name='reservedMemory', value='2G', category='kvm', template_uuid=template_uuid)

    reserved_memory = config_ops.query_template_config(name='reservedMemory')[0].value
    if reserved_memory != '2G':
        test_util.test_fail('Failed to update template config reservedMemory value to 2G.')

    config_ops.apply_template_config(template_uuid)
    reserved_memory = config_ops.get_global_config(name='reservedMemory', category='host')
    if reserved_memory != '2G':
        test_util.test_fail('Failed to apply template config reservedMemory value to 2G.')

    config_ops.reset_template_config(template_uuid)
    reserved_memory = config_ops.query_template_config(name='reservedMemory')[0].value
    if reserved_memory == '2G':
        test_util.test_fail('Failed to reset template config.')
    reserved_memory = config_ops.get_global_config(name='reservedMemory', category='host')
    if reserved_memory != '2G':
        test_util.test_fail('Global config reservedMemory value changed when reset template config.')
