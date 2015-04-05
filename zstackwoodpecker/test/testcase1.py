'''

@author: Frank
'''

from zstackwoodpecker.engine.engine import *

Property(zone = 'zone1')
Property(zoneName = P('zone'))
Property(zoneDesc = 'this is zone1')

Target(
       name = 'target1',
       actions = [
                  Action(id='zone1', name='createZone',
                         args=IN(name=P('zoneName'), description=P('zoneDesc'))),
                 ],
       )

Target(
       name = 'target2',
       actions = [
                  Action(id='zone1', name='createZone',
                         args=IN(name=P('zoneName'), description=P('zoneDesc'))),
                 ],
       )

Target(
       name = 'target3',
       actions = [
                  Action(id='zone1', name='createZone',
                         args=IN(name=P('zoneName'), description=P('zoneDesc'))),
                 ],
       depends = ['target1', 'target2']
       )

Target(
       name = 'target4',
       actions = [
                  Action(id='zone1', name='createZone',
                         args=IN(name=P('zoneName'), description=P('zoneDesc'))),
                 ],
       depends = ['target1']
       )

Target(
       name = 'target5',
       actions = [
                  Action(id='zone1', name='createZone',
                         args=IN(name=P('zoneName'), description=P('zoneDesc'))),
                 ],
       depends = ['target3', 'target4']
       )

RunTarget('target5')
