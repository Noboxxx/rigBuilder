from maya.api import OpenMaya
from maya import cmds


def toPvLock(namespace, member, side):
    # get
    oldMatrix = cmds.xform('{}ik1_{}_{}0_jnt'.format(namespace, member, side), q=True, translation=True, worldSpace=True)

    # set
    cmds.setAttr('{}ui_{}_{}0_ctl.pvLock'.format(namespace, member, side), 1)
    cmds.xform('{}pv_{}_{}0_ctl'.format(namespace, member, side), translation=oldMatrix, worldSpace=True)
    cmds.setAttr('{}ui_{}_{}0_ctl.offStretchA'.format(namespace, member, side), 0.0)
    cmds.setAttr('{}ui_{}_{}0_ctl.offStretchB'.format(namespace, member, side), 0.0)


def fromPvLock(namespace, member, side, blendColor=''):
    # get
    aPosition = cmds.xform('{}ik0_{}_{}0_jnt'.format(namespace, member, side), q=True, translation=True, worldSpace=True)
    bPosition = cmds.xform('{}ik1_{}_{}0_jnt'.format(namespace, member, side), q=True, translation=True, worldSpace=True)
    cPosition = cmds.xform('{}ik2_{}_{}0_jnt'.format(namespace, member, side), q=True, translation=True, worldSpace=True)

    if not blendColor:
        pvLockStretchA = cmds.getAttr('{}ui_{}_{}0_ctl.pvLockStretchA'.format(namespace, member, side))
        pvLockStretchB = cmds.getAttr('{}ui_{}_{}0_ctl.pvLockStretchB'.format(namespace, member, side))

        autoStretchA = cmds.getAttr('{}ui_{}_{}0_ctl.autoStretchA'.format(namespace, member, side))
        autoStretchB = cmds.getAttr('{}ui_{}_{}0_ctl.autoStretchB'.format(namespace, member, side))
    else:
        pvLockStretchA = cmds.getAttr('{}{}.color1R'.format(namespace, blendColor))
        pvLockStretchB = cmds.getAttr('{}{}.color1G'.format(namespace, blendColor))

        autoStretchA = cmds.getAttr('{}{}.color2R'.format(namespace, blendColor))
        autoStretchB = cmds.getAttr('{}{}.color2G'.format(namespace, blendColor))

    diffA = pvLockStretchA - autoStretchA
    diffB = pvLockStretchB - autoStretchB

    # calculate
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

    # set
    cmds.xform('{}pv_{}_{}0_ctl'.format(namespace, member, side), matrix=matrix, worldSpace=True)
    cmds.xform('{}pv_{}_{}0_ctl'.format(namespace, member, side), scale=(1.0, 1.0, 1.0))

    cmds.setAttr('{}ui_{}_{}0_ctl.pvLock'.format(namespace, member, side), 0)
    cmds.setAttr('{}ui_{}_{}0_ctl.offStretchA'.format(namespace, member, side), diffA)
    cmds.setAttr('{}ui_{}_{}0_ctl.offStretchB'.format(namespace, member, side), diffB)


def snapPvLock(namespace, member, side, blendColor=''):
    if namespace:
        namespace += ':'

    if cmds.getAttr('{}ui_{}_{}0_ctl.pvLock'.format(namespace, member, side)):
        fromPvLock(namespace, member, side, blendColor=blendColor)
    else:
        toPvLock(namespace, member, side)
