import os
import json

from rigBuilder.components.core import Component, ComponentBuilder, Attribute, Connection
from rigBuilder.core import MyOrderedDict
from rigBuilder.types import Side
from rigBuilder.files.core import customEncoder, JsonFile
from rigBuilder.components.oneCtrl import OneCtrl


def test():

    arm = Component(name='arm', side=Side('L'), bilateral=True, color=(10, 10, 10))
    leg = Component(name='leg', side=Side('L'), bilateral=True)
    base = OneCtrl(name='base')

    componentDict = MyOrderedDict()
    componentDict['arm'] = arm
    componentDict['leg'] = leg
    componentDict['base'] = base

    connection1 = Connection(
        sources=[
            Attribute(key='base', attribute='outputs', index=0),
            Attribute(key='base', attribute='outputs', index=1),
            Attribute(key='base', attribute='outputs', index=2),
        ],
        destination=Attribute(key='arm', attribute='inputs', index=0),
        bilateral=True
    )
    connection2 = Connection(
        sources=[Attribute(key='arm', attribute='outputs', index=0)],
        destination=Attribute(key='leg', attribute='inputs', index=0),
        bilateral=True
    )

    connectionDict = MyOrderedDict()
    connectionDict['connection1'] = connection1
    connectionDict['connection2'] = connection2

    componentBuilder = ComponentBuilder(componentDict, connectionDict)
    # componentBuilder.build()

    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    path = os.path.join(desktop, 'componentBuilder.json')

    JsonFile(path).dump(componentBuilder, force=True)

    print json.dumps(componentBuilder, indent=4, default=customEncoder)
