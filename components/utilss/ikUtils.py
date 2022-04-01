from maya import cmds
from maya.api import OpenMaya
from rigBuilder.components.utils2 import distance


def localMatrixPlug(parentWMatrixPlug, childWMatrixPlug):
    parentInverseWMatrix = cmds.createNode('inverseMatrix')
    cmds.connectAttr(parentWMatrixPlug, '{}.inputMatrix'.format(parentInverseWMatrix))

    multMatrix = cmds.createNode('multMatrix')
    cmds.connectAttr(childWMatrixPlug, '{}.matrixIn[0]'.format(multMatrix))
    cmds.connectAttr('{}.outputMatrix'.format(parentInverseWMatrix), '{}.matrixIn[1]'.format(multMatrix))

    return '{}.matrixSum'.format(multMatrix)


def ikPvLockSetup(rootSpaceWorldMatrixPlug,
                  shoulderCtrlWorldMatrixPlug, poleVectorCtrlWorldMatrixPlug, handCtrlWorldMatrixPlug):
    #
    shoulderLocalMatrix = localMatrixPlug(rootSpaceWorldMatrixPlug, shoulderCtrlWorldMatrixPlug)
    pvLocalMatrix = localMatrixPlug(rootSpaceWorldMatrixPlug, poleVectorCtrlWorldMatrixPlug)
    handLocalMatrix = localMatrixPlug(rootSpaceWorldMatrixPlug, handCtrlWorldMatrixPlug)

    # distance between shoulder and pv
    shoulderToPvDistance = cmds.createNode('distanceBetween', name='shoulderToPvDistance#')
    cmds.connectAttr(shoulderLocalMatrix, '{}.inMatrix1'.format(shoulderToPvDistance))
    cmds.connectAttr(pvLocalMatrix, '{}.inMatrix2'.format(shoulderToPvDistance))

    # distance between pv and hand
    pvToHandDistance = cmds.createNode('distanceBetween', name='pvToHandDistance#')
    cmds.connectAttr(pvLocalMatrix, '{}.inMatrix1'.format(pvToHandDistance))
    cmds.connectAttr(handLocalMatrix, '{}.inMatrix2'.format(pvToHandDistance))

    return '{}.distance'.format(shoulderToPvDistance), '{}.distance'.format(pvToHandDistance)


def ikStretchSetup(rootSpaceWorldMatrixPlug,
                   shoulderCtrlWMatrixPlug, handCtrlWMatrixPlug,
                   elbowForwardValueOrig, wristForwardValueOrig,
                   minStretchPlug, maxStretchPlug):
    #
    shoulderLocalMatrix = localMatrixPlug(rootSpaceWorldMatrixPlug, shoulderCtrlWMatrixPlug)
    handLocalMatrix = localMatrixPlug(rootSpaceWorldMatrixPlug, handCtrlWMatrixPlug)

    # distance between shoulder and hand
    fullLengthDistance = cmds.createNode('distanceBetween', name='fullLengthDistance#')
    cmds.connectAttr(shoulderLocalMatrix, '{}.inMatrix1'.format(fullLengthDistance))
    cmds.connectAttr(handLocalMatrix, '{}.inMatrix2'.format(fullLengthDistance))

    # compute full length ratio
    fullLengthRatio = cmds.createNode('multiplyDivide', name='fullLengthRatio#')
    cmds.setAttr('{}.operation'.format(fullLengthRatio), 2)  # division
    cmds.connectAttr('{}.distance'.format(fullLengthDistance), '{}.input1X'.format(fullLengthRatio))
    cmds.setAttr('{}.input2X'.format(fullLengthRatio), elbowForwardValueOrig + wristForwardValueOrig)

    # clamp full length ratio
    clampFullLengthRatio = cmds.createNode('clamp', name='clampFullLengthRatio#')
    cmds.connectAttr('{}.outputX'.format(fullLengthRatio), '{}.inputR'.format(clampFullLengthRatio))
    cmds.connectAttr(minStretchPlug, '{}.minR'.format(clampFullLengthRatio))
    cmds.connectAttr(maxStretchPlug, '{}.maxR'.format(clampFullLengthRatio))

    # values Stretched
    valuesStretched = cmds.createNode('multiplyDivide', name='valuesStretched#')

    cmds.connectAttr('{}.outputR'.format(clampFullLengthRatio), '{}.input1X'.format(valuesStretched))
    cmds.setAttr('{}.input2X'.format(valuesStretched), elbowForwardValueOrig)

    cmds.connectAttr('{}.outputR'.format(clampFullLengthRatio), '{}.input1Y'.format(valuesStretched))
    cmds.setAttr('{}.input2Y'.format(valuesStretched), wristForwardValueOrig)

    return '{}.outputX'.format(valuesStretched), '{}.outputY'.format(valuesStretched)


def ikFullStretchSetup(rootSpaceWorldMatrixPlug,
                       shoulderCtrlWorldMatrixPlug, poleVectorCtrlWorldMatrixPlug, handCtrlWorldMatrixPlug,
                       elbowForwardValueOrig, wristForwardValueOrig,
                       minStretchPlug, maxStretchPlug, pvLockPlug, offsetAPlug, offsetBPlug):

    elbowStretchValuePlug, wristStretchValuePlug = ikStretchSetup(
        rootSpaceWorldMatrixPlug=rootSpaceWorldMatrixPlug,
        shoulderCtrlWMatrixPlug=shoulderCtrlWorldMatrixPlug,
        minStretchPlug=minStretchPlug,
        maxStretchPlug=maxStretchPlug,
        elbowForwardValueOrig=abs(elbowForwardValueOrig),
        wristForwardValueOrig=abs(wristForwardValueOrig),
        handCtrlWMatrixPlug=handCtrlWorldMatrixPlug
    )

    elbowLockValuePlug, wristLockValuePlug = ikPvLockSetup(
        rootSpaceWorldMatrixPlug=rootSpaceWorldMatrixPlug,
        shoulderCtrlWorldMatrixPlug=shoulderCtrlWorldMatrixPlug,
        poleVectorCtrlWorldMatrixPlug=poleVectorCtrlWorldMatrixPlug,
        handCtrlWorldMatrixPlug=handCtrlWorldMatrixPlug,
    )

    pvLockSwitch = cmds.createNode('blendColors', name='pvLockSwitch#')
    cmds.connectAttr(pvLockPlug, '{}.blender'.format(pvLockSwitch))
    cmds.connectAttr(elbowStretchValuePlug, '{}.color2R'.format(pvLockSwitch))
    cmds.connectAttr(elbowLockValuePlug, '{}.color1R'.format(pvLockSwitch))

    cmds.connectAttr(wristStretchValuePlug, '{}.color2G'.format(pvLockSwitch))
    cmds.connectAttr(wristLockValuePlug, '{}.color1G'.format(pvLockSwitch))

    offsetStretch = cmds.createNode('plusMinusAverage', name='offsetStretchA#')
    cmds.connectAttr('{}.outputR'.format(pvLockSwitch), '{}.input2D[0].input2Dx'.format(offsetStretch))
    cmds.connectAttr(offsetAPlug, '{}.input2D[1].input2Dx'.format(offsetStretch))

    cmds.connectAttr('{}.outputG'.format(pvLockSwitch), '{}.input2D[0].input2Dy'.format(offsetStretch))
    cmds.connectAttr(offsetBPlug, '{}.input2D[1].input2Dy'.format(offsetStretch))

    scaleResult = cmds.createNode('multiplyDivide', name='scaleResult#')
    cmds.connectAttr('{}.output2D.output2Dx'.format(offsetStretch), '{}.input1X'.format(scaleResult))
    cmds.connectAttr('{}.output2D.output2Dy'.format(offsetStretch), '{}.input1Y'.format(scaleResult))
    cmds.setAttr('{}.input2X'.format(scaleResult), -1 if elbowForwardValueOrig < 0.0 else 1)
    cmds.setAttr('{}.input2Y'.format(scaleResult), -1 if wristForwardValueOrig < 0.0 else 1)

    return '{}.outputX'.format(scaleResult), '{}.outputY'.format(scaleResult)


def poleVectorMatrix(matrixA, matrixB, matrixC, offset=10.0):
    positionA = matrixA[12:15]
    positionB = matrixB[12:15]
    positionC = matrixC[12:15]

    abLength = distance(positionA, positionB)
    bcLength = distance(positionB, positionC)
    fullLength = abLength + bcLength

    abRatio = abLength / fullLength
    bcRatio = bcLength / fullLength

    midPosition = [x * bcRatio + y * abRatio for x, y in zip(positionA, positionC)]

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

    return offsetMatrix * matrix