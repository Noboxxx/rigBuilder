import math
from maya import cmds


def controller(name, normal=(1, 0, 0), size=1.0, matrix=None, color=(0, 255, 255), ctrlParent=None, visParent=None):
    bfr = cmds.group(empty=True, name='{}Bfr'.format(name))
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
