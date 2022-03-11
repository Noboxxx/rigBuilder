from maya import cmds
from maya.api import OpenMaya
from rigBuilder.components.core import Component, Guide, Storage
from rigBuilder.components.nodeUtils import MultMatrix, DecomposeMatrix, QuatToEuler, RotateOrder, ComposeMatrix, \
    BlendMatrix
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.components.utils2 import controller, distance
from rigBuilder.types import UnsignedInt


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


class Limb(Component):

    aName = str()
    bName = str()
    cName = str()

    abName = str()
    bcName = str()

    def __init__(self, aGuide='', bGuide='', cGuide='', firstSection=4, secondSection=4, **kwargs):
        super(Limb, self).__init__(**kwargs)

        self.aGuide = Guide(aGuide)
        self.bGuide = Guide(bGuide)
        self.cGuide = Guide(cGuide)

        self.firstSection = UnsignedInt(firstSection)
        self.secondSection = UnsignedInt(secondSection)

        self.ikInputs = Storage()
        self.pvInputs = Storage()

    def mirror(self):
        super(Limb, self).mirror()
        self.aGuide = self.aGuide.mirrored()
        self.bGuide = self.bGuide.mirrored()
        self.cGuide = self.cGuide.mirrored()

    def buildSecondSegmentSkinJointsSetup(self, elbowTransform, wristTransform):
        elbowTransform = BlendMatrix(elbowTransform)
        wristTransform = BlendMatrix(wristTransform)

        inverseMatrix = cmds.createNode('inverseMatrix')
        cmds.connectAttr(elbowTransform.resultMatrix, '{}.inputMatrix'.format(inverseMatrix))

        # Stuff
        localWristMatrix = MultMatrix.create('localWristMatrix#')
        localWristMatrix.matrixIn.index(0).connectIn(wristTransform.resultMatrix)
        localWristMatrix.matrixIn.index(1).connectIn('{}.outputMatrix'.format(inverseMatrix))

        inverseLocalWristMatrix = OpenMaya.MMatrix(localWristMatrix.matrixSum.get()).inverse()

        zeroedWristMatrix = MultMatrix.create('zeroedWristMatrix#')
        zeroedWristMatrix.matrixIn.index(0).connectIn(localWristMatrix.matrixSum)
        zeroedWristMatrix.matrixIn.index(1).set(list(inverseLocalWristMatrix))

        zeroedWristMatrixDecomposed = DecomposeMatrix.create('zeroedWristMatrixDecomposed#')
        zeroedWristMatrixDecomposed.inputMatrix.connectIn(zeroedWristMatrix.matrixSum)

        zeroedWristRotate = QuatToEuler.create('zeroedWristRotate#')
        zeroedWristRotate.inputRotateOrder.set(RotateOrder.xzy)
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
        wristResultMatrix.matrixIn.index(3).connectIn(elbowTransform.resultMatrix)

        # Constraint joints
        joints = list()
        for index in range(self.secondSection + 1):
            if joints:
                cmds.select(joints[-1])

            joint = cmds.joint(name='{}{}_{}_skn'.format(self.bcName, index, self))
            cmds.setAttr('{}.segmentScaleCompensate'.format(joint), False)

            self.influencers.append(joint)
            blendMatrix = matrixConstraint((elbowTransform.resultMatrix, wristResultMatrix.matrixSum), joint)
            blendMatrix.blender.set(float(index) / float(self.secondSection))

            joints.append(joint)

        return joints

    def buildFirstSegmentSkinJointsSetup(self, parentMatrixPlug, startMatrixPlug, endMatrixPlug):
        startWorldMatrix = OpenMaya.MMatrix(cmds.getAttr(startMatrixPlug))
        parentWorldInverseMatrix = OpenMaya.MMatrix(cmds.getAttr(parentMatrixPlug)).inverse()
        localStartMatrix = startWorldMatrix * parentWorldInverseMatrix  # type: OpenMaya.MMatrix
        localStartMatrix.setElement(3, 0, 0.0)
        localStartMatrix.setElement(3, 1, 0.0)
        localStartMatrix.setElement(3, 2, 0.0)

        resultMatrices = list()
        for parent, child, offset, x, y, z, rotateOrder in (
                (parentMatrixPlug, startMatrixPlug, localStartMatrix, False, True, True, RotateOrder.xyz),
                (startMatrixPlug, endMatrixPlug, OpenMaya.MMatrix(), True, False, False, RotateOrder.zyx)
        ):
            inverseLocalStartMatrix = offset.inverse()

            inverseMatrix = cmds.createNode('inverseMatrix')
            cmds.connectAttr(parent, '{}.inputMatrix'.format(inverseMatrix))

            localStartMatrixNode = MultMatrix.create('localStartMatrix#')
            localStartMatrixNode.matrixIn.index(0).connectIn(child)
            localStartMatrixNode.matrixIn.index(1).connectIn('{}.outputMatrix'.format(inverseMatrix))

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
            startResultMatrix.matrixIn.index(3).connectIn(parent)

            resultMatrices.append(startResultMatrix)

        # Constraint joints
        joints = list()
        for index in range(self.firstSection + 1):
            if joints:
                cmds.select(joints[-1])

            joint = cmds.joint(name='{}{}_{}_skn'.format(self.abName, index, self))
            cmds.setAttr('{}.segmentScaleCompensate'.format(joint), False)
            self.influencers.append(joint)
            blendMatrix = matrixConstraint((resultMatrices[0].matrixSum, resultMatrices[1].matrixSum), joint)
            blendMatrix.blender.set(float(index) / float(self.firstSection))

            if index == 0:
                self.children.append(joint)

            joints.append(joint)

        return joints

    def ikSetup(self, mainCtrl, switchPlug):
        # joints
        joints = list()
        for index, guide in enumerate((self.aGuide, self.bGuide, self.cGuide)):
            if index == 0:
                cmds.select(mainCtrl)

            joint = cmds.joint(name='ik{}_{}_jnt'.format(index, self))
            joints.append(joint)

            cmds.xform(joint, matrix=list(guide.matrix), worldSpace=True)

        # leg ctrls
        cmds.makeIdentity(joints[0], rotate=True, apply=True)

        for joint in joints:
            cmds.setAttr('{}.segmentScaleCompensate'.format(joint), False)

        legIkCtrlBuffer, legIkCtrl = controller(
            'ik_{}_ctl'.format(self), size=self.size, matrix=self.cGuide.matrix, color=self.color - 100,
            ctrlParent=mainCtrl, visParent=switchPlug, shape='cube')
        self.controllers.append(legIkCtrl)
        self.ikInputs.append(legIkCtrlBuffer)

        legIkHandle, _ = cmds.ikHandle(startJoint=joints[0], endEffector=joints[2], solver='ikRPsolver')
        self.children.append(legIkHandle)

        matrixConstraint((legIkCtrl,), joints[2], translate=False, rotate=True, scale=True, shear=True)
        cmds.parentConstraint(legIkCtrl, legIkHandle)

        self.children.append(legIkCtrlBuffer)

        # pv
        pvMatrix = poleVectorMatrix(
            self.aGuide.matrix, self.bGuide.matrix, self.cGuide.matrix, offset=self.size * 5)
        pvCtrlBuffer, pvCtrl = controller('pv_{}_ctl'.format(self), color=self.color - 100, matrix=pvMatrix,
                                          size=self.size * 0.5, visParent=switchPlug, ctrlParent=mainCtrl, shape='diamond')
        cmds.poleVectorConstraint(pvCtrl, legIkHandle)
        self.controllers.append(pvCtrl)
        self.inputs.append(pvCtrlBuffer)
        self.children.append(pvCtrlBuffer)
        self.pvInputs.append(pvCtrlBuffer)

        return joints

    def fkSetup(self, mainCtrl, switchPlug):
        reverseNode = cmds.createNode('reverse')
        cmds.connectAttr(switchPlug, '{}.inputX'.format(reverseNode))

        ctrls = list()
        latestCtrl = None
        for index, guide in enumerate((self.aGuide, self.bGuide, self.cGuide)):
            ctrlParent = mainCtrl if index == 0 else latestCtrl
            ctrlBuffer, ctrl = controller(
                'fk{}_{}_ctl'.format(index, self), size=self.size, matrix=list(guide.matrix.normalized()),
                color=self.color, ctrlParent=ctrlParent, visParent='{}.outputX'.format(reverseNode))
            ctrls.append(ctrl)
            self.controllers.append(ctrl)

            if index == 0:
                cmds.parent(ctrlBuffer, mainCtrl)
            else:
                cmds.parent(ctrlBuffer, latestCtrl)
            latestCtrl = ctrl

        return ctrls

    def resultSetup(self, fkCtrls, ikJoints, switchPlug):
        resultMatrices = list()
        for ik, fk in zip(ikJoints, fkCtrls):
            resultMatrix = cmds.createNode('blendMatrix')
            resultMatrices.append(resultMatrix)

            cmds.connectAttr('{}.worldMatrix'.format(fk), '{}.matrices[0].matrix'.format(resultMatrix))
            cmds.connectAttr('{}.worldMatrix'.format(ik), '{}.matrices[1].matrix'.format(resultMatrix))
            cmds.connectAttr(switchPlug, '{}.blender'.format(resultMatrix))
            self.outputs.insert(0, '{}.resultMatrix'.format(resultMatrix))

        return resultMatrices

    def skinSetup(self, mainCtrl, resultMatrices):
        legJoints = self.buildFirstSegmentSkinJointsSetup(
            '{}.worldMatrix'.format(mainCtrl), '{}.resultMatrix'.format(resultMatrices[0]),
            '{}.resultMatrix'.format(resultMatrices[1]))
        forelegJoints = self.buildSecondSegmentSkinJointsSetup(resultMatrices[1], resultMatrices[2])

        ankleMatrix = cmds.createNode('blendMatrix')
        cmds.connectAttr('{}.resultMatrix'.format(resultMatrices[2]), '{}.matrices[0].matrix'.format(ankleMatrix))

        ankleJnt = cmds.joint(name='ankle_{}_skn'.format(self))
        cmds.setAttr('{}.segmentScaleCompensate'.format(ankleJnt), False)
        self.influencers.append(ankleJnt)
        for attr in ('translate', 'rotate', 'scale', 'shear'):
            cmds.connectAttr('{}.{}'.format(ankleMatrix, attr), '{}.{}'.format(ankleJnt, attr))
        cmds.connectAttr('{}.parentInverseMatrix'.format(ankleJnt), '{}.parentInverseMatrix'.format(ankleMatrix))
        cmds.connectAttr('{}.jointOrient'.format(ankleJnt), '{}.jointOrient'.format(ankleMatrix))

        cmds.parent(ankleJnt, forelegJoints[-1])
        cmds.parent(forelegJoints[0], legJoints[-1])

    def build(self):
        # settings ctrl
        mainCtrlBuffer, mainCtrl = controller(
            'main_{}_ctl'.format(self), size=self.size * 1.25, color=self.color + 100, matrix=self.aGuide.matrix)
        self.interfaces.append(mainCtrl)
        self.controllers.append(mainCtrl)
        self.children.append(mainCtrlBuffer)
        self.inputs.append(mainCtrlBuffer)

        # switch plug
        switchAttr = 'switchFkIk'
        switchPlug = '{}.{}'.format(mainCtrl, switchAttr)
        cmds.addAttr(mainCtrl, longName=switchAttr, min=0, max=1, keyable=True)

        # ik setup
        ikJoints = self.ikSetup(mainCtrl, switchPlug)

        # fk ctrls
        fkCtrls = self.fkSetup(mainCtrl, switchPlug)

        # Result Matrices and switch
        resultMatrices = self.resultSetup(fkCtrls, ikJoints, switchPlug)

        # skin joints
        self.skinSetup(mainCtrl, resultMatrices)

        # buildFolder
        self.buildFolder()
