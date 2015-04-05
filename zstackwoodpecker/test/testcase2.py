'''

@author: Frank
'''

from zstackwoodpecker.engine.engine import *

PropertyFile(REALATIVE_path('test.properties'))

Property(hi="hi", hello="hello", a="b")

@RT
def say(s):
    return 'hi, %s' % s

Target(
       name = 'target1',
       actions = [
                  Action(id='a1', name='fakeAction1',
                         args=IN(greeting=say(P('greeting1'))))
                  ]
       )

Target(
       name = 'target2',
       actions = [
                  Action(id='a2', name='fakeAction2',
                         args=IN(greeting=P('hi')))
                  ],
       depends = ['target1'],
       stopOnError=False,
       )

RunTarget('target2')