import json

from rigBuilder.components.core import Component, ComponentBuilder, Attribute, Connection
from rigBuilder.core import MyOrderedDict
from rigBuilder.types import Side
from rigBuilder.files.core import customEncoder, JsonFile


def test():

    arm = Component(name='arm', side=Side('L'), bilateral=True, color=(10, 10, 10))
    leg = Component(name='leg', side=Side('L'), bilateral=True)
    base = Component(name='base')

    componentDict = MyOrderedDict()
    componentDict['arm'] = arm
    componentDict['leg'] = leg
    componentDict['base'] = base

    connection1 = Connection(
        source=Attribute(key='base', attribute='outputs', index=0),
        destination=Attribute(key='arm', attribute='inputs', index=0),
        bilateral=True
    )
    connection2 = Connection(
        source=Attribute(key='arm', attribute='outputs', index=0),
        destination=Attribute(key='leg', attribute='inputs', index=0),
        bilateral=True
    )

    connectionDict = MyOrderedDict()
    connectionDict['connection1'] = connection1
    connectionDict['connection2'] = connection2

    componentBuilder = ComponentBuilder(componentDict, connectionDict)
    # componentBuilder.build()

    JsonFile(r'C:\Users\Pierre\Desktop\New folder\componentBuilder.json').dump(componentBuilder, force=True)

    print json.dumps(componentBuilder, indent=4, default=customEncoder)
