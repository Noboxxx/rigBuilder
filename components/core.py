import re

from maya import cmds
from rigBuilder.types import Side, Color, UnsignedInt, Matrix, Vector, StringArray
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

    def __init__(self, attributeName='follow', sources=None, destination=None,  bilateral=False, translate=True, rotate=True, scale=True, shear=True, maintainOffset=True, **kwargs):
        super(Connection, self).__init__()

        self.sources = ConnectionPlugArray(sources) if sources is not None else ConnectionPlugArray()
        self.destination = ConnectionPlug(destination) if destination is not None else ConnectionPlug()
        self.bilateral = bilateral

        self.attributeName = str(attributeName)
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

        plug = '{}.{}'.format(interface, self.attributeName)
        if cmds.objExists(plug):
            raise RuntimeError('Attribute already exists: {}'.format(repr(plug)))
        cmds.addAttr(
            interface,
            longName=self.attributeName,
            attributeType='enum',
            enumName=':'.join(x.key for x in self.sources),
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

    def __init__(self, name='untitled', side='C', index=0, color=(255, 255, 0), bilateral=False, **kwargs):
        super(Component, self).__init__()

        self.name = str(name)
        self.side = Side(side)
        self.index = UnsignedInt(index)
        self.color = Color(color)
        self.bilateral = bool(bilateral)

        self.interfaces = Storage()
        self.inputs = Input()
        self.outputs = Output()
        self.children = list()

        self.controllers = Storage()
        self.influencers = Storage()

        for k, v in kwargs.items():
            print('Unknown kwargs: {} -> {} for {}'.format(repr(k), repr(v), repr(self)))

    def __repr__(self):
        return repr(str(self))

    def __str__(self):
        return '{}_{}{}'.format(self.name, self.side, self.index)

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

    def buildControlSet(self):
        cmds.select(self.controllers)
        return cmds.sets(name='set_{}'.format(self))

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

    def __init__(self, componentDict=None, connectionDict=None, disabledComponents=None, disabledConnections=None):
        # type: (dict[str: Component], dict[str:Connection], List[str], List[str]) -> None
        super(ComponentBuilder, self).__init__()

        self.disabledConnections = disabledConnections if disabledConnections is not None else list()
        self.disabledComponents = disabledComponents if disabledComponents is not None else list()
        self.componentDict = componentDict if componentDict is not None else dict()
        self.connectionDict = connectionDict if connectionDict is not None else dict()

    def build(self, controlSet=False):
        folder = cmds.group(empty=True, name='setup')

        componentDict = dict()
        mirroredComponentDict = dict()
        for key, component in self.componentDict.items():
            if key in self.disabledComponents:
                continue
            copiedComponent = component.copy()
            copiedComponent.build()

            sets = list()
            if controlSet:
                sets.append(copiedComponent.buildControlSet())

            cmds.parent(str(copiedComponent), folder)

            mirrorComponent = None
            if copiedComponent.bilateral:
                mirrorComponent = copiedComponent.mirrored()
                mirrorComponent.build()

                if controlSet:
                    sets.append(mirrorComponent.buildControlSet())

                cmds.parent(str(mirrorComponent), folder)

            mirroredComponentDict[key] = mirrorComponent or copiedComponent
            componentDict[key] = copiedComponent

            if sets:
                controlSetNode = 'ControlSet'
                if not cmds.objExists(controlSetNode):
                    cmds.select(clear=True)
                    cmds.sets(name=controlSetNode)
                if len(sets) == 1:
                    cmds.sets(sets[0], addElement=controlSetNode)
                else:
                    cmds.select(clear=True)
                    grpSet = cmds.sets(name='set_{}'.format(key))
                    cmds.sets(grpSet, addElement=controlSetNode)
                    for s in sets:
                        cmds.sets(s, addElement=grpSet)

        for key, connection in self.connectionDict.items():
            if key in self.disabledConnections:
                continue
            connection.copy().build(componentDict)

            if connection.bilateral:
                connection.build(mirroredComponentDict)


class Guide(str):

    xArrowShape = (
        (0, 0, 0),
        (1.5, 0, 0),
    )
    xCircleShape = (
        (0, 2.98023e-08, 1),
        (0, 0.309017, 0.951057),
        (0, 0.587785, 0.809017),
        (0, 0.809017, 0.587785),
        (0, 0.951057, 0.309017),
        (0, 1, 0),
        (0, 0.951057, -0.309017),
        (0, 0.809017, -0.587785),
        (0, 0.587785, -0.809017),
        (0, 0.309017, -0.951057),
        (0, 0, -1),
        (0, -0.309017, -0.951057),
        (0, -0.587786, -0.809017),
        (0, -0.809018, -0.587786),
        (0, -0.951057, -0.309017),
        (0, -1, 0),
        (0, -0.951057, 0.309017),
        (0, -0.809017, 0.587785),
        (0, -0.587785, 0.809017),
        (0, -0.309017, 0.951057),
        (0, 2.98023e-08, 1),
    )

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
        return self._matrix.normalized()

    @property
    def _matrix(self):
        if not cmds.objExists(self):
            raise RuntimeError('Guide named \'{}\' does not exist.'.format(self))
        matrix = Matrix(cmds.xform(self, q=True, matrix=True, worldSpace=True))
        if self._mirror:
            matrix.mirror()
        return matrix

    @property
    def size(self):
        return Vector(self._matrix[4:7]).magnitude() * 1.2

    @classmethod
    def threeArrows(cls, name='guide#'):
        colors = (255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 100, 100)
        xArrowShape = (
            (0, 0, 0),
            (.5, 0, 0),
        )
        yArrowShape = (
            (0, 0, 0),
            (0, 1.5, 0),
        )
        zArrowShape = (
            (0, 0, 0),
            (0, 0, 1.5),
        )

        shapes = xArrowShape, yArrowShape, zArrowShape, cls.xCircleShape

        trs = cmds.group(empty=True, name=name)

        for color, shape in zip(colors, shapes):
            guide = cmds.curve(point=shape, degree=1)
            for s in cmds.listRelatives(guide, type='nurbsCurve'):

                cmds.setAttr('{}.overrideEnabled'.format(s), True)
                cmds.setAttr('{}.overrideRGBColors'.format(s), True)

                cmds.setAttr('{}.overrideColorR'.format(s), color[0] / 255.0)
                cmds.setAttr('{}.overrideColorG'.format(s), color[1] / 255.0)
                cmds.setAttr('{}.overrideColorB'.format(s), color[2] / 255.0)

                cmds.parent(s, trs, s=True, r=True)

            cmds.delete(guide)

        return trs

    @classmethod
    def create(cls, name):
        guidesGrp = 'guides'
        if not cmds.objExists(guidesGrp):
            cmds.group(empty=True, name=guidesGrp)

        if cmds.objExists(name):
            pattern = re.compile(r'(^[A-Za-z0-9_]*[A-Za-z_]+)(\d*$)')
            matches = pattern.findall(name)

            if not matches:
                raise ValueError('Key \'{}\' is not valid'.format(name))

            name, index = matches[0]
            index = int(index) if index.isdigit() else 0
            index += 1
            return cls.create('{}{}'.format(name, index))

        g = cls.threeArrows(name=name)
        cmds.parent(g, guidesGrp)
        return cls(g)


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
