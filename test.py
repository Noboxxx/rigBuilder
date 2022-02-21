import json

from rigBuilder.components.core import Component, ComponentBuilder, Attribute, Connection
from rigBuilder.types import Side
from rigBuilder.files.core import customEncoder, JsonFile


def test():

    arm = Component(name='arm', side=Side('L'), bilateral=True, color=(10, 10, 10))
    leg = Component(name='leg', side=Side('L'), bilateral=True)
    base = Component(name='base')

    componentDict = {
        'arm': arm,
        'leg': leg,
        'base': base,
    }

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

    connectionList = [
        connection1,
        connection2,
    ]

    componentBuilder = ComponentBuilder(componentDict, connectionList)
    # componentBuilder.build()

    JsonFile(r'C:\Users\Pierre\Desktop\New folder\componentBuilder.json').dump(componentBuilder, force=True)

    print json.dumps(componentBuilder, indent=4, default=customEncoder)
