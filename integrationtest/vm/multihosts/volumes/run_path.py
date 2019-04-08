#coding:utf-8
'''

Robot Test run specified path 

@author: Quarkonics
'''
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.test_state as ts_header
import os
import time

#Will sent 4000s as timeout, since case need to run at least ~3700s
_config_ = {
        'timeout' : 7200,
        'noparallel' : True
        }

test_dict = test_state.TestStateDict()
TestAction = ts_header.TestAction

default_config = [{"ps1": "PS"}, {"ps1": "default"}, {"host1": "HOST"}, {"host1": "default"}]

def test():
    case_flavor = test_util.load_paths(os.path.join(os.path.dirname(__file__), "templates"), os.path.join(os.path.dirname(__file__), "paths"))
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    initial_formation = flavor['initial_formation']
    if flavor.has_key('config'):
        config = flavor['config']
    else:
        config = None
    path_list = flavor['path_list']

    test_util.test_dsc('''Will mainly doing random test for all kinds of snapshot operations. VM, Volume and Image operations will also be tested. If reach 1 hour successful running condition, testing will success and quit.  SG actions, and VIP actions are removed in this robot test.
        VM resources: a special Utility vm is required to do volume attach/detach operation. 
        ''')

    test_util.test_dsc('Constant Path Test Begin.')
    robot_test_obj = test_util.Robot_Test_Object()
    if not config:
        config = default_config
    robot_test_obj.set_config(config)
    robot_test_obj.set_test_dict(test_dict)
    robot_test_obj.set_initial_formation(initial_formation)
    robot_test_obj.set_constant_path_list(path_list)

    test_lib.lib_robot_create_initial_formation(robot_test_obj)
    test_lib.lib_robot_create_utility_vm(robot_test_obj)
    rounds = 1
    current_time = time.time()
    timeout_time = current_time + 7200
    while time.time() <= timeout_time:
        print "DEBUG:",test_dict
        all_volume_list = test_dict.get_all_volume_list()
        for volume in all_volume_list:
            sp = test_dict.get_volume_snapshot(volume.get_volume().uuid)
            sp_list = sp.get_snapshot_list()
            for i in sp_list:
                print "spspspsp, %s,%s" % (i.get_snapshot().uuid, i.md5sum)
            print "vovovovo, %s,%s" % (volume.get_volume().uuid, volume.md5sum)
        test_util.test_dsc('New round %s starts:' % rounds)
        test_lib.lib_robot_constant_path_operation(robot_test_obj, set_robot=False)
        test_util.test_dsc('===============Round %s finished. Begin status checking.================' % rounds)
        rounds += 1
        test_lib.lib_robot_status_check(test_dict)
        test_util.test_logger("Remaining constant path: %s" % robot_test_obj.get_constant_path_list())
        if not robot_test_obj.get_constant_path_list():
            test_util.test_dsc('Reach test pass exit criterial: Required path executed %s' % (path_list))
            break

    test_lib.lib_robot_cleanup(test_dict)
    test_util.test_pass('Snapshots Robot Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_robot_cleanup(test_dict)
