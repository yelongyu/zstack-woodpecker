'''
zstack node test class

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.setup_actions as setup_actions
import zstackwoodpecker.operations.node_operations as node_ops
import zstacklib.utils.linux as linux

STOPPED = 'stopped'
RUNNING = 'running'
UNKNOWN = 'unknown'

class ZstackTestNode(object):
    def __init__(self):
        self.node_option = test_util.NodeOption()
        self.state = UNKNOWN
        self.node = None
        self.test_node = None

    def is_docker_node(self):
        return self.node_option.get_docker_image()

    def add(self, deploy_config):
        if self.state == RUNNING:
            return

        if self.is_docker_node():
            self.test_node = setup_actions.DockerNode(deploy_config)
            self.test_node.set_docker_image(self.node_option.get_docker_image())
        else:
            self.test_node = setup_actions.HostNode(deploy_config)

        self.test_node.set_username(self.node_option.get_username())
        self.test_node.set_password(self.node_option.get_password())
        self.test_node.set_node_ip(self.node_option.get_management_ip())

        self.test_node.start_node()
        if self.wait_for_node_start():
            self.state = RUNNING
            self.node = node_ops.get_management_node_by_host_ip(self.node_option.get_management_ip())[0]

    def wait_for_node_start(self, timeout=120):
        if not linux.wait_callback_success(node_ops.is_management_node_start, \
                self.node_option.get_management_ip(), timeout=timeout, \
                interval=0.5):
            test_util.test_logger('multi node does not startup on host: %s' \
                    % self.node_option.get_management_ip())
            return False
        test_util.test_logger('multi node startup on host: %s' \
                % self.node_option.get_management_ip())
        return True

    def stop(self):
        self.test_node.stop_node()
        self.state = STOPPED

    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()

    def set_node_option(self, node_option):
        self.node_option = node_option

    def get_node_option(self):
        return self.node_option

    def get_node(self):
        return self.node

    def get_state(self):
        return self.state

    def get_test_node(self):
        return self.test_node
