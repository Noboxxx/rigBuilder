from maya import cmds
from maya.api import OpenMaya
from rigBuilder.components.core import Component, Guide
from rigBuilder.components.nodeUtils import MultMatrix, DecomposeMatrix, QuatToEuler, RotateOrder, ComposeMatrix, \
    BlendMatrix
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.components.utils2 import controller, distance
from rigBuilder.types import UnsignedInt, Matrix


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


class Leg(Component):

    def __init__(self, hipGuide='', kneeGuide='', ankleGuide='', toesGuide='', legSection=4, forelegSection=4,
                 footTipGuide='', footBackGuide='', footInGuide='', footOutGuide='', **kwargs):
        super(Leg, self).__init__(**kwargs)

        self.hipGuide = Guide(hipGuide)
        self.kneeGuide = Guide(kneeGuide)
        self.ankleGuide = Guide(ankleGuide)
        self.toesGuide = Guide(toesGuide)

        self.legSection = UnsignedInt(legSection)
        self.forelegSection = UnsignedInt(forelegSection)

        self.footTipGuide = Guide(footTipGuide)
        self.footBackGuide = Guide(footBackGuide)
        self.footInGuide = Guide(footInGuide)
        self.footOutGuide = Guide(footOutGuide)

    def mirror(self):
        super(Leg, self).mirror()
        self.hipGuide = self.hipGuide.mirrored()
        self.kneeGuide = self.kneeGuide.mirrored()
        self.ankleGuide = self.ankleGuide.mirrored()
        self.toesGuide = self.toesGuide.mirrored()

        self.footTipGuide = self.footTipGuide.mirrored()
        self.footBackGuide = self.footBackGuide.mirrored()
        self.footInGuide = self.footInGuide.mirrored()
        self.footOutGuide = self.footOutGuide.mirrored()

    def buildForelegSkinJointsSetup(self, elbowTransform, wristTransform):
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
        wristResultMatrix.matrixIn.index(3).connectIn(elbowTransform.resultMatrix)

        # Constraint joints
        joints = list()
        for index in range(self.forelegSection + 1):
            if joints:
                cmds.select(joints[-1])

            joint = cmds.joint(name='foreleg{}_{}_skn'.format(index, self))
            cmds.setAttr('{}.segmentScaleCompensate'.format(joint), False)

            self.influencers.append(joint)
            blendMatrix = matrixConstraint((elbowTransform.resultMatrix, wristResultMatrix.matrixSum), joint)
            blendMatrix.blender.set(float(index) / float(self.forelegSection))

            joints.append(joint)

        return joints

    def buildLegSkinJointsSetup(self, parentMatrixPlug, startMatrixPlug, endMatrixPlug):
        startWorldMatrix = OpenMaya.MMatrix(cmds.getAttr(startMatrixPlug))
        parentWorldInverseMatrix = OpenMaya.MMatrix(cmds.getAttr(parentMatrixPlug)).inverse()
        localStartMatrix = startWorldMatrix * parentWorldInverseMatrix  # type: OpenMaya.MMatrix
        localStartMatrix.setElement(3, 0, 0.0)
        localStartMatrix.setElement(3, 1, 0.0)
        localStartMatrix.setElement(3, 2, 0.0)

        resultMatrices = list()
        for parent, child, offset, x, y, z, rotateOrder in (
                (parentMatrixPlug, startMatrixPlug, localStartMatrix, False, True, True, RotateOrder.xyz),
                (startMatrixPlug, endMatrixPlug, OpenMaya.MMatrix(), True, False, False, RotateOrder.yzx)
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
        for index in range(self.forelegSection + 1):
            if joints:
                cmds.select(joints[-1])

            joint = cmds.joint(name='leg{}_{}_skn'.format(index, self))
            cmds.setAttr('{}.segmentScaleCompensate'.format(joint), False)
            self.influencers.append(joint)
            blendMatrix = matrixConstraint((resultMatrices[0].matrixSum, resultMatrices[1].matrixSum), joint)
            blendMatrix.blender.set(float(index) / float(self.forelegSection))

            if index == 0:
                self.children.append(joint)

            joints.append(joint)

        return joints

    def ikSetup(self, mainCtrl, switchPlug):
        # joints
        joints = list()
        for index, guide in enumerate((self.hipGuide, self.kneeGuide, self.ankleGuide, self.toesGuide)):
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
            'ikLeg_{}_ctl'.format(self), size=self.size, matrix=self.ankleGuide.matrix, color=self.color - 100,
            ctrlParent=mainCtrl, visParent=switchPlug, shape='cube')
        self.controllers.append(legIkCtrl)

        legIkHandle, _ = cmds.ikHandle(startJoint=joints[0], endEffector=joints[2], solver='ikRPsolver')
        self.children.append(legIkHandle)

        footIkCtrlBuffer, footIkCtrl = controller(
            'ikFoot_{}_ctl'.format(self), size=self.size, matrix=self.toesGuide.matrix, color=self.color - 100,
            ctrlParent=legIkCtrl, visParent=switchPlug, normal=(0, 1, 0))
        self.controllers.append(footIkCtrl)
        cmds.scaleConstraint(footIkCtrl, joints[2])

        footIkHandle, _ = cmds.ikHandle(startJoint=joints[2], endEffector=joints[3], solver='ikSCsolver')
        self.children.append(footIkHandle)

        toesIkCtrlBuffer, toesIkCtrl = controller(
            'ikToes_{}_ctl'.format(self), size=self.size, matrix=self.toesGuide.matrix, color=self.color - 100,
            ctrlParent=footIkCtrl, visParent=switchPlug)
        self.controllers.append(toesIkCtrl)

        cmds.parentConstraint(footIkCtrl, legIkHandle, maintainOffset=True)
        cmds.parentConstraint(footIkCtrl, footIkHandle)
        matrixConstraint((toesIkCtrl,), joints[3], translate=False, rotate=True, scale=True, shear=True)

        self.children.append(legIkCtrlBuffer)

        # reverseFoot setup
        footInIkCtrlBuffer, footInIkCtrl = controller(
            'ikFootIn_{}_ctl'.format(self), size=self.size * 0.25, matrix=self.footInGuide.matrix,
            color=self.color - 100, ctrlParent=legIkCtrl, visParent=switchPlug, shape='sphere')
        self.controllers.append(footInIkCtrl)

        footOutIkCtrlBuffer, footOutIkCtrl = controller(
            'ikFootOut_{}_ctl'.format(self), size=self.size * 0.25, matrix=self.footOutGuide.matrix,
            color=self.color - 100, ctrlParent=footInIkCtrl, visParent=switchPlug, shape='sphere')
        self.controllers.append(footOutIkCtrl)

        footTipIkCtrlBuffer, footTipIkCtrl = controller(
            'ikFootTip_{}_ctl'.format(self), size=self.size * 0.25, matrix=self.footTipGuide.matrix,
            color=self.color - 100, ctrlParent=footOutIkCtrl, visParent=switchPlug, shape='sphere')
        self.controllers.append(footTipIkCtrl)

        footBackIkCtrlBuffer, footBackIkCtrl = controller(
            'ikFootBack_{}_ctl'.format(self), size=self.size * 0.25, matrix=self.footBackGuide.matrix,
            color=self.color - 100, ctrlParent=footTipIkCtrl, visParent=switchPlug, shape='sphere')
        self.controllers.append(footBackIkCtrl)

        cmds.parent(footInIkCtrlBuffer, legIkCtrl)
        cmds.parent(footOutIkCtrlBuffer, footInIkCtrl)
        cmds.parent(footTipIkCtrlBuffer, footOutIkCtrl)
        cmds.parent(footBackIkCtrlBuffer, footTipIkCtrl)

        cmds.parent(footIkCtrlBuffer, footBackIkCtrl)
        cmds.parent(toesIkCtrlBuffer, footBackIkCtrl)

        # pv
        pvMatrix = poleVectorMatrix(
            self.hipGuide.matrix, self.kneeGuide.matrix, self.ankleGuide.matrix, offset=self.size * 5)
        pvCtrlBuffer, pvCtrl = controller('pv_{}_ctl'.format(self), color=self.color - 100, matrix=pvMatrix,
                                          size=self.size * 0.5, visParent=switchPlug, ctrlParent=mainCtrl, shape='diamond')
        cmds.poleVectorConstraint(pvCtrl, legIkHandle)
        self.controllers.append(pvCtrl)
        self.inputs.append(pvCtrlBuffer)
        self.children.append(pvCtrlBuffer)

        return joints

    def fkSetup(self, mainCtrl, switchPlug):
        reverseNode = cmds.createNode('reverse')
        cmds.connectAttr(switchPlug, '{}.inputX'.format(reverseNode))

        ctrls = list()
        latestCtrl = None
        for index, guide in enumerate((self.hipGuide, self.kneeGuide, self.ankleGuide, self.toesGuide)):
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

        return resultMatrices

    def skinSetup(self, mainCtrl, resultMatrices):
        legJoints = self.buildLegSkinJointsSetup(
            '{}.worldMatrix'.format(mainCtrl), '{}.resultMatrix'.format(resultMatrices[0]),
            '{}.resultMatrix'.format(resultMatrices[1]))
        forelegJoints = self.buildForelegSkinJointsSetup(resultMatrices[1], resultMatrices[2])

        ankleMatrix = cmds.createNode('blendMatrix')
        cmds.connectAttr('{}.resultMatrix'.format(resultMatrices[2]), '{}.matrices[0].matrix'.format(ankleMatrix))

        ankleJnt = cmds.joint(name='ankle_{}_skn'.format(self))
        cmds.setAttr('{}.segmentScaleCompensate'.format(ankleJnt), False)
        self.influencers.append(ankleJnt)
        for attr in ('translate', 'rotate', 'scale', 'shear'):
            cmds.connectAttr('{}.{}'.format(ankleMatrix, attr), '{}.{}'.format(ankleJnt, attr))
        cmds.connectAttr('{}.parentInverseMatrix'.format(ankleJnt), '{}.parentInverseMatrix'.format(ankleMatrix))
        cmds.connectAttr('{}.jointOrient'.format(ankleJnt), '{}.jointOrient'.format(ankleMatrix))

        toesJnt = cmds.joint(name='toes_{}_skn'.format(self))
        cmds.setAttr('{}.segmentScaleCompensate'.format(toesJnt), False)
        self.influencers.append(toesJnt)
        for attr in ('translate', 'rotate', 'scale', 'shear'):
            cmds.connectAttr('{}.{}'.format(resultMatrices[3], attr), '{}.{}'.format(toesJnt, attr))
        cmds.connectAttr('{}.parentInverseMatrix'.format(toesJnt), '{}.parentInverseMatrix'.format(resultMatrices[3]))
        cmds.connectAttr('{}.jointOrient'.format(toesJnt), '{}.jointOrient'.format(resultMatrices[3]))

        cmds.parent(ankleJnt, forelegJoints[-1])
        cmds.parent(forelegJoints[0], legJoints[-1])

    def build(self):
        # settings ctrl
        mainCtrlBuffer, mainCtrl = controller(
            'main_{}_ctl'.format(self), size=self.size * 1.25, color=self.color + 100, matrix=self.hipGuide.matrix)
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
