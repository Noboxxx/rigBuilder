from __future__ import division
from maya import cmds
from maya.api import OpenMaya
import math
import os
from .nodeUtils import BlendMatrixCustom, Transform, Plug, Joint


currentDir = os.path.join(*os.path.split(os.path.dirname(os.path.realpath(__file__)))[:-1])
cmds.loadPlugin(os.path.join(currentDir, r'plug-ins\blendMatrixCustomNode.py'))


def jointChainBetweenTwoMatrices(matrixA, matrixB, sections=4, namePattern='joint{index}', compensateScale=False):
    matrices = list()
    for index in range(sections + 1):
        blender = index / sections
        position = [x * (1.0 - blender) + y * blender for x, y in zip(matrixA[12:15], matrixB[12:15])]
        matrix = list(matrixA[0:12]) + position + [1.0]
        matrices.append(matrix)

    return jointChain(matrices, namePattern=namePattern, compensateScale=compensateScale)


def createPoleVector(matrixA, matrixB, matrixC, ikHandle, offset=20.0, ctrlName='poleVector', ctrlSize=1.0):
    positionA = matrixA[12:15]
    positionB = matrixB[12:15]
    positionC = matrixC[12:15]

    midPosition = [x * 0.5 + y * 0.5 for x, y in zip(positionA, positionC)]

    forwardVector = OpenMaya.MVector([x - y for x, y in zip(positionB, midPosition)])
    forwardVector.normalize()

    sideVector = OpenMaya.MVector([x - y for x, y in zip(midPosition, positionA)])
    sideVector.normalize()

    upVector = sideVector ^ forwardVector
    upVector.normalize()

    sideVector = forwardVector ^ upVector
    sideVector.normalize()

    matrix = OpenMaya.MMatrix(
        [
            forwardVector.x, forwardVector.y, forwardVector.z, 0.0,
            upVector.x, upVector.y, upVector.z, 0.0,
            sideVector.x, sideVector.y, sideVector.z, 0.0,
            midPosition[0], midPosition[1], midPosition[2], 1.0
        ]
    )

    offsetMatrix = OpenMaya.MMatrix(
        [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            offset, 0.0, 0.0, 1.0,
        ]
    )

    ctrlBuffer, ctrl = bufferedCtrl(name=ctrlName, size=ctrlSize)
    cmds.xform(ctrlBuffer, matrix=list(offsetMatrix * matrix))

    cmds.poleVectorConstraint(ctrl, ikHandle)

    return ctrlBuffer, ctrl


def jointChain(matrices, namePattern='joint{index}', compensateScale=False):
    joints = list()
    for index, matrix in enumerate(matrices):
        name = namePattern.format(index=index)

        joint = cmds.createNode('joint', name=name)
        cmds.xform(joint, matrix=list(matrix))

        if index > 0:
            cmds.parent(joint, joints[-1])

        cmds.makeIdentity(joint, apply=True, rotate=True)
        cmds.setAttr('{}.segmentScaleCompensate'.format(joint), compensateScale)

        joints.append(joint)
    return joints


def ctrlChain(joints, namePattern='ctrl{index}', color=(255, 255, 0), size=1.0, normal=(1.0, 0.0, 0.0)):
    ctrls = list()
    for index, jnt in enumerate(joints):
        name = namePattern.format(index=index)
        matrix = cmds.xform(jnt, q=True, matrix=True, worldSpace=True)
        ctrlBuffer, ctrl = bufferedCtrl(name=name, color=color, size=size, normal=normal)
        cmds.xform(ctrlBuffer, matrix=matrix)
        matrixConstraint((ctrl, ), jnt)
        if index > 0:
            cmds.parent(ctrlBuffer, ctrls[-1][1])
        ctrls.append((ctrlBuffer, ctrl))
    return ctrls


def bufferedCtrl(name='ctrl#', color=(255, 255, 0), normal=(1.0, 0.0, 0.0), size=1.0):
    ctrl = Controller.create(name=name, color=color, normal=normal, size=size)
    ctrlBuffer = createBuffer(ctrl)
    return ctrlBuffer, ctrl


def createBuffer(obj, bufferSuffix='Bfr'):
    buffer_ = cmds.group(empty=True, name='{}{}'.format(obj, bufferSuffix))
    objMatrix = cmds.xform(obj, q=True, matrix=True, worldSpace=True)
    cmds.xform(buffer_, matrix=objMatrix)

    objParents = cmds.listRelatives(obj, parent=True)

    cmds.parent(obj, buffer_)
    if objParents:
        cmds.parent(buffer_, objParents[0])

    return buffer_


class Controller(object):

    shortType = 'ctl'

    def __init__(self, name):
        self.name = str(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return repr(self.name)

    @classmethod
    def create(cls, name='ctrl#', color=(255, 255, 0), normal=(1.0, 0.0, 0.0), size=1.0):
        if cmds.objExists(name):
            raise RuntimeError('Controller named \"{}\" already exist.'.format(name))
        color = list(color)
        name, = cmds.circle(name=name, constructionHistory=False, radius=size, normal=normal)

        cmds.controller(name)

        for shape in cmds.listRelatives(name, children=True, shapes=True):
            cmds.setAttr('{}.overrideEnabled'.format(shape), True)
            cmds.setAttr('{}.overrideRGBColors'.format(shape), True)

            cmds.setAttr('{}.overrideColorR'.format(shape), color[0] / 255)
            cmds.setAttr('{}.overrideColorG'.format(shape), color[1] / 255)
            cmds.setAttr('{}.overrideColorB'.format(shape), color[2] / 255)

        return cls(name)


# class Color(list):
#
#     red = (255, 0, 0)
#     green = (0, 255, 0)
#     blue = (0, 0, 255)
#     yellow = (255, 255, 0)
#
#     mirrorTable = {
#         red: green,
#         green: red,
#         yellow: None,
#     }
#
#     def __init__(self, r=255, g=255, b=255):
#         r = int(imath.clamp(int(r), 0, 255))
#         g = int(imath.clamp(int(g), 0, 255))
#         b = int(imath.clamp(int(b), 0, 255))
#         super(Color, self).__init__((r, g, b))
#
#     def mirrored(self):
#         return self.mirrorTable.get(tuple(self), None)
#
#     def __add__(self, other):
#         if isinstance(other, Color):
#             return self.__class__(
#                 self[0] + other[0],
#                 self[1] + other[1],
#                 self[2] + other[2],
#             )
#         elif isinstance(other, int) or isinstance(other, float):
#             return self.__class__(
#                 self[0] + other,
#                 self[1] + other,
#                 self[2] + other,
#             )
#         else:
#             raise TypeError('Only int, float and Color can be added to Color')


# class Name(str):
#
#     pattern = r'^[a-z][a-zA-Z0-9]*$'
#
#     def __init__(self, name):
#         name = str(name)
#         if not re.match(self.pattern, name):
#             raise ValueError('Name is not valid -> {}'.format(name))
#         super(Name, self).__init__(name)


# class Side(str):
#     left = 'L'
#     right = 'R'
#     center = 'C'
#
#     mirrorTable = {
#         left: right,
#         right: left,
#         center: None,
#     }
#
#     def __init__(self, side):
#         side = str(side)
#         if side not in self.mirrorTable.keys():
#             raise ValueError('Side not recognized -> {}'.format(side))
#         super(Side, self).__init__(side)
#
#     def mirrored(self):
#         mirroredSide = self.mirrorTable[str(self)]
#         if mirroredSide is None:
#             return None
#         return self.__class__(mirroredSide)


# class Index(int):
#
#     def __init__(self, index):
#         index = int(index)
#         if index < 0:
#             raise ValueError('Index should be positive -> {}'.format(index))
#         super(Index, self).__init__(index)


def distance(pointA, pointB):
    result = 0
    for r in [(b - a)**2 for a, b in zip(pointA, pointB)]:
        result += r
    return abs(math.sqrt(result))


def matrixConstraint(parents, child, translate=True, rotate=True, scale=True, shear=True, maintainOffset=False):
    """

    :param parents: Transforms or Matrix plugs
    :param child: Transform or matrix plug
    :param translate:
    :param rotate:
    :param scale:
    :param shear:
    :param maintainOffset:
    :return:
    """
    child = Plug(child) if '.' in str(child) else Transform(child)

    constraint = BlendMatrixCustom.create('matrixConstraint#')

    for index, parent in enumerate(parents):
        parent = Plug(parent) if '.' in str(parent) else Transform(parent).worldMatrix

        if maintainOffset:
            if isinstance(child, Transform):
                offset = OpenMaya.MMatrix(child.worldMatrix.get()) * OpenMaya.MMatrix(parent.get()).inverse()
            else:
                offset = OpenMaya.MMatrix(child.get()) * OpenMaya.MMatrix(parent.get()).inverse()

            constraint.matrices.index(index).child(constraint.matricesOffsetAttr).set(offset)

        constraint.matrices.index(index).child(constraint.matricesMatrixAttr).connectIn(parent)

    if isinstance(child, Transform):
        constraint.parentInverseMatrix.connectIn(child.parentInverseMatrix)

        if cmds.objectType(child, isAType='joint'):
            constraint.jointOrient.connectIn(Joint(child).jointOrient)

        if translate:
            constraint.translate.connectOut(child.translate)
        if rotate:
            constraint.rotate.connectOut(child.rotate)
        if scale:
            constraint.scale.connectOut(child.scale)
        if shear:
            constraint.shear.connectOut(child.shear)
    else:
        constraint.resultMatrix.connectIn(child)
    return constraint
