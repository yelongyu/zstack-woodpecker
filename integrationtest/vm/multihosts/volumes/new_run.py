import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.robot_action as Robot
import os

_config_ = {
    'timeout': 7200,
    'noparallel': True
}


case_flavor = test_util.load_paths(os.path.join(os.path.dirname(__file__), "templates"),
                                   os.path.join(os.path.dirname(__file__), "paths"))


def test():
    test_util.test_dsc('''Will mainly doing random test for all kinds of snapshot operations. VM, Volume and Image operations will also be tested. If reach 1 hour successful running condition, testing will success and quit.  SG actions, and VIP actions are removed in this robot test.
            VM resources: a special Utility vm is required to do volume attach/detach operation. 
            ''')
    test_util.test_dsc('Constant Path Test Begin.')

    Robot.robot_create_utility_vm()

    robot_test_obj = Robot.robot()
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    initial_formation = flavor['initial_formation']
    path_list = flavor['path_list']


    robot_test_obj.initial(path_list, initial_formation)
    Robot.robot_run_constant_path(robot_test_obj, set_robot=True)

def error_cleanup():
    pass