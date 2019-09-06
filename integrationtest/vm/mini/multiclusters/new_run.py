import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.robot_action as Robot
import os

_config_ = {
    'timeout': 10400,
    'noparallel': True
}
Robot.MINI = True

case_flavor = test_util.load_paths(os.path.join(os.path.dirname(__file__), "templates"),
                                   os.path.join(os.path.dirname(__file__), "paths"))

test_dict = None


def test():
    global test_dict
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    test_util.test_dsc('''Will mainly doing random test for all kinds of snapshot operations. VM, Volume and Image operations will also be tested. If reach 1 hour successful running condition, testing will success and quit.  SG actions, and VIP actions are removed in this robot test.
            VM resources: a special Utility vm is required to do volume attach/detach operation.
            ''')
    test_util.test_dsc('Constant Path Test Begin.')

    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    path_list = flavor['path_list']
    repeat = flavor['repeat']

    #Robot.robot_create_utility_vm()
    robot_test_obj = Robot.robot()
    robot_test_obj.initial(path_list)

    while repeat > 0:
        test_util.test_logger("Robot action: Iteration %s" % (repeat))
        test_dict = robot_test_obj.get_test_dict()
        Robot.robot_run_constant_path(robot_test_obj, set_robot=False)

        repeat -= 1
        test_dict.cleanup()
        del test_dict
        robot_test_obj.test_dict = Robot.robot_test_dict()

def env_recover():
    global test_dict
    if test_dict:
        test_dict.cleanup()


def error_cleanup():
    global test_dict
    if test_dict:
        # test_dict.cleanup()
        pass
