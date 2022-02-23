from maya import cmds
from rigBuilder.types import Side, Color, UnsignedInt, UnsignedFloat, Matrix
from rigBuilder.core import Data


class Attributes(list):

    def __init__(self, attributes=None):  # type: (list or tuple) -> None
        attributes = [Attribute(*i) for i in attributes] if attributes is not None else list()
        super(Attributes, self).__init__(attributes)


class Attribute(list):

    def __init__(self, key='', attribute='', index=0):
        # type: (str, str, int) -> None
        super(Attribute, self).__init__((key, attribute, index))

    def get(self, componentDict):
        if self[0] not in componentDict:
            return None

        component = componentDict[self[0]]

        if self[1] not in dir(component):
            return None

        attribute = getattr(component, self[1])

        try:
            return attribute[self[2]]
        except IndexError:
            return None

    @property
    def key(self):
        return self[0]

    @property
    def attribute(self):
        return self[1]

    @property
    def index(self):
        return self[2]


class Connection(Data):

    def __init__(self, sources=None, destination=None, bilateral=False, translate=True, rotate=True, scale=True, shear=True):
        # type: (List[list], list, bool, bool, bool, bool, bool) -> None
        super(Connection, self).__init__()

        self.sources = Attributes(sources) if sources is not None else Attributes()
        self.destination = Attribute(*destination) if destination is not None else Attribute()
        self.bilateral = bilateral

        self.translate = translate
        self.rotate = rotate
        self.scale = scale
        self.shear = shear

    def build(self, componentDict):
        print 'build', [p.get(componentDict) for p in self.sources], self.destination.get(componentDict)


class Plug(list):
    pass


class Output(Plug):
    pass


class Input(Plug):
    pass


class Guide(Matrix):

    def build(self, name):
        guidesFolder = 'guides'
        if not cmds.objExists(guidesFolder):
            cmds.group(empty=True, name=guidesFolder)

        lct, = cmds.spaceLocator(name='{}_guide'.format(name))
        cmds.parent(lct, guidesFolder)
        cmds.xform(lct, matrix=list(self))


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

        self.controllers = list()
        self.influencers = list()

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

    def createGuides(self):
        pass


class ComponentBuilder(Data):

    def __init__(self, componentDict=None, connectionDict=None):
        # type: (dict[str: Component], dict[str:Connection]) -> None
        super(ComponentBuilder, self).__init__()

        self.componentDict = componentDict if componentDict is not None else dict()
        self.connectionDict = connectionDict if connectionDict is not None else dict()

    def build(self):

        folder = cmds.group(empty=True, name='rig')

        componentDict = dict()
        mirroredComponentDict = dict()
        for key, component in self.componentDict.items():
            copiedComponent = component.copy()
            copiedComponent.build()

            cmds.parent(str(copiedComponent), folder)

            mirrorComponent = None
            if component.bilateral:
                mirrorComponent = component.mirrored()
                mirrorComponent.build()

                cmds.parent(str(mirrorComponent), folder)

            mirroredComponentDict[key] = mirrorComponent or component
            componentDict[key] = component

        for key, connection in self.connectionDict:
            connection.copy().build(componentDict)

            if connection.bilateral:
                connection.build(mirroredComponentDict)
