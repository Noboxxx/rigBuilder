import math
from maya import cmds


def controller(name, normal=(1, 0, 0), size=1.0, matrix=None, color=(0, 255, 255), ctrlParent=None, visParent=None,
               shape='circle'):
    bfr = cmds.group(empty=True, name='{}Bfr'.format(name))

    if shape == 'circle':
        ctrl, = cmds.circle(ch=False, name=name, normal=normal, radius=size)
    elif shape == 'cube':
        points = (
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
        )
        pointsScaled = [[x * size for x in p] for p in points]
        ctrl = cmds.curve(d=1, p=pointsScaled, k=range(16))
    elif shape == 'sphere':
        # curve -d 1 -p -1 0 0 -p -0.707107 0 0.707107 -p 0 0 1 -p 0.707107 0 0.707107 -p 1 0 0 -p 0.707107 0 -0.707107 -p 0 0 -1 -p -0.707107 0 -0.707107 -p -1 0 0 -p -0.923879 0.382683 0 -p -0.707107 0.707107 0 -p -0.382683 0.92388 0 -p 0 1 0 -p 0 0.92388 -0.382683 -p 0 0.707107 -0.707107 -p 0 0.382683 -0.923879 -p 0 0 -1 -p 0 -0.382683 -0.923879 -p 0 -0.707107 -0.707107 -p 0 -0.92388 -0.382683 -p 0 -1 0 -p 0.382683 -0.92388 0 -p 0.707107 -0.707107 0 -p 0.92388 -0.382683 0 -p 1 0 0 -p 0.92388 0.382683 0 -p 0.707107 0.707107 0 -p 0.382683 0.92388 0 -p 0 1 0 -p 0 0.92388 0.382683 -p 0 0.707107 0.707107 -p 0 0.382683 0.923879 -p 0 0 1 -p 0 -0.382683 0.923879 -p 0 -0.707107 0.707107 -p 0 -0.92388 0.382683 -p 0 -1 0 -p -0.382683 -0.92388 0 -p -0.707107 -0.707107 0 -p -0.923879 -0.382683 0 -p -1 0 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 -k 25 -k 26 -k 27 -k 28 -k 29 -k 30 -k 31 -k 32 -k 33 -k 34 -k 35 -k 36 -k 37 -k 38 -k 39 -k 40 ;
        points = (
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
        )
        pointsScaled = [[x * size for x in p] for p in points]
        ctrl = cmds.curve(d=1, p=pointsScaled, k=range(41))
    else:
        ctrl, = cmds.circle(ch=False, name=name, normal=normal, radius=size)

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
