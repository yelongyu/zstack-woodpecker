'''

@author: Frank
'''

import os
import zstackwoodpecker.setup_actions as setup_actions
import zstackwoodpecker.operations.scenario_operations as scenario_operations
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstacklib.utils.shell as shell

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH

def deploy_vbmc(vm_ip=None):
    if vm_ip != None:
        ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null'
        shell.call('%s %s yum --disablerepo=epel install -y libvirt-devel' %(ssh_cmd, vm_ip))
        #To avoid bug behind, reinstall python-pip before upgrade. bug: ImportError: 'module' object has no attribute 'main'
        shell.call('%s %s yum --nogpg -y reinstall python-pip' %(ssh_cmd, vm_ip))
        shell.call('%s %s pip install --upgrade pip' %(ssh_cmd, vm_ip))
        shell.call('%s %s pip install virtualbmc' %(ssh_cmd, vm_ip))
        #shell.call('scp %s/integrationtest/vm/baremetal/vbmc.py \
        #       %s:/var/lib/zstack/virtualenv/woodpecker/lib/python2.7/site-packages/virtualbmc/vbmc.py -fr' \
        #       % (os.environ.get('woodpecker_root_path'),vm_ip))
    else:
        shell.call('yum --disablerepo=epel install -y libvirt-devel')
        shell.call('%s %s yum -y reinstall python-pip' %(ssh_cmd, vm_ip))
        shell.call('pip install --upgrade pip')
        shell.call('pip install virtualbmc')
        shell.call('cp %s/integrationtest/vm/baremetal/vbmc.py \
               /var/lib/zstack/virtualenv/woodpecker/lib/python2.7/site-packages/virtualbmc/vbmc.py -fr' \
               % os.environ.get('woodpecker_root_path'))
    test_util.test_logger('Virtualbmc has been deployed on Host')

def test():
    if test_lib.scenario_config != None and test_lib.scenario_file != None and not os.path.exists(test_lib.scenario_file):
        scenario_operations.deploy_scenario(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        test_util.test_skip('Suite Setup Success')
    if test_lib.scenario_config != None and test_lib.scenario_destroy != None:
        scenario_operations.destroy_scenario(test_lib.all_scenario_config, test_lib.scenario_destroy)

    #setup = setup_actions.SetupAction()
    #setup.plan = test_lib.all_config
    #setup.run()

    test_lib.setup_plan.deploy_test_agent()

    test_lib.setup_plan.execute_plan_without_deploy_test_agent()

    if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        mn_ips = deploy_operations.get_nodes_from_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
            os.system("bash %s '%s'" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ips))
            deploy_vbmc(mn_ips)
    elif os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % (EXTRA_SUITE_SETUP_SCRIPT))
        deploy_vbmc()

    deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    delete_policy = test_lib.lib_set_delete_policy('vm', 'Direct')
    delete_policy = test_lib.lib_set_delete_policy('volume', 'Direct')
    delete_policy = test_lib.lib_set_delete_policy('image', 'Direct')
    if test_lib.lib_get_ha_selffencer_maxattempts() != None:
	test_lib.lib_set_ha_selffencer_maxattempts('60')
	test_lib.lib_set_ha_selffencer_storagechecker_timeout('60')
    test_lib.lib_set_primary_storage_imagecache_gc_interval(1)
    test_util.test_pass('Suite Setup Success')
