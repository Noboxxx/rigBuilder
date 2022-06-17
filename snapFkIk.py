import math
from maya.api import OpenMaya
from maya import cmds


def distance(a, b):
    result = 0
    for r in [(x - y)**2 for y, x in zip(a, b)]:
        result += r
    return abs(math.sqrt(result))


def blendValue(a, b, blender):  # type: (float, float, float) -> float
    return a * (1 - blender) + b * blender


def getPvMatrix(aPosition, bPosition, cPosition):
    sideVector = OpenMaya.MVector([h - t for h, t in zip(cPosition, aPosition)])
    rawForwardVector = OpenMaya.MVector([h - t for h, t in zip(bPosition, aPosition)])
    upVector = sideVector ^ rawForwardVector
    forwardVector = sideVector ^ upVector

    forwardVector.normalize()
    sideVector.normalize()
    upVector.normalize()

    matrix = OpenMaya.MMatrix(
        (
            forwardVector.x, forwardVector.y, forwardVector.z, 0.0,
            sideVector.x, sideVector.y, sideVector.z, 0.0,
            upVector.x, upVector.y, upVector.z, 0.0,
            bPosition[0], bPosition[1], bPosition[2], 1.0
        )
    )
    return matrix


def fkToIk(namespace, member, side, blendColor=''):
    # get
    scaleReferent = OpenMaya.MMatrix(cmds.xform('{}main_{}_{}0_ctl'.format(namespace, member, side), q=True, matrix=True, worldSpace=True)).inverse()

    aWorldMatrix = OpenMaya.MMatrix(cmds.xform('{}fk0_{}_{}0_ctl'.format(namespace, member, side), q=True, matrix=True, worldSpace=True))
    bWorldMatrix = OpenMaya.MMatrix(cmds.xform('{}fk1_{}_{}0_ctl'.format(namespace, member, side), q=True, matrix=True, worldSpace=True))
    cWorldMatrix = OpenMaya.MMatrix(cmds.xform('{}fk2_{}_{}0_ctl'.format(namespace, member, side), q=True, matrix=True, worldSpace=True))

    aMatrix = aWorldMatrix * scaleReferent
    bMatrix = bWorldMatrix * scaleReferent
    cMatrix = cWorldMatrix * scaleReferent

    stretchA = distance(list(aMatrix)[12:15], list(bMatrix)[12:15])
    stretchB = distance(list(bMatrix)[12:15], list(cMatrix)[12:15])

    pvLock = cmds.getAttr('{}ui_{}_{}0_ctl.pvLock'.format(namespace, member, side))

    stretchA = blendValue(stretchA, 0, pvLock)
    stretchB = blendValue(stretchB, 0, pvLock)

    pvMatrix = getPvMatrix(list(aWorldMatrix)[12:15], list(bWorldMatrix)[12:15], list(cWorldMatrix)[12:15])

    # set
    cmds.xform('{}pv_{}_{}0_ctl'.format(namespace, member, side), matrix=pvMatrix, worldSpace=True)
    cmds.xform('{}pv_{}_{}0_ctl'.format(namespace, member, side), scale=(1, 1, 1))

    cmds.xform('{}ik_{}_{}0_ctl'.format(namespace, member, side), matrix=cWorldMatrix, worldSpace=True)
    cmds.xform('{}ik_{}_{}0_ctl'.format(namespace, member, side), scale=(1, 1, 1))

    if not blendColor:
        autoStretchA = cmds.getAttr('{}ui_{}_{}0_ctl.autoStretchA'.format(namespace, member, side))
        autoStretchB = cmds.getAttr('{}ui_{}_{}0_ctl.autoStretchB'.format(namespace, member, side))
    else:
        autoStretchA = cmds.getAttr('{}{}.color2R'.format(namespace, blendColor))
        autoStretchB = cmds.getAttr('{}{}.color2G'.format(namespace, blendColor))

    cmds.setAttr('{}ui_{}_{}0_ctl.offStretchA'.format(namespace, member, side), stretchA - autoStretchA)
    cmds.setAttr('{}ui_{}_{}0_ctl.offStretchB'.format(namespace, member, side), stretchB - autoStretchB)

    # switch
    cmds.setAttr('{}ui_{}_{}0_ctl.switchFkIk'.format(namespace, member, side), 1)


def ikToFk(namespace, member, side):
    # get
    ikJoints = ('{}ik0_{}_{}0_jnt'.format(namespace, member, side), '{}ik1_{}_{}0_jnt'.format(namespace, member, side), '{}ik2_{}_{}0_jnt'.format(namespace, member, side))
    fkCtrls = ('{}fk0_{}_{}0_ctl'.format(namespace, member, side), '{}fk1_{}_{}0_ctl'.format(namespace, member, side), '{}fk2_{}_{}0_ctl'.format(namespace, member, side))
    ikMatrices = [cmds.xform(j, q=True, matrix=True, worldSpace=True) for j in ikJoints]

    # set
    [cmds.xform(c, matrix=m, worldSpace=True) for c, m in zip(fkCtrls, ikMatrices)]

    # switch
    cmds.setAttr('{}ui_{}_{}0_ctl.switchFkIk'.format(namespace, member, side), 0)


def snapFkIk(namespace, member, side, blendColor=''):
    if namespace:
        namespace += ':'

    if cmds.getAttr('{}ui_{}_{}0_ctl.switchFkIk'.format(namespace, member, side)):
        ikToFk(namespace, member, side)
    else:
        fkToIk(namespace, member, side, blendColor=blendColor)
