from __future__ import division
from rigBuilder.components.core import Component, Guide, Input, Output
from rigBuilder.types import UnsignedInt

from maya import cmds
from .utils import (
    jointChain,
    bufferedCtrl,
    createPoleVector,
    jointChainBetweenTwoMatrices,
)
from .utils import matrixConstraint
from collections import namedtuple
from .nodeUtils import (
    MultiplyDivide,
    DistanceBetween,
    BlendColors,
    Transform,
    Node,
    PlusMinusAverage,
    MultMatrix,
    DecomposeMatrix,
    QuatToEuler,
    ComposeMatrix,
    RotateOrder,
)
from maya.api import OpenMaya

# ---


def buildIkSetup(
        mainCtrl,
        matrices,
        ctrlColor=(255, 255, 0),
        ctrlSize=1.0,
        armIkCtrlName='armIkCtrl#',
        pvCtrlName='pvCtrl#',
        jointNamePattern='ik#'
):
    #
    mainCtrl = Transform(mainCtrl)

    joints = jointChain(matrices, jointNamePattern)
    cmds.parent(joints[0], mainCtrl)

    # ik handle
    armIkHandle, _ = cmds.ikHandle(startJoint=joints[0], endEffector=joints[-1], solver='ikRPsolver')
    armIkCtrlBuffer, armIkCtrl = bufferedCtrl(
        name=armIkCtrlName,
        color=[value - 100 for value in ctrlColor],
        size=ctrlSize * 1.5
    )

    cmds.xform(armIkCtrlBuffer, matrix=list(matrices[-1]))
    cmds.parentConstraint(armIkCtrl, armIkHandle)

    # matrixConstraint((mainCtrl,), armIkCtrlBuffer, maintainOffset=True)

    # pv
    pvCtrlBuffer, pvCtrl = createPoleVector(
        matrixA=matrices[0],
        matrixB=matrices[1],
        matrixC=matrices[2],
        ikHandle=armIkHandle,
        ctrlName=pvCtrlName,
        ctrlSize=ctrlSize / 3.0
    )

    # matrixConstraint((mainCtrl,), pvCtrlBuffer, maintainOffset=True)
    matrixConstraint((armIkCtrl,), joints[-1], translate=False, rotate=True, scale=True, shear=True)

    # stretch
    jointTransforms = [Transform(j) for j in joints]

    mainCtrl.ikStretchA = mainCtrl.addFloatAttr('ikStretchA', keyable=True)
    mainCtrl.ikStretchB = mainCtrl.addFloatAttr('ikStretchB', keyable=True)

    origStretchA = jointTransforms[1].translateX.get()
    origStretchB = jointTransforms[2].translateX.get()

    inverseStretchNode = MultiplyDivide.create('inverseStretchValue#')
    inverseStretchNode.input1X.connectIn(mainCtrl.ikStretchA)
    inverseStretchNode.input1Y.connectIn(mainCtrl.ikStretchB)

    inverseStretchNode.input2X.set(1.0)
    inverseStretchNode.input2Y.set(1.0)

    addStretchNode = PlusMinusAverage.create('addStretch#')
    addStretchNode.input2D.index(0).child('input2Dx').connectIn(inverseStretchNode.outputX)
    addStretchNode.input2D.index(0).child('input2Dy').connectIn(inverseStretchNode.outputY)

    addStretchNode.input2D.index(1).child('input2Dx').set(origStretchA)
    addStretchNode.input2D.index(1).child('input2Dy').set(origStretchB)

    addStretchNode.output2D.child('output2Dx').connectOut(jointTransforms[1].translateX)
    addStretchNode.output2D.child('output2Dy').connectOut(jointTransforms[2].translateX)

    # Return
    Data = namedtuple(
        'IkSetup',
        (
            'joints',
            'controllers',
            'armCtrlBuffer',
            'armCtrl',
            'pvCtrlBuffer',
            'pvCtrl',
            'armIkHandle',
            'addStretchNode',
            'armIkCtrlBuffer'
        )
    )
    return Data(
        joints=joints,
        controllers=(armIkCtrl, pvCtrl),
        armCtrlBuffer=armIkCtrlBuffer,
        armCtrl=armIkCtrl,
        pvCtrlBuffer=pvCtrlBuffer,
        pvCtrl=pvCtrl,
        armIkHandle=armIkHandle,
        addStretchNode=addStretchNode,
        armIkCtrlBuffer=armIkCtrlBuffer
    )


def buildFkSetup(mainCtrl, matrices, ctrlNamePattern='fk#', ctrlSize=1.0, ctrlColor=(255, 255, 0)):
    ctrlBuffers = list()
    ctrls = list()
    for index, matrix in enumerate(matrices):
        ctrlBuffer, ctrl = bufferedCtrl(name=ctrlNamePattern.format(index=index), size=ctrlSize, color=ctrlColor)
        cmds.xform(ctrlBuffer, matrix=list(matrix))
        if index > 0:
            cmds.parent(ctrlBuffer, ctrls[-1])
        ctrls.append(ctrl)
        ctrlBuffers.append(ctrlBuffer)

    matrixConstraint((mainCtrl,), ctrlBuffers[0])

    Data = namedtuple('FkSetup', ('controllers', 'buffers'))
    return Data(
        controllers=ctrls,
        buffers=ctrlBuffers,
    )


def buildIkElbowLockSetup(interfaceNode, startTransform, pvTransform, endTransform, midJoint, endJoint, addStretchNode):
    midJoint = Transform(midJoint)
    endJoint = Transform(endJoint)
    interfaceNode = Node(interfaceNode)

    # locators to avoid cycles (there should be an other way to do so)
    startLocator, = cmds.spaceLocator(name='startLocator#')
    cmds.pointConstraint(startTransform, startLocator)

    pvLocator, = cmds.spaceLocator(name='pvLocator#')
    cmds.pointConstraint(pvTransform, pvLocator)

    endLocator, = cmds.spaceLocator(name='endLocator#')
    cmds.pointConstraint(endTransform, endLocator)

    # distances
    startToPvDistance = DistanceBetween.create('startToPvDistance#')
    startToPvDistance.point1.connectIn('{}.t'.format(startLocator))
    startToPvDistance.point2.connectIn('{}.t'.format(pvLocator))

    pvToEndDistance = DistanceBetween.create('startToPvDistance#')
    pvToEndDistance.point1.connectIn('{}.t'.format(pvLocator))
    pvToEndDistance.point2.connectIn('{}.t'.format(endLocator))

    # scale distances
    distancesScaled = MultiplyDivide.create('startToPvDistanceScaled#')
    distancesScaled.input1X.connectIn(startToPvDistance.distance)
    distancesScaled.input1Y.connectIn(pvToEndDistance.distance)

    distancesScaled.input2X.set(1.0 if midJoint.translateX.get() >= 0.0 else -1.0)
    distancesScaled.input2Y.set(1.0 if endJoint.translateX.get() >= 0.0 else -1.0)

    # add elbow lock attr
    interfaceNode.elbowLock = interfaceNode.addFloatAttr('elbowLock', min=0.0, max=1.0, keyable=True)

    # Connect to joints
    elbowLockBlender = BlendColors.create(name='elbowLockBlender#')
    elbowLockBlender.color1R.connectIn(distancesScaled.outputX)
    elbowLockBlender.color1G.connectIn(distancesScaled.outputY)

    elbowLockBlender.color2R.set(0.0)
    elbowLockBlender.color2G.set(0.0)

    elbowLockBlender.blender.connectIn(interfaceNode.elbowLock)

    elbowLockBlender.outputR.connectOut(addStretchNode.input2D.index(2).child('input2Dx'), force=True)
    elbowLockBlender.outputG.connectOut(addStretchNode.input2D.index(2).child('input2Dy'), force=True)


def buildIkStretchSetup(interface, ikJoints, armCtrl):
    origLength = cmds.getAttr('{}.tx'.format(ikJoints[1])) + cmds.getAttr('{}.tx'.format(ikJoints[2]))

    startLocator, = cmds.spaceLocator(name='startLocator#')
    cmds.pointConstraint(ikJoints[0], startLocator)

    endLocator, = cmds.spaceLocator(name='endLocator#')
    cmds.pointConstraint(armCtrl, endLocator)

    origLengthAttr = 'origLength'
    distanceBetween = cmds.createNode('distanceBetween', name='length#')
    origLengthPlug = '{}.{}'.format(distanceBetween, origLengthAttr)
    cmds.addAttr(distanceBetween, longName=origLengthAttr)
    cmds.setAttr(origLengthPlug, abs(origLength))
    cmds.connectAttr(
        '{}.t'.format(startLocator),
        '{}.point1'.format(distanceBetween)
    )
    cmds.connectAttr(
        '{}.t'.format(endLocator),
        '{}.point2'.format(distanceBetween)
    )

    deltaLengthPMA = cmds.createNode('plusMinusAverage', name='deltaLength#')
    cmds.setAttr('{}.operation'.format(deltaLengthPMA), 2)
    cmds.connectAttr(
        '{}.distance'.format(distanceBetween),
        '{}.input1D[0]'.format(deltaLengthPMA),
    )
    cmds.connectAttr(
        origLengthPlug,
        '{}.input1D[1]'.format(deltaLengthPMA),
    )

    ifStretchedCondition = cmds.createNode('condition', name='ifStretched')
    cmds.connectAttr(
        '{}.output1D'.format(deltaLengthPMA),
        '{}.firstTerm'.format(ifStretchedCondition),
    )
    cmds.setAttr('{}.operation'.format(ifStretchedCondition), 2)
    cmds.setAttr('{}.colorIfFalseR'.format(ifStretchedCondition), 0)
    cmds.connectAttr(
        '{}.output1D'.format(deltaLengthPMA),
        '{}.colorIfTrueR'.format(ifStretchedCondition),
    )

    halfDeltaValueMD = cmds.createNode('multiplyDivide', name='halfDeltaValue#')
    cmds.setAttr('{}.input2X'.format(halfDeltaValueMD), .5 if origLength >= 0.0 else -.5)
    cmds.connectAttr(
        '{}.outColorR'.format(ifStretchedCondition),
        '{}.input1X'.format(halfDeltaValueMD),
    )

    origForwardValue = 'origForwardValue'
    for lct, j in zip((startLocator, endLocator), ikJoints[1:]):
        cmds.addAttr(j, longName=origForwardValue)
        origForwardPlug = '{}.{}'.format(j, origForwardValue)
        forwardPlug = '{}.tx'.format(j)
        cmds.setAttr(origForwardPlug, cmds.getAttr(forwardPlug))
        addValueNodePMA = cmds.createNode('plusMinusAverage', name='stretchAdd#')
        cmds.connectAttr(
            '{}.outputX'.format(halfDeltaValueMD),
            '{}.input1D[0]'.format(addValueNodePMA)
        )
        cmds.connectAttr(
            origForwardPlug,
            '{}.input1D[1]'.format(addValueNodePMA)
        )
        cmds.connectAttr(
            '{}.output1D'.format(addValueNodePMA),
            forwardPlug
        )

    Data = namedtuple('StretchSetup', ('measureTransforms',))
    return Data(
        measureTransforms=(startLocator, endLocator),
    )


def buildForearmSkinJointsSetup(elbowTransform, wristTransform, sections=4, jointNamePattern='twist#'):
    elbowTransform = Transform(elbowTransform)
    wristTransform = Transform(wristTransform)

    # Create joints
    joints = jointChainBetweenTwoMatrices(
        elbowTransform.worldMatrix.get(),
        wristTransform.worldMatrix.get(),
        sections=sections,
        namePattern=jointNamePattern
    )

    # Stuff
    localWristMatrix = MultMatrix.create('localWristMatrix#')
    localWristMatrix.matrixIn.index(0).connectIn(wristTransform.worldMatrix)
    localWristMatrix.matrixIn.index(1).connectIn(elbowTransform.worldInverseMatrix)

    inverseLocalWristMatrix = OpenMaya.MMatrix(localWristMatrix.matrixSum.get()).inverse()

    zeroedWristMatrix = MultMatrix.create('zeroedWristMatrix#')
    zeroedWristMatrix.matrixIn.index(0).connectIn(localWristMatrix.matrixSum)
    zeroedWristMatrix.matrixIn.index(1).set(list(inverseLocalWristMatrix))

    zeroedWristMatrixDecomposed = DecomposeMatrix.create('zeroedWristMatrixDecomposed#')
    zeroedWristMatrixDecomposed.inputMatrix.connectIn(zeroedWristMatrix.matrixSum)

    zeroedWristRotate = QuatToEuler.create('zeroedWristRotate#')
    zeroedWristRotate.inputRotateOrder.set(RotateOrder.zxy)
    zeroedWristRotate.inputQuat.connectIn(zeroedWristMatrixDecomposed.outputQuat)

    wristXRotationMatrix = ComposeMatrix.create('wristXRotationMatrix#')
    wristXRotationMatrix.inputRotateX.connectIn(zeroedWristRotate.outputRotateX)

    wristMatrixDecomposed = DecomposeMatrix.create('localStartMatrixDecomposed#')
    wristMatrixDecomposed.inputMatrix.connectIn(localWristMatrix.matrixSum)

    wristTranslateMatrix = ComposeMatrix.create('localStartTranslateMatrix#')
    wristTranslateMatrix.inputTranslate.connectIn(wristMatrixDecomposed.outputTranslate)

    wristResultMatrix = MultMatrix.create('startResultMatrix#')
    wristResultMatrix.matrixIn.index(0).connectIn(wristXRotationMatrix.outputMatrix)
    # startResultMatrix.matrixIn.index(1).set(list(offset))
    wristResultMatrix.matrixIn.index(2).connectIn(wristTranslateMatrix.outputMatrix)
    wristResultMatrix.matrixIn.index(3).connectIn(elbowTransform.worldMatrix)

    # Constraint joints
    for index, joint in enumerate(joints):
        blender = index / sections
        blendMatrix = matrixConstraint((elbowTransform.worldMatrix, wristResultMatrix.matrixSum), joint)
        blendMatrix.blender.set(blender)

    return joints


def buildArmSkinJointsSetup(parentTransform, startTransform, endTransform, sections=4, jointNamePattern='twist#'):
    parentTransform = Transform(parentTransform)
    startTransform = Transform(startTransform)
    endTransform = Transform(endTransform)

    startWorldMatrix = OpenMaya.MMatrix(startTransform.worldMatrix.get())
    parentWorldInverseMatrix = OpenMaya.MMatrix(parentTransform.worldInverseMatrix.get())
    localStartMatrix = startWorldMatrix * parentWorldInverseMatrix  # type: OpenMaya.MMatrix
    localStartMatrix.setElement(3, 0, 0.0)
    localStartMatrix.setElement(3, 1, 0.0)
    localStartMatrix.setElement(3, 2, 0.0)

    resultMatrices = list()
    for parent, child, offset, x, y, z, rotateOrder in (
            (parentTransform, startTransform, localStartMatrix, False, True, True, RotateOrder.xyz),
            (startTransform, endTransform, OpenMaya.MMatrix(), True, False, False, RotateOrder.yzx)
    ):
        inverseLocalStartMatrix = offset.inverse()

        localStartMatrixNode = MultMatrix.create('localStartMatrix#')
        localStartMatrixNode.matrixIn.index(0).connectIn(child.worldMatrix)
        localStartMatrixNode.matrixIn.index(1).connectIn(parent.worldInverseMatrix)

        localStartRotateMatrix = MultMatrix.create('localStartRotateMatrix#')
        localStartRotateMatrix.matrixIn.index(0).connectIn(localStartMatrixNode.matrixSum)
        localStartRotateMatrix.matrixIn.index(1).set(list(inverseLocalStartMatrix))

        localStartRotateMatrixDecomposed = DecomposeMatrix.create('localStartMatrixDecomposed#')
        localStartRotateMatrixDecomposed.inputMatrix.connectIn(localStartRotateMatrix.matrixSum)

        localStartQuatToEuler = QuatToEuler.create('localStartQuatToEuler#')
        localStartQuatToEuler.inputRotateOrder.set(rotateOrder)
        localStartQuatToEuler.inputQuat.connectIn(localStartRotateMatrixDecomposed.outputQuat)

        localStartRotation = ComposeMatrix.create('localStartRotation#')
        if x:
            localStartRotation.inputRotateX.connectIn(localStartQuatToEuler.outputRotateX)
        if y:
            localStartRotation.inputRotateY.connectIn(localStartQuatToEuler.outputRotateY)
        if z:
            localStartRotation.inputRotateZ.connectIn(localStartQuatToEuler.outputRotateZ)

        localStartMatrixDecomposed = DecomposeMatrix.create('localStartMatrixDecomposed#')
        localStartMatrixDecomposed.inputMatrix.connectIn(localStartMatrixNode.matrixSum)

        localStartTranslateMatrix = ComposeMatrix.create('localStartTranslateMatrix#')
        localStartTranslateMatrix.inputTranslate.connectIn(localStartMatrixDecomposed.outputTranslate)

        startResultMatrix = MultMatrix.create('startResultMatrix#')
        startResultMatrix.matrixIn.index(0).connectIn(localStartRotation.outputMatrix)
        startResultMatrix.matrixIn.index(1).set(list(offset))
        startResultMatrix.matrixIn.index(2).connectIn(localStartTranslateMatrix.outputMatrix)
        startResultMatrix.matrixIn.index(3).connectIn(parent.worldMatrix)

        resultMatrices.append(startResultMatrix)

    joints = jointChainBetweenTwoMatrices(
        startTransform.worldMatrix.get(),
        endTransform.worldMatrix.get(),
        namePattern=jointNamePattern
    )

    for index, joint in enumerate(joints):
        blender = index / sections
        blendMatrix = matrixConstraint((resultMatrices[0].matrixSum, resultMatrices[1].matrixSum), joint)
        blendMatrix.blender.set(blender)

    return joints


def buildTwistingChain(parentTransform, startTransform, endTransform, sections=4, jointNamePattern='twist#'):
    parentTransform = Transform(parentTransform)
    startTransform = Transform(startTransform)
    endTransform = Transform(endTransform)

    startWorldMatrix = OpenMaya.MMatrix(startTransform.worldMatrix.get())
    parentWorldInverseMatrix = OpenMaya.MMatrix(parentTransform.worldInverseMatrix.get())
    localStartMatrix = startWorldMatrix * parentWorldInverseMatrix  # type: OpenMaya.MMatrix
    localStartMatrix.setElement(3, 0, 0.0)
    localStartMatrix.setElement(3, 1, 0.0)
    localStartMatrix.setElement(3, 2, 0.0)

    resultMatrices = list()
    for parent, child, offset, x, y, z, rotateOrder in (
            (parentTransform, startTransform, localStartMatrix, False, True, True, RotateOrder.xyz),
            (startTransform, endTransform, OpenMaya.MMatrix(), True, False, False, RotateOrder.yzx)
    ):
        inverseLocalStartMatrix = offset.inverse()

        localStartMatrixNode = MultMatrix.create('localStartMatrix#')
        localStartMatrixNode.matrixIn.index(0).connectIn(child.worldMatrix)
        localStartMatrixNode.matrixIn.index(1).connectIn(parent.worldInverseMatrix)

        localStartRotateMatrix = MultMatrix.create('localStartRotateMatrix#')
        localStartRotateMatrix.matrixIn.index(0).connectIn(localStartMatrixNode.matrixSum)
        localStartRotateMatrix.matrixIn.index(1).set(list(inverseLocalStartMatrix))

        localStartRotateMatrixDecomposed = DecomposeMatrix.create('localStartMatrixDecomposed#')
        localStartRotateMatrixDecomposed.inputMatrix.connectIn(localStartRotateMatrix.matrixSum)

        localStartQuatToEuler = QuatToEuler.create('localStartQuatToEuler#')
        localStartQuatToEuler.inputRotateOrder.set(rotateOrder)
        localStartQuatToEuler.inputQuat.connectIn(localStartRotateMatrixDecomposed.outputQuat)

        localStartRotation = ComposeMatrix.create('localStartRotation#')
        if x:
            localStartRotation.inputRotateX.connectIn(localStartQuatToEuler.outputRotateX)
        if y:
            localStartRotation.inputRotateY.connectIn(localStartQuatToEuler.outputRotateY)
        if z:
            localStartRotation.inputRotateZ.connectIn(localStartQuatToEuler.outputRotateZ)

        localStartMatrixDecomposed = DecomposeMatrix.create('localStartMatrixDecomposed#')
        localStartMatrixDecomposed.inputMatrix.connectIn(localStartMatrixNode.matrixSum)

        localStartTranslateMatrix = ComposeMatrix.create('localStartTranslateMatrix#')
        localStartTranslateMatrix.inputTranslate.connectIn(localStartMatrixDecomposed.outputTranslate)

        startResultMatrix = MultMatrix.create('startResultMatrix#')
        startResultMatrix.matrixIn.index(0).connectIn(localStartRotation.outputMatrix)
        startResultMatrix.matrixIn.index(1).set(list(offset))
        startResultMatrix.matrixIn.index(2).connectIn(localStartTranslateMatrix.outputMatrix)
        startResultMatrix.matrixIn.index(3).connectIn(parent.worldMatrix)

        resultMatrices.append(startResultMatrix)

    joints = jointChainBetweenTwoMatrices(
        startTransform.worldMatrix.get(),
        endTransform.worldMatrix.get(),
        namePattern=jointNamePattern
    )

    for index, joint in enumerate(joints):
        blender = index / sections
        blendMatrix = matrixConstraint((resultMatrices[0].matrixSum, resultMatrices[1].matrixSum), joint)
        blendMatrix.blender.set(blender)

    return joints

    #
    # # get world rotate, scale, shear of parentTransform
    # parentTransforms = DecomposeMatrix.create('parentTransforms#')
    # parentTransforms.inputMatrix.connectIn(parentTransform.worldMatrix)
    #
    # parentRotateMatrix = ComposeMatrix.create('parentRotateMatrix#')
    # parentRotateMatrix.inputRotate.connectIn(parentTransforms.outputRotate)
    # parentRotateMatrix.inputScale.connectIn(parentTransforms.outputScale)
    # parentRotateMatrix.inputShear.connectIn(parentTransforms.outputShear)
    #
    # # get world translate of startTransform
    # startTransforms = DecomposeMatrix.create('startTransforms#')
    # startTransforms.inputMatrix.connectIn(startTransform.worldMatrix)
    #
    # startTranslate = ComposeMatrix.create('startTranslate#')
    # startTranslate.inputTranslate.connectIn(startTransforms.outputTranslate)
    #
    # # Extract only ry, ry from start trs
    # startPartialRotateMatrix = ComposeMatrix.create('startRotateMatrix#')
    # startPartialRotateMatrix.inputRotateY.connectIn(startTransform.rotateY)
    # startPartialRotateMatrix.inputRotateZ.connectIn(startTransform.rotateZ)
    #
    # # Get offset matrix parent > start
    # startWorldMatrix = OpenMaya.MMatrix(startTransform.worldMatrix.get())
    # parentWorldInverseMatrix = OpenMaya.MMatrix(parentTransform.worldInverseMatrix.get())
    # startOffsetMatrix = startWorldMatrix * parentWorldInverseMatrix  # type: OpenMaya.MMatrix
    # startOffsetMatrix.setElement(3, 0, 0.0)  # zero out translation
    # startOffsetMatrix.setElement(3, 1, 0.0)
    # startOffsetMatrix.setElement(3, 2, 0.0)
    #
    # # Compose and decompose start result matrix
    # startResultMatrix = MultMatrix.create('startResultMatrix#')
    # startResultMatrix.matrixIn.index(0).connectIn(startPartialRotateMatrix.outputMatrix)
    # startResultMatrix.matrixIn.index(1).set(list(startOffsetMatrix))
    # startResultMatrix.matrixIn.index(2).connectIn(parentRotateMatrix.outputMatrix)
    # startResultMatrix.matrixIn.index(3).connectIn(startTranslate.outputMatrix)
    #
    # #####
    #
    # # get rx from endTransform
    # endRotateMatrix = ComposeMatrix.create('endRotateMatrix#')
    # endRotateMatrix.inputRotateX.connectIn(endTransform.rotateX)
    #
    # # get world rotate, scale, shear of startTransform
    # startRotateMatrix = ComposeMatrix.create('startRotateMatrix#')
    # startRotateMatrix.inputRotate.connectIn(startTransforms.outputRotate)
    # startRotateMatrix.inputScale.connectIn(startTransforms.outputScale)
    # startRotateMatrix.inputShear.connectIn(startTransforms.outputShear)
    #
    # # get world translate of startTransform
    # endTransforms = DecomposeMatrix.create('endTransforms#')
    # endTransforms.inputMatrix.connectIn(endTransform.worldMatrix)
    #
    # endTranslate = ComposeMatrix.create('endTranslate#')
    # endTranslate.inputTranslate.connectIn(endTransforms.outputTranslate)
    #
    # # Compose and decompose start result matrix
    # endResultMatrix = MultMatrix.create('endResultMatrix#')
    # endResultMatrix.matrixIn.index(0).connectIn(endRotateMatrix.outputMatrix)
    # endResultMatrix.matrixIn.index(1).connectIn(startRotateMatrix.outputMatrix)
    # endResultMatrix.matrixIn.index(2).connectIn(endTranslate.outputMatrix)
    #
    # ###
    #
    # joints = jointChainBetweenTwoMatrices(
    #     startTransform.worldMatrix.get(),
    #     endTransform.worldMatrix.get(),
    #     sections=sections,
    #     namePattern=jointNamePattern
    # )
    #
    # for index, joint in enumerate(joints):
    #     joint = Joint(joint)
    #     blender = index / sections
    #
    #     constraint = BlendMatrix.create('matrixConstraint#')
    #
    #     constraint.blender.set(blender)
    #
    #     constraint.matrices.index(0).child(constraint.matricesMatrixAttr).connectIn(startResultMatrix.matrixSum)
    #     constraint.matrices.index(1).child(constraint.matricesMatrixAttr).connectIn(endResultMatrix.matrixSum)
    #
    #     constraint.jointOrient.connectIn(joint.jointOrient)
    #     constraint.parentInverseMatrix.connectIn(joint.parentInverseMatrix)
    #
    #     constraint.translate.connectOut(joint.translate)
    #     constraint.rotate.connectOut(joint.rotate)
    #     constraint.scale.connectOut(joint.scale)
    #     constraint.shear.connectOut(joint.shear)
    #
    # return joints


def buildResultSetup(mainCtrl, fkTransforms, ikTransforms, fkCtrls, ikCtrls, resultNamePattern='result{index}'):
    # fk ik switch
    switchAttr = 'switchFkIk'
    switchPlug = '{}.{}'.format(mainCtrl, switchAttr)
    cmds.addAttr(mainCtrl, longName=switchAttr, min=0.0, max=1.0, dv=0.0, attributeType='float', keyable=True)

    # create result chain
    resultTransforms = list()
    for index, (fk, ik) in enumerate(zip(fkTransforms, ikTransforms)):
        rs, = cmds.spaceLocator(name=resultNamePattern.format(index=index))
        blendMatrix = matrixConstraint((fk, ik), rs)
        cmds.connectAttr(switchPlug, '{}.blender'.format(blendMatrix))
        if index > 0:
            cmds.parent(rs, resultTransforms[-1])
        resultTransforms.append(rs)

    switchReverseNode = cmds.createNode('reverse')
    cmds.connectAttr(switchPlug, '{}.inputX'.format(switchReverseNode))

    # switch chain vis
    for ctrl in fkCtrls:
        cmds.connectAttr('{}.outputX'.format(switchReverseNode), '{}.v'.format(ctrl),)

    for ctrl in ikCtrls:
        cmds.connectAttr(switchPlug, '{}.v'.format(ctrl),)

    Data = namedtuple('ResultSetup', ('transforms',))
    return Data(
        transforms=resultTransforms
    )


def buildSnapSetup(interface):
    # snap attr
    snapAttr = 'snap'
    snapPlug = '{}.{}'.format(interface, snapAttr)
    cmds.addAttr(interface, longName=snapAttr, attributeType='enum', enumName='_:ikToFk:fkToIk')
    cmds.setAttr(snapPlug, channelBox=True)

    # script job
    pythonCmd = 'print cmds.getAttr(\\\"{snapPlug}\\\")'.format(snapPlug=snapPlug)
    scriptJobCmd = 'cmds.scriptJob(killWithScene=True, attributeChange=[\"{snapPlug}\", \"{pythonCmd}\"])'.format(
        snapPlug=snapPlug,
        pythonCmd=pythonCmd,
    )
    command = 'print \"{snapPlug}: init scriptJob\"; {scriptJobCmd}'.format(
        snapPlug=snapPlug,
        scriptJobCmd=scriptJobCmd
    )
    exec command

    # scriptNode
    scriptNode = cmds.createNode('script', name='snapScript#')
    cmds.setAttr('{}.sourceType'.format(scriptNode), 1)  # python
    cmds.setAttr('{}.scriptType'.format(scriptNode), 1)  # open/close
    cmds.setAttr('{}.before'.format(scriptNode), command, type='string')

    # Return
    Data = namedtuple('SnapSetup', ('scriptNode',))
    return Data(
        scriptNode=scriptNode
    )


class Arm(Component):

    def __init__(self, shoulderGuide='', elbowGuide='', wristGuide='', armSections=4, forearmSections=4, **kwargs):
        super(Arm, self).__init__(**kwargs)

        self.shoulderGuide = Guide(shoulderGuide)
        self.elbowGuide = Guide(elbowGuide)
        self.wristGuide = Guide(wristGuide)
        self.armSections = UnsignedInt(armSections)
        self.forearmSections = UnsignedInt(forearmSections)

        self.ikInputs = Input()
        self.armInfluencers = Output()
        self.forearmInfluencers = Output()
        self.scriptNodes = Output()

    def mirror(self):
        super(Arm, self).mirror()
        self.shoulderGuide = self.shoulderGuide.mirrored()
        self.elbowGuide = self.elbowGuide.mirrored()
        self.wristGuide = self.wristGuide.mirrored()

    def build(self):
        # matrices
        matrices = (self.shoulderGuide.matrix, self.elbowGuide.matrix, self.wristGuide.matrix)

        # mainCtrl
        mainCtrlBuffer, mainCtrl = bufferedCtrl(
            'main_' + str(self) + '_ctl',
            color=[c - 100 for c in self.color],
            size=self.size * 1.5
        )
        cmds.xform(mainCtrlBuffer, matrix=list(self.shoulderGuide.matrix))

        self.controllers.append(mainCtrl)
        self.interface = mainCtrl
        self.children.append(mainCtrlBuffer)
        self.inputs.append(mainCtrlBuffer)

        # fkSetup
        fkSetup = buildFkSetup(
            mainCtrl,
            matrices,
            ctrlColor=self.color,
            ctrlSize=self.size,
            ctrlNamePattern='fk{index}_' + str(self) + '_ctl'
        )
        self.controllers += fkSetup.controllers
        self.children.append(fkSetup.buffers[0])

        # ikSetup
        ikSetup = buildIkSetup(
            mainCtrl,
            matrices,
            ctrlColor=self.color,
            ctrlSize=self.size,
            armIkCtrlName=str(self) + '_ctl',
            pvCtrlName='pv_' + str(self) + '_ctl'
        )
        self.ikInputs.append(ikSetup.armCtrlBuffer)
        self.controllers += ikSetup.controllers
        self.children += ikSetup.armIkHandle, ikSetup.armCtrlBuffer, ikSetup.pvCtrlBuffer

        # # squashStretchSetup
        # stretchSetup = buildIkStretchSetup(mainCtrl, ikSetup.joints, ikSetup.armCtrl)
        # fld.children += stretchSetup.measureTransforms

        # elbowLockSetup
        buildIkElbowLockSetup(
            interfaceNode=mainCtrl,
            startTransform=ikSetup.joints[0],
            pvTransform=ikSetup.pvCtrl,
            endTransform=ikSetup.armCtrl,
            midJoint=ikSetup.joints[1],
            endJoint=ikSetup.joints[2],
            addStretchNode=ikSetup.addStretchNode
        )

        resultSetup = buildResultSetup(
            mainCtrl,
            fkSetup.controllers,
            ikSetup.joints,
            fkSetup.controllers,
            ikSetup.controllers,
            resultNamePattern='rs{index}_' + str(self) + '_lct'
        )
        self.children.append(resultSetup.transforms[0])

        # skin setup
        armSkinJoints = buildArmSkinJointsSetup(
            mainCtrl,
            resultSetup.transforms[0],
            resultSetup.transforms[1],
            sections=self.armSections,
            jointNamePattern='arm{index}_' + str(self) + '_skn'
        )
        self.influencers += armSkinJoints
        self.armInfluencers += armSkinJoints
        self.children.append(armSkinJoints[0])

        forearmSkinJoints = buildForearmSkinJointsSetup(
            resultSetup.transforms[1],
            resultSetup.transforms[2],
            sections=self.forearmSections,
            jointNamePattern='forearm{index}_' + str(self) + '_skn'
        )
        self.influencers += forearmSkinJoints
        self.forearmInfluencers += forearmSkinJoints
        self.children.append(forearmSkinJoints[0])

        self.outputs.append(resultSetup.transforms[-1])

        # snap setup
        snapSetup = buildSnapSetup(mainCtrl)
        self.scriptNodes += snapSetup.scriptNode,

        self.buildFolder()
