'''
Run test in a chain, the chained actions would be picked up randomly or by some algorithm

@author: Legion
'''

import types, random
import zstacklib.utils.jsonobject as jsonobject
import zstackwoodpecker.test_util  as test_util

class TestChain(object):
    def __init__(self, chain_head, chain_length=20):
#         self.test_obj = test_obj
        test_ops = filter(lambda x, obj=self: not x.startswith('_') 
                          and hasattr(eval('obj.%s' % x), '__call__'), 
                          dir(self))
        self.chain_list = [ops for ops in test_ops if eval('self.%s.__doc__' % ops) is not None]
        self.test_list = chain_head if isinstance(chain_head, types.ListType) else [chain_head]
        self.chain_length = chain_length
        self.test_chain = ''
        self.weights = {}
        self.skip = []
        self.delay = {}
        self.runned_chain = []

    def __call__(self):
        return self

    def make_chain(self, delay_added=None):
        test = jsonobject.loads(eval('self.%s.__doc__' % self.test_list[-1].split('(')[0]))
        if test.skip:
            self.skip.extend(test.skip)
        if test.weight:
            self.weights[self.test_list[-1]] = test.weight
        if test.must:
            if test.must.before:
                for before_ops in test.must.before:
                    self.test_list.insert(-1, before_ops)
            if test.must.after:
                for after_ops in test.must.after:
                    self.test_list.append(after_ops)
        next_list = list(set(test.next) - set(self.skip))
        _next_list = next_list[:]
        for act in next_list:
            if self.weights.has_key(act):
                for _ in range(int(self.weights[act])):
                    _next_list.append(act)
            else:
                if act not in self.test_list:
                    self.test_list.append(act)
                    break
        else:
            random.shuffle(_next_list)
            self.test_list.append(random.choice(_next_list))
        if test.delay:
            for dly in test.delay:
                self.delay[len(self.test_list)] = dly
        self.chain_length -= 1
        if self.chain_length > 0:
            self.make_chain(test.delay)
        else:
            for pos in self.delay.keys():
                self.test_list.insert(random.randint(pos, len(self.test_list)), self.delay[pos])
        self.test_chain = 'self.' + '().'.join(self.test_list) + '()'

    def run_test(self):
        for action in self.chain_list:
            if action in self.test_list:
                test_util.test_dsc('Action [%s] will be run [%s] times' % 
                                   (action, self.test_list.count(action)))
#         eval(self.test_chain)
        for test in self.test_list:
            test_util.test_dsc("Next Action is [%s]" % test)
            eval('self.%s()' % test)
            self.runned_chain.append(test)
            test_util.test_dsc("Passed chain: %s" % self.runned_chain)
            test_util.test_dsc("Left chain: %s" % list(set(self.test_list) - set(self.runned_chain)))
