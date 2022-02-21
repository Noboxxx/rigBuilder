from maya import cmds
from rigBuilder.types import Side, Color, UnsignedInt, UnsignedFloat
from rigBuilder.core import Data


class Attribute(Data):

    def __init__(self, key, attribute, index):
        # type: (str, str, int) -> None
        super(Attribute, self).__init__()

        self.key = key
        self.attribute = attribute
        self.index = index

    def get(self, componentDict):
        if self.key not in componentDict:
            return None

        component = componentDict[self.key]

        if self.attribute not in dir(component):
            return None

        attribute = getattr(component, self.attribute)

        try:
            return attribute[self.index]
        except IndexError:
            return None


class Connection(Data):

    def __init__(self, source, destination, bilateral=False):
        # type: (Attribute, Attribute, bool) -> None
        super(Connection, self).__init__()

        self.source = source
        self.destination = destination
        self.bilateral = bilateral

    def build(self, componentDict):
        print 'build: {} -> {}'.format(self.source.get(componentDict), self.destination.get(componentDict))


class Plug(list):
    pass


class Output(Plug):
    pass


class Input(Plug):
    pass


class Component(Data):

    def __init__(self, name='untitled', side='L', index=0, color=(255, 255, 0), size=1.0, bilateral=False):
        super(Component, self).__init__()

        self.name = str(name)
        self.side = Side(side)
        self.index = UnsignedInt(index)
        self.color = Color(*color)
        self.size = UnsignedFloat(size)
        self.bilateral = bool(bilateral)

        self.interface = None
        self.inputs = Input()
        self.outputs = Output()
        self.children = list()

    def __repr__(self):
        return repr(str(self))

    def __str__(self):
        return '{}_{}_{}'.format(self.name, self.side, self.index)

    def mirror(self):
        self.side = self.side.mirrored()
        self.color = self.color.mirrored()

    def mirrored(self):
        copy = self.copy()
        copy.mirror()
        return copy

    def build(self):
        self.buildFolder()

    def buildFolder(self):
        if cmds.objExists(str(self)):
            raise RuntimeError('folder named \'{}\' already exists.'.format(self))

        folder = cmds.group(empty=True, name=str(self))

        if self.children:
            cmds.parent(self.children, folder)

        for attr, plug in self.getPlugDict().items():
            cmds.addAttr(str(self), longName=attr, attributeType='message', multi=True)
            for index, node in enumerate(plug):

                objAttr = 'receiver'
                objPlug = '{}.{}'.format(node, objAttr)
                if not cmds.objExists(objPlug):
                    cmds.addAttr(node, longName=objAttr, attributeType='message', multi=True, indexMatters=False)

                indexedPlug = '{}.{}[{}]'.format(self, attr, index)
                cmds.connectAttr(indexedPlug, objPlug, nextAvailable=True)

    def getPlugDict(self):
        plugDict = dict()
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, Plug):
                plugDict[attr] = value
        return plugDict


class ComponentBuilder(Data):

    def __init__(self, componentDict=None, connectionList=None):
        # type: (dict[str: Component], List[Connection]) -> None
        super(ComponentBuilder, self).__init__()

        self.componentDict = componentDict
        self.connectionList = connectionList

    def build(self):
        mirroredComponentDict = dict()
        for key, component in self.componentDict.items():
            component.build()

            mirrorComponent = None
            if component.bilateral:
                mirrorComponent = component.mirrored()
                mirrorComponent.build()

            mirroredComponentDict[key] = mirrorComponent or component

        for connection in self.connectionList:
            connection.build(self.componentDict)

            if connection.bilateral:
                connection.build(mirroredComponentDict)
