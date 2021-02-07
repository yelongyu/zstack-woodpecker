'''
check the global_config category is vm
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
#import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global default_vm_videoType 
    global default_vm_bootMenu 
    global default_vm_expungePeriod 
    global default_vm_emulateHyperV 
    global default_vm_deletionPolicy
    global default_vm_numa
    global default_vm_vmPortOff
    global default_vm_cleanTraffic
    global default_vm_instanceOffering_setNullWhenDeleting
    global default_vm_dataVolume_deleteOnVmDestroy
    global default_vm_kvmHiddenState
    global default_vm_spiceStreamingMode
    global default_vm_expungeInterval

    #get the default value
    default_vm_videoType = conf_ops.get_global_config_default_value('vm', 'videoType')
    default_vm_bootMenu = conf_ops.get_global_config_default_value('vm', 'bootMenu')
    default_vm_expungePeriod = conf_ops.get_global_config_default_value('vm', 'expungePeriod')
    default_vm_emulateHyperV = conf_ops.get_global_config_default_value('vm', 'emulateHyperV')
    default_vm_deletionPolicy = conf_ops.get_global_config_default_value('vm', 'deletionPolicy')
    default_vm_numa = conf_ops.get_global_config_default_value('vm', 'numa')
    default_vm_vmPortOff = conf_ops.get_global_config_default_value('vm', 'vmPortOff')
    default_vm_cleanTraffic = conf_ops.get_global_config_default_value('vm', 'cleanTraffic')
    default_vm_instanceOffering_setNullWhenDeleting = conf_ops.get_global_config_default_value('vm', 'instanceOffering.setNullWhenDeleting')
    default_vm_dataVolume_deleteOnVmDestroy = conf_ops.get_global_config_default_value('vm', 'dataVolume.deleteOnVmDestroy')
    default_vm_kvmHiddenState = conf_ops.get_global_config_default_value('vm', 'kvmHiddenState')
    default_vm_spiceStreamingMode = conf_ops.get_global_config_default_value('vm', 'spiceStreamingMode')
    default_vm_expungeInterval = conf_ops.get_global_config_default_value('vm', 'expungeInterval')

   # change the default value

    conf_ops.change_global_config('vm', 'videoType', 'vga')
    conf_ops.change_global_config('vm', 'bootMenu', 'false')
    conf_ops.change_global_config('vm', 'expungePeriod', '3600')
    conf_ops.change_global_config('vm', 'emulateHyperV', 'true')
    conf_ops.change_global_config('vm', 'deletionPolicy', 'Direct')
    conf_ops.change_global_config('vm', 'numa', 'true')
    conf_ops.change_global_config('vm', 'vmPortOff', 'true')
    conf_ops.change_global_config('vm', 'cleanTraffic', 'true')
    conf_ops.change_global_config('vm', 'instanceOffering.setNullWhenDeleting', 'true')
    conf_ops.change_global_config('vm', 'dataVolume.deleteOnVmDestroy', 'true')
    conf_ops.change_global_config('vm', 'kvmHiddenState', 'true')
    conf_ops.change_global_config('vm', 'spiceStreamingMode', 'all')
    conf_ops.change_global_config('vm', 'expungeInterval', '3000')

    # restore defaults

    conf_ops.change_global_config('vm', 'videoType', '%s' % default_vm_videoType )
    conf_ops.change_global_config('vm', 'bootMenu', '%s' % default_vm_bootMenu)
    conf_ops.change_global_config('vm', 'expungePeriod', '%s' % default_vm_expungePeriod)
    conf_ops.change_global_config('vm', 'emulateHyperV', '%s' % default_vm_emulateHyperV)
    conf_ops.change_global_config('vm', 'deletionPolicy', '%s' % default_vm_deletionPolicy)
    conf_ops.change_global_config('vm', 'numa', '%s' % default_vm_numa)
    conf_ops.change_global_config('vm', 'vmPortOff', '%s' % default_vm_vmPortOff)
    conf_ops.change_global_config('vm', 'cleanTraffic', '%s' % default_vm_cleanTraffic)
    conf_ops.change_global_config('vm', 'instanceOffering.setNullWhenDeleting', '%s' % default_vm_instanceOffering_setNullWhenDeleting)
    conf_ops.change_global_config('vm', 'dataVolume.deleteOnVmDestroy', '%s' % default_vm_dataVolume_deleteOnVmDestroy)
    conf_ops.change_global_config('vm', 'kvmHiddenState', '%s' % default_vm_kvmHiddenState)
    conf_ops.change_global_config('vm', 'spiceStreamingMode', '%s' % default_vm_spiceStreamingMode)
    conf_ops.change_global_config('vm', 'expungeInterval', '%s' % default_vm_expungeInterval)

    test_util.test_pass('Create VM with spice Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global default_vm_videoType

