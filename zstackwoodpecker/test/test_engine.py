'''

@author: Frank
'''
import unittest
from zstackwoodpecker.engine import engine

class Test(unittest.TestCase):
    def testName(self):
        logfd = open('/tmp/log', 'w')
        engine.execute_case('test/testcase2.py', logfd)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()