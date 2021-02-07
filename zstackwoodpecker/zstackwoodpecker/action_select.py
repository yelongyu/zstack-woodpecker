'''
@author: Yongkang
'''
import zstacklib.utils.list_ops as list_ops
import random

priorityType = 'priority_type'
priorityValue = 'priority_value'

weight = 'weight'
precentage = 'precentage'

random_strategy = 'random'
fair_strategy = 'fair'
weight_fair_strategy = 'weight_fair'
path_strategy = 'path_strategy'
resource_path_strategy = 'resource_path_strategy'
default_strategy = random_strategy

class ActionPriority(object):
    '''
    Define the robot action priority class
    '''
    def __init__(self):
        self.action_priority_dict = {}

    def _validate(self):
        '''
        The sum of all actions' percentage should not exceed 100%
        '''
        sum = 0
        for key, value in self.get_priority_action_dict().iteritems():
            if value[priorityType] != weight:
                sum += value[priorityValue]

        if sum > 100:
            import zstackwoodpecker.test_util as test_util
            raise test_util.TestError('The Sum of actions priority percentage should not exceed 100. Now it is : %s' % sum)

    def add_priority_action(self, action_name, priority_type = weight, \
            priority_value = None):
        '''
        When priority_type is 'weight', the priority_value should be integate.
        When priority_type is 'percentage', the priority_value should be an
        integate between 1 ~ 100
        '''

        if priority_type == weight:
            if not priority_value :
                priority_value = 1
            elif not isinstance(priority_value, int):
                priority_value = 1

        if self.action_priority_dict.has_key(action_name):
            print ('Add duplicated action, will remove the old one')

        self.action_priority_dict[action_name] = {priorityType: priority_type, \
                priorityValue: priority_value}

    def add_priority_action_list(self, action_list):
        '''
        Based on action_list to set action priority weight
        '''
        for action in action_list:
            if self.action_priority_dict.has_key(action):
                if self.get_action_priority_type(action) == weight:
                    self.action_priority_dict[action][priorityValue] += 1
            else:
                self.action_priority_dict[action] = {\
                        priorityType: weight, \
                        priorityValue: 1}

    def get_priority_action_list(self):
        action_list = []
        for key, value in self.action_priority_dict.iteritems():
            if value[priorityType] == weight:
                action_list.extend([key] * value[priorityValue])

        return action_list

    def get_priority_action(self, action_name):
        return self.action_priority_dict[action_name]

    def set_action_priority_type(self, action_name, priority_type):
        self.action_priority_dict[action_name][priorityType] = priority_type

    def get_action_priority_type(self, action_name):
        return self.action_priority_dict[action_name][priorityType]

    def set_action_priority_value(self, action_name, priority_value):
        self.action_priority_dict[action_name][priorityValue] = priority_value

    def get_action_priority_value(self, action_name):
        return self.action_priority_dict[action_name][priorityValue]

    def get_priority_action_dict(self):
        return self.action_priority_dict

class ActionSelector(object):
    def __init__(self, action_list, history_actions, priority_actions):
        self.history_actions = history_actions
        self.action_list = action_list
        self.priority_actions = priority_actions

    def select(self):
        '''
        New Action Selector need to implement own select() function. 
        '''
        pass

    def get_action_list(self):
        return self.action_list

    def get_priority_actions(self):
        return self.priority_actions

    def get_history_actions(self):
        return self.history_actions

class RandomActionSelector(ActionSelector):
    '''
    Base on the priority action list, just randomly pickup action. 

    If need to set higher priority for some action, it just needs to put them
    more times in priority_actions list. 
    '''
    def __init__(self, action_list, history_actions, priority_actions):
        super(RandomActionSelector, self).__init__(action_list, \
                history_actions, priority_actions)

    def select(self):
        priority_actions = self.priority_actions.get_priority_action_list()
        #test_util.test_logger('Priority Action List: %s ' % priority_actions)
        for action in priority_actions:
            if action in self.get_action_list():
                self.action_list.append(action)

        #test_util.test_logger('Candidate Action List: %s ' % action_list)
        return random.choice(self.get_action_list())

class FairActionSelector(ActionSelector):
    '''
    Based on priority action, will fairly choose next action. 

    In allowed condition, the priority action will not exceed other action 2 
    times. When all possible actions in action list have been executed with 
    same times, the priority action will be executed next time. If there are 
    some actions has less execution times, the next action will be picked up
    from these actions. 
    '''
    def __init__(self, action_list, history_actions, priority_actions):
        super(FairActionSelector, self).__init__(action_list, \
                history_actions, priority_actions)

    def parse_pre_actions(self):
        pre_action_dict = {}
        for key in self.history_actions:
            if pre_action_dict.has_key(key):
                pre_action_dict[key] += 1
            else:
                pre_action_dict[key] = 1

        return pre_action_dict

    def cal_least_execute_action(self, pre_action_dict):
        action_times_dict = {}
        for action in pre_action_dict.keys():
            if not action in self.action_list:
                continue

            times = pre_action_dict[action]
            if action_times_dict.has_key(times):
                action_times_dict[times].append(action)
            else:
                action_times_dict[times] = [action]

        all_times = action_times_dict.keys()
        all_times.sort()
        return action_times_dict[all_times[0]]

    def select(self):
        priority_actions = self.priority_actions.get_priority_action_list()
        pri_action_list = list_ops.unique_list(priority_actions)
        pre_action_dict = self.parse_pre_actions()
        pre_action_list = pre_action_dict.keys()
    
        #not executed action is always higher priority in this pickup strategy
        not_executed_actions = list_ops.list_minus(self.action_list, \
                pre_action_list)
        #test_util.test_logger('Not executed actions: %s ' % not_executed_actions)
        print('Not executed actions: %s ' % not_executed_actions)
    
        #test_util.test_logger('Priority Action List: %s ' % pri_action_list)
        print('Priority Action List: %s ' % pri_action_list)
    
        if not_executed_actions:
            if pri_action_list:
                pri_not_executed_actions = list_ops.list_and(not_executed_actions, pri_action_list)
                if pri_not_executed_actions:
                    return random.choice(pri_not_executed_actions)
            return random.choice(not_executed_actions)
        else:
            least_actions = self.cal_least_execute_action(pre_action_dict)
            pri_least_actions = list_ops.list_and(least_actions, pri_action_list)
            if pri_least_actions:
                return random.choice(pri_least_actions)
            else:
                return random.choice(least_actions)

class WeightActionSelector(ActionSelector):
    pass

class WeightFairActionSelector(FairActionSelector):
    '''
    An enhanced selector based on fair selector by adding weight consideration.

    If a priority action is weight as 2, it will be executed 2 times than other
    weight=1 priority action. 
    '''
    def __init__(self, action_list, history_actions, priority_actions):
        super(WeightFairActionSelector, self).__init__(action_list, \
                history_actions, priority_actions)

    def cal_least_execute_action(self, pre_action_dict):
        action_times_dict = {}
        priority_action_list = self.priority_actions.get_priority_action_list()
        for action in pre_action_dict.keys():
            if not action in self.action_list:
                continue

            times = pre_action_dict[action]
            if action in priority_action_list and \
                    self.priority_actions.get_action_priority_type(action) \
                    == weight:
                times = times / \
                        self.priority_actions.get_action_priority_value(action)

            if action_times_dict.has_key(times):
                action_times_dict[times].append(action)
            else:
                action_times_dict[times] = [action]

        all_times = action_times_dict.keys()
        all_times.sort()
        return action_times_dict[all_times[0]]

class PathActionSelector(ActionSelector):
    '''
    Based on history action path to select next action, it is try to cover all
    possible combination and avoid duplicated path.
    Will not consider the priority in this selector.
    '''
    def __init__(self, action_list, history_actions, priority_actions):
        super(PathActionSelector, self).__init__(action_list, \
                history_actions, priority_actions)

    def _get_action_history_next_actions(self, pre_action):
        action_list = []
        index = 1
        history_actions_num = len(self.history_actions)
        for action in self.history_actions:
            index += 1
            if action == pre_action and index <= history_actions_num:
                action_list.append(self.history_actions[index - 1])

        return action_list

    def _find_longest_not_executed_action(self, action_list):
        if len(action_list) == 1:
            return action_list[0]

        tmp_action_list = list(action_list)
        tmp_history_action_list = list(self.history_actions)
        tmp_history_action_list.reverse()
        for action in tmp_history_action_list:
            if action in tmp_action_list:
                tmp_action_list.remove(action)
                if len(tmp_action_list) == 1:
                    return tmp_action_list[0]

        return random.choice(tmp_action_list)

    def select(self):
        if not self.history_actions:
            return random.choice(self.action_list)

        last_action = self.history_actions[-1]
        previous_next_action_list = \
                self._get_action_history_next_actions(last_action)

        not_executed_actions = []
        for action in self.action_list:
            if not action in previous_next_action_list:
                not_executed_actions.append(action)
        
        if not_executed_actions:
            #try to find the latest not executed action
            return self._find_longest_not_executed_action(not_executed_actions)

        return self._find_longest_not_executed_action(self.action_list)

action_selector_table = {
        random_strategy: RandomActionSelector,
        fair_strategy: FairActionSelector,
        weight_fair_strategy: WeightFairActionSelector,
        path_strategy: PathActionSelector,
        resource_path_strategy: PathActionSelector
        }

