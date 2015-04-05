'''

@author: Frank
'''
from zstackwoodpecker.engine.engine import *

Target(
       name = 'login',
       actions = [
                  Action(id='login', name='logInAsAdmin')
                  ]
       )

Property(sessionUuid=O('login').sessionUuid)

Target(
       name = 'logout',
       actions = [
                  Action(id='logout', name='logOut',
                         args=IN(sessionUuid=RP('sessionUuid')))
                  ]
       )

Target(
       name = 'setup',
       actions = [
                  Action(id='zone', name='createZone',
                         args=IN(name='zone1', description='zone1', sessionUuid=RP('sessionUuid'))),
                  
                  Action(id='cluster', name='createCluster',
                         args=IN(name='cluster1', zoneUuid=O('zone').uuid,
                                 sessionUuid=RP('sessionUuid'),
                                 hypervisorType='KVM'))
                  ],
       )

Target(
       name = 'run',
       depends = ['login', 'setup', 'logout']
       )

RunTarget('run')