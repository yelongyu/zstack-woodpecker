'''
Run test in a chain, the chained actions would be picked up randomly or by some algorithm

@author: Legion
'''

import types, random
import zstacklib.utils.jsonobject as jsonobject
import zstackwoodpecker.test_util  as test_util

class TestChain(object):
    def __init__(self, test_obj, chain_head, chain_length=20):
        self.test_obj = test_obj
        test_ops = filter(lambda x, obj=test_obj: not x.startswith('_') 
                          and hasattr(eval('obj.%s' % x), '__call__'), 
                          dir(test_obj))
        self.chain_list = [ops for ops in test_ops if eval('test_obj.%s.__doc__' % ops) is not None]
        self.test_list = chain_head if isinstance(chain_head, types.ListType) else [chain_head]
        self.chain_length = chain_length
        self.test_chain = ''
        self.weights = {}
        self.skip = []

    def make_chain(self, delay_added=None):
        test = jsonobject.loads(eval('self.test_obj.%s.__doc__' % 
                                     (self.test_list[-2].split('(')[0] 
                                      if delay_added 
                                      else self.test_list[-1].split('(')[0])))
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
        for act in test.next:
            if self.weights.has_key(act):
                for _ in range(int(self.weights[act])):
                    next_list.append(act)
            else:
                if act not in self.test_list:
                    self.test_list.append(act)
                    break
        else:
            random.shuffle(next_list)
            self.test_list.append(random.choice(next_list))
        if test.delay:
            self.test_list.append(test.delay)
        self.chain_length -= 1
        if self.chain_length > 0:
            self.make_chain(test.delay)
        self.test_chain = 'self.test_obj' + '.' + '().'.join(self.test_list) + '()'

    def run_test(self):
        for action in self.chain_list:
            if action in self.test_list:
                test_util.test_dsc('Action [%s] will be run [%s] times' % 
                                   (action, self.test_list.count(action)))
        eval(self.test_chain)
