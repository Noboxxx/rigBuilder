from maya import cmds
from maya.api import OpenMaya
from rigBuilder.components.core import Component, Guide, Storage
from rigBuilder.components.nodeUtils import MultMatrix, DecomposeMatrix, QuatToEuler, RotateOrder, ComposeMatrix, \
    BlendMatrixCustom, Transform, DistanceBetween, MultiplyDivide, BlendColors, Node
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.components.utils2 import controller, distance
from rigBuilder.components.utilss.ikUtils import ikFullStretchSetup, poleVectorMatrix
from rigBuilder.types import UnsignedInt, UnsignedFloat


class Limb(Component):

    aName = str()
    bName = str()
    cName = str()

    abName = str()
    bcName = str()

    def __init__(self, aGuide='', bGuide='', cGuide='', firstSection=4, secondSection=4, pvDistance=5.0, **kwargs):
        super(Limb, self).__init__(**kwargs)

        self.aGuide = Guide(aGuide)
        self.bGuide = Guide(bGuide)
        self.cGuide = Guide(cGuide)

        self.firstSection = UnsignedInt(firstSection)
        self.secondSection = UnsignedInt(secondSection)

        self.pvDistance = UnsignedFloat(pvDistance)

        self.ikInputs = Storage()
        self.pvInputs = Storage()

    def mirror(self):
        super(Limb, self).mirror()
        self.aGuide = self.aGuide.mirrored()
        self.bGuide = self.bGuide.mirrored()
        self.cGuide = self.cGuide.mirrored()

    def buildSecondSegmentSkinJointsSetup(self, elbowTransform, wristTransform):
        elbowTransform = BlendMatrixCustom(elbowTransform)
        wristTransform = BlendMatrixCustom(wristTransform)

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
            'ik_{}_ctl'.format(self), size=self.cGuide.size, matrix=self.cGuide.matrix, color=self.color - 100,
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
            self.aGuide.matrix, self.bGuide.matrix, self.cGuide.matrix, offset=self.bGuide.size * self.pvDistance)
        pvCtrlBuffer, pvCtrl = controller(
            'pv_{}_ctl'.format(self), color=self.color - 100, matrix=pvMatrix,
            size=self.bGuide.size, visParent=switchPlug, ctrlParent=mainCtrl, shape='diamond')
        cmds.poleVectorConstraint(pvCtrl, legIkHandle)
        self.controllers.append(pvCtrl)
        self.inputs.append(pvCtrlBuffer)
        self.children.append(pvCtrlBuffer)
        self.pvInputs.append(pvCtrlBuffer)

        # stretch
        cmds.addAttr(mainCtrl, longName='minStretch', min=0, defaultValue=1, keyable=True)
        cmds.addAttr(mainCtrl, longName='maxStretch', min=0, defaultValue=2, keyable=True)
        cmds.addAttr(mainCtrl, longName='pvLock', min=0, max=1, defaultValue=0, keyable=True)
        cmds.addAttr(mainCtrl, longName='offStretchA', keyable=True)
        cmds.addAttr(mainCtrl, longName='offStretchB', keyable=True)

        elbowStretchPlug, wristStretchPlug = ikFullStretchSetup(
            rootSpaceWorldMatrixPlug='{}.worldMatrix'.format(mainCtrl),
            shoulderCtrlWorldMatrixPlug='{}.worldMatrix'.format(mainCtrl),
            poleVectorCtrlWorldMatrixPlug='{}.worldMatrix'.format(pvCtrl),
            handCtrlWorldMatrixPlug='{}.worldMatrix'.format(legIkCtrl),
            elbowForwardValueOrig=cmds.getAttr('{}.tx'.format(joints[1])),
            wristForwardValueOrig=cmds.getAttr('{}.tx'.format(joints[2])),
            minStretchPlug='{}.minStretch'.format(mainCtrl),
            maxStretchPlug='{}.maxStretch'.format(mainCtrl),
            pvLockPlug='{}.pvLock'.format(mainCtrl),
            offsetAPlug='{}.offStretchA'.format(mainCtrl),
            offsetBPlug='{}.offStretchB'.format(mainCtrl)
        )

        cmds.connectAttr(elbowStretchPlug, '{}.tx'.format(joints[1]))
        cmds.connectAttr(wristStretchPlug, '{}.tx'.format(joints[2]))

        return joints, legIkCtrlBuffer, legIkCtrl, legIkHandle

    def fkSetup(self, mainCtrl, switchPlug):
        reverseNode = cmds.createNode('reverse')
        cmds.connectAttr(switchPlug, '{}.inputX'.format(reverseNode))

        ctrls = list()
        latestCtrl = None
        for index, guide in enumerate((self.aGuide, self.bGuide, self.cGuide)):
            ctrlParent = mainCtrl if index == 0 else latestCtrl
            ctrlBuffer, ctrl = controller(
                'fk{}_{}_ctl'.format(index, self), size=guide.size, matrix=list(guide.matrix),
                color=self.color, ctrlParent=ctrlParent, visParent='{}.outputX'.format(reverseNode))

            cmds.parent(ctrlBuffer, mainCtrl)

            ctrls.append(ctrl)
            self.controllers.append(ctrl)

            if index > 0:
                matrixConstraint((latestCtrl,), ctrlBuffer, maintainOffset=True, scale=False, shear=False)

            latestCtrl = ctrl

        return ctrls, reverseNode

    def resultSetup(self, fkCtrls, ikJoints, switchPlug):
        freeBBfr, freeBCtrl = controller(
            'free{}_{}_ctl'.format(self.bName.title(), self),
            size=self.bGuide.size * .9,
            matrix=self.bGuide.matrix,
            color=self.color + 100,
            shape='sphere'
        )
        self.controllers.append(freeBCtrl)
        self.children.append(freeBBfr)

        resultMatrices = list()
        for index, (ik, fk) in enumerate(zip(ikJoints, fkCtrls)):
            resultMatrix = cmds.createNode('blendMatrixCustom')
            resultMatrices.append(resultMatrix)

            if index != 1:
                cmds.connectAttr('{}.worldMatrix'.format(fk), '{}.matrices[0].matrix'.format(resultMatrix))
                cmds.connectAttr('{}.worldMatrix'.format(ik), '{}.matrices[1].matrix'.format(resultMatrix))
                cmds.connectAttr(switchPlug, '{}.blender'.format(resultMatrix))
            else:
                b = matrixConstraint((fk, ik), freeBBfr)
                cmds.connectAttr(switchPlug, '{}.blender'.format(b))
                cmds.connectAttr('{}.worldMatrix'.format(freeBCtrl), '{}.matrices[0].matrix'.format(resultMatrix))

            self.outputs.insert(0, '{}.resultMatrix'.format(resultMatrix))

        return resultMatrices

    def skinSetup(self, mainCtrl, resultMatrices):
        legJoints = self.buildFirstSegmentSkinJointsSetup(
            '{}.worldMatrix'.format(mainCtrl), '{}.resultMatrix'.format(resultMatrices[0]),
            '{}.resultMatrix'.format(resultMatrices[1]))
        forelegJoints = self.buildSecondSegmentSkinJointsSetup(resultMatrices[1], resultMatrices[2])

        ankleMatrix = cmds.createNode('blendMatrixCustom')
        cmds.connectAttr('{}.resultMatrix'.format(resultMatrices[2]), '{}.matrices[0].matrix'.format(ankleMatrix))

        ankleJnt = cmds.joint(name='{}_{}_skn'.format(self.cName, self))
        cmds.setAttr('{}.segmentScaleCompensate'.format(ankleJnt), False)
        self.influencers.append(ankleJnt)
        for attr in ('translate', 'rotate', 'scale', 'shear'):
            cmds.connectAttr('{}.{}'.format(ankleMatrix, attr), '{}.{}'.format(ankleJnt, attr))
        cmds.connectAttr('{}.parentInverseMatrix'.format(ankleJnt), '{}.parentInverseMatrix'.format(ankleMatrix))
        cmds.connectAttr('{}.jointOrient'.format(ankleJnt), '{}.jointOrient'.format(ankleMatrix))

        cmds.parent(ankleJnt, forelegJoints[-1])
        cmds.parent(forelegJoints[0], legJoints[-1])

        return legJoints + forelegJoints + [ankleJnt]

    def build(self):
        # settings ctrl
        mainCtrlBuffer, mainCtrl = controller(
            'main_{}_ctl'.format(self), size=self.aGuide.size * 1.25, color=self.color + 100, matrix=self.aGuide.matrix)
        self.interfaces.append(mainCtrl)
        self.controllers.append(mainCtrl)
        self.children.append(mainCtrlBuffer)
        self.inputs.append(mainCtrlBuffer)

        # switch plug
        switchAttr = 'switchFkIk'
        switchPlug = '{}.{}'.format(mainCtrl, switchAttr)
        cmds.addAttr(mainCtrl, longName=switchAttr, min=0, max=1, keyable=True)

        # ik setup
        ikJoints = self.ikSetup(mainCtrl, switchPlug)[0]

        # fk ctrls
        fkCtrls = self.fkSetup(mainCtrl, switchPlug)[0]

        # Result Matrices and switch
        resultMatrices = self.resultSetup(fkCtrls, ikJoints, switchPlug)

        # skin joints
        self.skinSetup(mainCtrl, resultMatrices)

        # buildFolder
        self.buildFolder()
