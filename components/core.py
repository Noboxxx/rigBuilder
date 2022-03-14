import re

from maya import cmds
from rigBuilder.types import Side, Color, UnsignedInt, UnsignedFloat, Matrix
from rigBuilder.core import Data
from collections import OrderedDict


class ConnectionPlugArray(list):

    def __init__(self, seq=None):  # type: (list or tuple) -> None
        attributes = [ConnectionPlug(i) for i in seq] if seq is not None else list()
        super(ConnectionPlugArray, self).__init__(attributes)


class ConnectionPlug(list):

    def __init__(self, seq=None):  # type: (List[str, str, int]) -> None
        if seq is None:
            seq = ['', '', 0]

        if len(seq) != 3:
            raise ValueError('Expect 3 values in the given sequence. Got {}'.format(len(seq)))

        key = str(seq[0])
        attribute = str(seq[1])
        index = int(seq[2])

        super(ConnectionPlug, self).__init__((key, attribute, index))

    def get(self, componentDict):
        component = self.getComponent(componentDict)

        if self[1] not in dir(component):
            return None

        attribute = getattr(component, self[1])

        try:
            return attribute[self[2]]
        except IndexError:
            return None

    def getComponent(self, componentDict):
        if self[0] not in componentDict:
            return None

        return componentDict[self[0]]

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

    def __init__(self, sources=None, destination=None, bilateral=False, translate=True, rotate=True, scale=True, shear=True, maintainOffset=True):
        # type: (List[list], list, bool, bool, bool, bool, bool, bool) -> None
        super(Connection, self).__init__()

        self.sources = ConnectionPlugArray(sources) if sources is not None else ConnectionPlugArray()
        self.destination = ConnectionPlug(destination) if destination is not None else ConnectionPlug()
        self.bilateral = bilateral

        self.translate = bool(translate)
        self.rotate = bool(rotate)
        self.scale = bool(scale)
        self.shear = bool(shear)
        self.maintainOffset = bool(maintainOffset)

    def build(self, componentDict):
        from rigBuilder.components.utils import matrixConstraint

        sources = [p.get(componentDict) for p in self.sources]
        destination = self.destination.get(componentDict)

        interface = self.destination.getComponent(componentDict).interfaces[0]

        attrs = '_'.join([attr for attr, state in zip(
            ('t', 'r', 's', 'sh'),
            (self.translate, self.rotate, self.scale, self.shear),
        ) if state])

        attr = '{}_space_{}'.format(destination, attrs)
        plug = '{}.{}'.format(interface, attr)
        cmds.addAttr(
            interface,
            longName=attr,
            attributeType='enum',
            enumName=':'.join(map(str, sources)),
            keyable=True,
        )
        constr = matrixConstraint(sources, destination, self.translate, self.rotate, self.scale, self.shear, self.maintainOffset)
        cmds.connectAttr(
            plug, '{}.blender'.format(constr)
        )


class Storage(list):
    pass


class Plug(Storage):
    pass


class Output(Plug):
    pass


class Input(Plug):
    pass


class Component(Data):

    def __init__(self, name='untitled', side='C', index=0, color=(255, 255, 0), size=1.0, bilateral=False):
        super(Component, self).__init__()

        self.name = str(name)
        self.side = Side(side)
        self.index = UnsignedInt(index)
        self.color = Color(color)
        self.size = UnsignedFloat(size)
        self.bilateral = bool(bilateral)

        self.interfaces = Storage()
        self.inputs = Input()
        self.outputs = Output()
        self.children = list()

        self.controllers = Storage()
        self.influencers = Storage()

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

        for attr, storage in self.getStorageDict().items():
            cmds.addAttr(str(self), longName=attr, attributeType='message', multi=True)
            for index, obj in enumerate(storage):
                node = obj.split('.')[0] if '.' in obj else obj

                objAttr = 'receiver'
                objPlug = '{}.{}'.format(node, objAttr)
                if not cmds.objExists(objPlug):
                    cmds.addAttr(node, longName=objAttr, attributeType='message', multi=True, indexMatters=False)

                indexedPlug = '{}.{}[{}]'.format(self, attr, index)
                cmds.connectAttr(indexedPlug, objPlug, nextAvailable=True)

    def getStorageDict(self):
        d = dict()
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, Storage):
                d[attr] = value
        return d

    def createGuides(self, name):
        pass


class ComponentBuilder(Data):

    def __init__(self, componentDict=None, connectionDict=None):
        # type: (dict[str: Component], dict[str:Connection], GuideDict) -> None
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
            if copiedComponent.bilateral:
                mirrorComponent = copiedComponent.mirrored()
                mirrorComponent.build()

                cmds.parent(str(mirrorComponent), folder)

            mirroredComponentDict[key] = mirrorComponent or copiedComponent
            componentDict[key] = copiedComponent

        for key, connection in self.connectionDict.items():
            connection.copy().build(componentDict)

            if connection.bilateral:
                connection.build(mirroredComponentDict)


class Guide(str):

    def __init__(self, name):
        super(Guide, self).__init__(name)

        self._mirror = False

    def mirror(self):
        self._mirror = not self._mirror

    def mirrored(self):
        guide = self.__class__(self)
        guide.mirror()
        return guide

    @property
    def matrix(self):
        if not cmds.objExists(self):
            raise RuntimeError('Guide named \'{}\' does not exist.'.format(self))
        matrix = Matrix(cmds.xform(self, q=True, matrix=True, worldSpace=True))
        if self._mirror:
            matrix.mirror()
        return matrix.normalized()

    @classmethod
    def create(cls, name):
        if cmds.objExists(name):
            pattern = re.compile(r'(^[A-Za-z0-9_]*[A-Za-z_]+)(\d*$)')
            matches = pattern.findall(name)

            if not matches:
                raise ValueError('Key \'{}\' is not valid'.format(name))

            name, index = matches[0]
            index = int(index) if index.isdigit() else 0
            index += 1
            return cls.create('{}{}'.format(name, index))

        lct, = cmds.spaceLocator(name=name)
        return cls(lct)


class GuideArray(list):

    def __init__(self, seq=None):
        seq = [Guide(i) for i in seq] if seq is not None else list()
        super(GuideArray, self).__init__(seq)

    def mirror(self):
        for index, guide in enumerate(self):
            self[index] = guide.mirrored()

    def mirrored(self):
        copy = self.__class__(self)
        copy.mirror()
        return copy


class GuideDict(OrderedDict):

    def build(self):
        grp = cmds.group(empty=True, name='guides')

        for name, guide in self.items():
            guide.build(name)

        for name, guide in self.items():
            if cmds.objExists(guide.parent):
                cmds.parent(guide, guide.parent)
            else:
                cmds.parent(guide, grp)

    def mirrored(self):
        mirroredGuideDict = OrderedDict()
        for name, guide in self.items():
            mirroredGuideDict[name] = guide.mirrored()
        return mirroredGuideDict

    @classmethod
    def create(cls, grp):
        guideDict = cls()
        for transform in cmds.listRelatives(grp, children=True, type='transform'):
            guide = Guide.create(transform)
            guideDict[transform] = guide

        return guideDict
