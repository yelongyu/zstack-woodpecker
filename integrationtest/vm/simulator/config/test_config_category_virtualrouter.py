'''
check the global_config category is virtualRouter
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_virtualRouter_1
    global deft_virtualRouter_2
    global deft_virtualRouter_3
    global deft_virtualRouter_4
    global deft_virtualRouter_5
    global deft_virtualRouter_6
    global deft_virtualRouter_7
    global deft_virtualRouter_8
    global deft_virtualRouter_9

    #get the default value
    deft_virtualRouter_1 = conf_ops.get_global_config_default_value('virtualRouter', 'agent.deployOnStart')
    deft_virtualRouter_2 = conf_ops.get_global_config_default_value('virtualRouter', 'vrouter.echoTimeout')
    deft_virtualRouter_3 = conf_ops.get_global_config_default_value('virtualRouter', 'ssh.port')
    deft_virtualRouter_4 = conf_ops.get_global_config_default_value('virtualRouter', 'command.parallelismDegree')
    deft_virtualRouter_5 = conf_ops.get_global_config_default_value('virtualRouter', 'ssh.username')
    deft_virtualRouter_6 = conf_ops.get_global_config_default_value('virtualRouter', 'ping.interval')
    deft_virtualRouter_7 = conf_ops.get_global_config_default_value('virtualRouter', 'ping.parallelismDegree')
    deft_virtualRouter_8 = conf_ops.get_global_config_default_value('virtualRouter', 'vrouter.password')
    deft_virtualRouter_9 = conf_ops.get_global_config_default_value('virtualRouter', 'dnsmasq.restartAfterNumberOfSIGUSER1')


   # change the default value

    conf_ops.change_global_config('virtualRouter', 'agent.deployOnStart', 'true')
    conf_ops.change_global_config('virtualRouter', 'vrouter.echoTimeout', '30')
    conf_ops.change_global_config('virtualRouter', 'ssh.port', '222')
    conf_ops.change_global_config('virtualRouter', 'command.parallelismDegree', '50')
    conf_ops.change_global_config('virtualRouter', 'ssh.username', 'root')
    conf_ops.change_global_config('virtualRouter', 'ping.interval', '30')
    conf_ops.change_global_config('virtualRouter', 'ping.parallelismDegree', '200')
    conf_ops.change_global_config('virtualRouter', 'vrouter.password', 'password')
    conf_ops.change_global_config('virtualRouter', 'dnsmasq.restartAfterNumberOfSIGUSER1', '200')

    # restore defaults

    conf_ops.change_global_config('virtualRouter', 'agent.deployOnStart', '%s' % deft_virtualRouter_1)
    conf_ops.change_global_config('virtualRouter', 'vrouter.echoTimeout', '%s' % deft_virtualRouter_2)
    conf_ops.change_global_config('virtualRouter', 'ssh.port', '%s' % deft_virtualRouter_3)
    conf_ops.change_global_config('virtualRouter', 'command.parallelismDegree', '%s' % deft_virtualRouter_4)
    conf_ops.change_global_config('virtualRouter', 'ssh.username', '%s' % deft_virtualRouter_5)
    conf_ops.change_global_config('virtualRouter', 'ping.interval', '%s' % deft_virtualRouter_6)
    conf_ops.change_global_config('virtualRouter', 'ping.parallelismDegree', '%s' % deft_virtualRouter_7)
    conf_ops.change_global_config('virtualRouter', 'vrouter.password', '%s' % deft_virtualRouter_8)
    conf_ops.change_global_config('virtualRouter', 'dnsmasq.restartAfterNumberOfSIGUSER1', '%s' % deft_virtualRouter_9)


#Will be called only if exception happens in test().
def error_cleanup():
    global deft_virtualRouter_1

