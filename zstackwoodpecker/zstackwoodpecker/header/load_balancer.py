import zstackwoodpecker.header.header as zstack_header
DELETED = 'DELETED'
LB_ALGORITHM_RR = 'roundrobin'
LB_ALGORITHM_LC = 'leastconn'
LB_ALGORITHM_SO = 'source'

class TestLoadBalancer(zstack_header.ZstackObject):
    def __init__(self):
        self.load_balancer = None
        self.state = None 

    def __repr__(self):
        if self.get_load_balancer():
            return '%s-%s' % (self.__class__.__name__, self.get_load_balancer().uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        pass

    def delete(self):
        self.state = DELETED

    def check(self):
        pass

    def get_load_balancer(self):
        return self.load_balancer

    def get_state(self):
        return self.state

class TestLoadBalancerListener(zstack_header.ZstackObject):
    def __init__(self):
        self.load_balancer_listener = None
        self.state = None 
        self.algorithm = LB_ALGORITHM_RR

    def __repr__(self):
        if self.get_load_balancer_listener():
            return '%s-%s' % (self.__class__.__name__, \
                    self.get_load_balancer_listener().uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        pass

    def delete(self):
        self.state = DELETED

    def check(self):
        pass

    def get_load_balancer_listener(self):
        return self.load_balancer_listener

    def get_state(self):
        return self.state

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def get_algorithm(self):
        return self.algorithm
