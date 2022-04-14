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
            (2.98023e-08, 0, 1),
            (0.309017, 0, 0.951057),
            (0.587785, 0, 0.809017),
            (0.809017, 0, 0.587785),
            (0.951057, 0, 0.309017),
            (1, 0, 0),
            (0.951057, 0, -0.309017),
            (0.809017, 0, -0.587785),
            (0.587785, 0, -0.809017),
            (0.309017, 0, -0.951057),
            (0, 0, -1),
            (-0.309017, 0, -0.951057),
            (-0.587786, 0, -0.809017),
            (-0.809018, 0, -0.587786),
            (-0.951057, 0, -0.309017),
            (-1, 0, 0),
            (-0.951057, 0, 0.309017),
            (-0.809017, 0, 0.587785),
            (-0.587785, 0, 0.809017),
            (-0.309017, 0, 0.951057),
            (2.98023e-08, 0, 1),
        )
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
    },
    'fourArrows': {
        'points': (
            (0.0, 1.2016340415869203e-31, -1.105821775523436),
            (-0.3124633170867661, 1.2016340415869203e-31, -0.6371267999462347),
            (-0.15623165849043252, 1.2016340415869203e-31, -0.6371267999462347),
            (-0.15623165849043252, 1.2016340415869203e-31, -0.21814189742880918),
            (-0.5752165610078581, 1.2016340415869203e-31, -0.21814189742880918),
            (-0.5752165610078581, 1.2016340415869203e-31, -0.37437355602514505),
            (-1.0439115365850573, 1.2016340415869203e-31, -0.06191023893838002),
            (-0.5752165610078581, 1.2016340415869203e-31, 0.25055307814838784),
            (-0.5752165610078581, 1.2016340415869203e-31, 0.09432141955205486),
            (-0.15623165849043252, 1.2016340415869203e-31, 0.09432141955205486),
            (-0.15623165849043252, 1.2016340415869203e-31, 0.513306322069479),
            (-0.3124633170867661, 1.2016340415869203e-31, 0.513306322069479),
            (0.0, 1.2016340415869203e-31, 0.9820012976466758),
            (0.3124633170867661, 1.2016340415869203e-31, 0.513306322069479),
            (0.15623165849043252, 1.2016340415869203e-31, 0.513306322069479),
            (0.15623165849043252, 1.2016340415869203e-31, 0.09432141955205486),
            (0.5752165610078581, 1.2016340415869203e-31, 0.09432141955205486),
            (0.5752165610078581, 1.2016340415869203e-31, 0.25055307814838784),
            (1.0439115365850573, 1.2016340415869203e-31, -0.06191023893838002),
            (0.5752165610078581, 1.2016340415869203e-31, -0.37437355602514505),
            (0.5752165610078581, 1.2016340415869203e-31, -0.21814189742880918),
            (0.15623165849043252, 1.2016340415869203e-31, -0.21814189742880918),
            (0.15623165849043252, 1.2016340415869203e-31, -0.6371267999462347),
            (0.3124633170867661, 1.2016340415869203e-31, -0.6371267999462347),
            (0.0, 1.2016340415869203e-31, -1.105821775523436)
        )
    },
    'square': {
        'points': (
            (-1.0, 0.0, 1.0),

            (-1.0, 0.0, -1.0),
            (1.0, 0.0, -1.0),
            (1.0, 0.0, 1.0),

            (-1.0, 0.0, 1.0),
        )
    }
}


def controller(name, normal=(1, 0, 0), size=1.0, matrix=None, color=(255, 255, 0), ctrlParent=None, visParent=None,
               shape=None, lockAttrs=None):
    if lockAttrs is None:
        lockAttrs = list()

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
    ctrl = cmds.curve(name=name, d=1, p=points, k=shapeInfo.get('knots', range(len(points))))

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

    for attr in lockAttrs:
        cmds.setAttr('{}.{}'.format(ctrl, attr), lock=True, keyable=False)

    return bfr, ctrl


def distance(a, b):
    result = 0
    for r in [(x - y)**2 for y, x in zip(a, b)]:
        result += r
    return abs(math.sqrt(result))


def scaleController(ctrl, size):
    for shape in cmds.listRelatives(ctrl, shapes=True, type='nurbsCurve'):
        cvCount = cmds.getAttr('{}.spans'.format(shape))

        if cmds.getAttr('{}.form'.format(shape)) != 2:
            cvCount += 1

        for index in range(cvCount):
            cvPlug = '{}.cv[{}]'.format(shape, index)
            pos = cmds.xform(cvPlug, q=True, translation=True)
            newPos = [v * size for v in pos]
            cmds.xform(cvPlug, translation=newPos)