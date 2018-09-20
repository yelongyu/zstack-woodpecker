'''
check the global_config category is host
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global default_host_ping_parallelismDegree
    global default_host_update_os_parallelismDegree 
    global default_host_ping_timeout
    global default_host_load_parallelismDegree 
    global default_host_ping_maxFailure
    global default_host_load_all
    global default_host_connection_autoReconnectOnError
    global default_host_ping_sleepPeriodAfterFailure
    global default_host_cpu_overProvisioning_ratio
    global default_host_maintenanceMode_ignoreError
    global default_host_reconnectAllOnBoot
    global default_host_ping_interval

    #get the default value
    default_host_ping_parallelismDegree = conf_ops.get_global_config_default_value('host', 'ping.parallelismDegree')
    default_host_update_os_parallelismDegree = conf_ops.get_global_config_default_value('host', 'update.os.parallelismDegree')
    default_host_ping_timeout = conf_ops.get_global_config_default_value('host', 'ping.timeout')
    default_host_load_parallelismDegree = conf_ops.get_global_config_default_value('host', 'load.parallelismDegree')
    default_host_ping_maxFailure = conf_ops.get_global_config_default_value('host', 'ping.maxFailure')
    default_host_load_all = conf_ops.get_global_config_default_value('host', 'load.all')
    default_host_connection_autoReconnectOnError = conf_ops.get_global_config_default_value('host', 'connection.autoReconnectOnError')
    default_host_ping_sleepPeriodAfterFailure = conf_ops.get_global_config_default_value('host', 'ping.sleepPeriodAfterFailure')
    default_host_cpu_overProvisioning_ratio = conf_ops.get_global_config_default_value('host', 'cpu.overProvisioning.ratio')
    default_host_maintenanceMode_ignoreError = conf_ops.get_global_config_default_value('host', 'maintenanceMode.ignoreError')
    default_host_reconnectAllOnBoot = conf_ops.get_global_config_default_value('host', 'reconnectAllOnBoot')
    default_host_ping_interval = conf_ops.get_global_config_default_value('host', 'ping.interval')

   # change the default value

    conf_ops.change_global_config('host', 'ping.parallelismDegree', '50')
    conf_ops.change_global_config('host', 'update.os.parallelismDegree', '1')
    conf_ops.change_global_config('host', 'ping.timeout', '5')
    conf_ops.change_global_config('host', 'load.parallelismDegree', '50')
    conf_ops.change_global_config('host', 'ping.maxFailure', '4')
    conf_ops.change_global_config('host', 'load.all', 'false')
    conf_ops.change_global_config('host', 'connection.autoReconnectOnError', 'false')
    conf_ops.change_global_config('host', 'ping.sleepPeriodAfterFailure', '2')
    conf_ops.change_global_config('host', 'cpu.overProvisioning.ratio', '5')
    conf_ops.change_global_config('host', 'maintenanceMode.ignoreError', 'true')
    conf_ops.change_global_config('host', 'reconnectAllOnBoot', 'false')
    conf_ops.change_global_config('host', 'ping.interval', '30')

    # restore defaults

    conf_ops.change_global_config('host', 'ping.parallelismDegree', '%s' % default_host_ping_parallelismDegree)
    conf_ops.change_global_config('host', 'update.os.parallelismDegree', '%s' % default_host_update_os_parallelismDegree)
    conf_ops.change_global_config('host', 'ping.timeout', '%s' % default_host_ping_timeout)
    conf_ops.change_global_config('host', 'load.parallelismDegree', '%s' % default_host_load_parallelismDegree)
    conf_ops.change_global_config('host', 'ping.maxFailure', '%s' % default_host_ping_maxFailure)
    conf_ops.change_global_config('host', 'load.all', '%s' % default_host_load_all)
    conf_ops.change_global_config('host', 'connection.autoReconnectOnError', '%s' % default_host_connection_autoReconnectOnError)
    conf_ops.change_global_config('host', 'ping.sleepPeriodAfterFailure', '%s' % default_host_ping_sleepPeriodAfterFailure)
    conf_ops.change_global_config('host', 'cpu.overProvisioning.ratio', '%s' % default_host_cpu_overProvisioning_ratio)
    conf_ops.change_global_config('host', 'maintenanceMode.ignoreError', '%s' % default_host_maintenanceMode_ignoreError)
    conf_ops.change_global_config('host', 'reconnectAllOnBoot', '%s' % default_host_reconnectAllOnBoot)
    conf_ops.change_global_config('host', 'ping.interval', '%s' % default_host_ping_interval)

    test_util.test_pass('change the config ategory is host Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global default_host_ping_parallelismDegree

