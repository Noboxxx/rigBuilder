import math
from maya import cmds
from math import cos, sin


def rotatePoints(points, axis, angle):

    if axis == 'x':
        a, b, c = 0, 1, 2
    elif axis == 'y':
        a, b, c = 1, 0, 2
    elif axis == 'z':
        a, b, c = 2, 0, 1
    else:
        raise ValueError('Axis not right')

    newPoints = list()
    for p in points:
        newB = p[b] * cos(angle) - p[c] * sin(angle)
        newC = p[c] * cos(angle) + p[b] * sin(angle)
        newPoints.append((p[a], newB, newC))

    return newPoints


shapes = {
    'circle': {
        'points': (
            (0, 0, 1),
            (-0.707107, 0, 0.707107),
            (-1, 0, 0),
            (-0.707107, 0, -0.707107),
            (0, 0, -1),
            (0.707107, 0, -0.707107),
            (1, 0, 0),
            (0.707107, 0, 0.707107),
            (0, 0, 1),
        ),
        'knots': range(9)
        },
    'cube': {
        'points': (
            (-0.75, 0.75, 0.75),
            (0.75, 0.75, 0.75),
            (0.75, -0.75, 0.75),
            (0.75, -0.75, -0.75),
            (0.75, 0.75, -0.75),
            (-0.75, 0.75, -0.75),
            (-0.75, -0.75, -0.75),
            (-0.75, -0.75, 0.75),
            (-0.75, 0.75, 0.75),
            (-0.75, 0.75, -0.75),
            (-0.75, -0.75, -0.75),
            (0.75, -0.75, -0.75),
            (0.75, 0.75, -0.75),
            (0.75, 0.75, 0.75),
            (0.75, -0.75, 0.75),
            (-0.75, -0.75, 0.75),
        ),
        'knots': range(16)
    },
    'sphere': {
        'points': (
            (-0.707107, 0, 0.707107),
            (0, 0, 1),
            (0.707107, 0, 0.707107),
            (1, 0, 0),
            (0.707107, 0, -0.707107),
            (0, 0, -1),
            (-0.707107, 0, -0.707107),
            (-1, 0, 0),
            (-0.923879, 0.382683, 0),
            (-0.707107, 0.707107, 0),
            (-0.382683, 0.92388, 0),
            (0, 1, 0),
            (0, 0.92388, -0.382683),
            (0, 0.707107, -0.707107),
            (0, 0.382683, -0.923879),
            (0, 0, -1),
            (0, -0.382683, -0.923879),
            (0, -0.707107, -0.707107),
            (0, -0.92388, -0.382683),
            (0, -1, 0),
            (0.382683, -0.92388, 0),
            (0.707107, -0.707107, 0),
            (0.92388, -0.382683, 0),
            (1, 0, 0),
            (0.92388, 0.382683, 0),
            (0.707107, 0.707107, 0),
            (0.382683, 0.92388, 0),
            (0, 1, 0),
            (0, 0.92388, 0.382683),
            (0, 0.707107, 0.707107),
            (0, 0.382683, 0.923879),
            (0, 0, 1),
            (0, -0.382683, 0.923879),
            (0, -0.707107, 0.707107),
            (0, -0.92388, 0.382683),
            (0, -1, 0),
            (-0.382683, -0.92388, 0),
            (-0.707107, -0.707107, 0),
            (-0.923879, -0.382683, 0),
            (-1, 0, 0),
            (-0.707107, 0, 0.707107),
        ),
        'knots': range(41)
    },
    'diamond': {
        'points': (
            (0, 0.75, 0),
            (0.75, 0, 0),
            (0, 0, 0.75),
            (0, 0.75, 0),
            (-0.75, 0, 0),
            (0, 0, 0.75),
            (0, -0.75, 0),
            (-0.75, 0, 0),
            (0, 0, -0.75),
            (0, 0.75, 0),
            (0.75, 0, 0),
            (0, 0, -0.75),
            (0, -0.75, 0),
            (0.75, 0, 0),
        ),
        'knots': range(14)
    },
    'ring': {
        'points': (
            (1.397655, 0, 3.57628e-07),
            (0.92388, 0, 0.382683),
            (0.707107, 0, 0.707107),
            (0.382683, 0, 0.92388),
            (-1.49012e-07, 0, 1),
            (-0.382684, 0, 0.923879),
            (-0.707107, 0, 0.707107),
            (-0.92388, 0, 0.382683),
            (-1, 0, 0),
            (-0.923879, 0, -0.382684),
            (-0.707106, 0, -0.707107),
            (-0.382683, 0, -0.92388),
            (5.06639e-07, 0, -1),
            (0.382684, 0, -0.923879),
            (0.707107, 0, -0.707106),
            (0.92388, 0, -0.382683),
            (1.397655, 0, 3.57628e-07),
        ),
        'knots': range(17)
    }
}


def controller(name, normal=(1, 0, 0), size=1.0, matrix=None, color=(0, 255, 255), ctrlParent=None, visParent=None,
               shape=None):
    bfr = cmds.group(empty=True, name='{}Bfr'.format(name))

    shapeInfo = shapes.get(shape, shapes['circle'])
    points = shapeInfo['points']

    if normal == (1, 0, 0):
        points = rotatePoints(points, 'y', 1.5708)
    elif normal == (0, 1, 0):
        pass
    elif normal == (0, 0, 1):
        points = rotatePoints(points, 'x', 1.5708)
    else:
        raise ValueError('Not valid normal')

    points = [[x * size for x in p] for p in points]
    ctrl = cmds.curve(name=name, d=1, p=points, k=shapeInfo['knots'])

    cmds.parent(ctrl, bfr)

    if matrix:
        cmds.xform(bfr, matrix=list(matrix))

    for shape in cmds.listRelatives(ctrl, children=True, shapes=True):
        cmds.setAttr('{}.overrideEnabled'.format(shape), True)
        cmds.setAttr('{}.overrideRGBColors'.format(shape), True)

        cmds.setAttr('{}.overrideColorR'.format(shape), color[0] / 255.0)
        cmds.setAttr('{}.overrideColorG'.format(shape), color[1] / 255.0)
        cmds.setAttr('{}.overrideColorB'.format(shape), color[2] / 255.0)

    cmds.controller(ctrl)
    if ctrlParent:
        cmds.controller(ctrl, ctrlParent, p=True)

    if visParent:
        cmds.connectAttr(visParent, '{}.v'.format(bfr))

    cmds.setAttr('{}.v'.format(ctrl), lock=True, keyable=False)

    return bfr, ctrl


def distance(a, b):
    result = 0
    for r in [(x - y)**2 for y, x in zip(a, b)]:
        result += r
    return abs(math.sqrt(result))
