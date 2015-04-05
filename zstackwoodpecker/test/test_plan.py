'''

@author: Frank
'''
import unittest
from zstacktest import test_util
import os.path

class Test(unittest.TestCase):

    def testName(self):
        cfg = os.path.join(os.path.dirname(__file__), 'plan1.xml')
        plan = test_util.Plan(cfg)
        plan.execute_plan()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
