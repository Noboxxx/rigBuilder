from maya import cmds
from maya.api import OpenMaya
from rigBuilder.components.core import Component, Guide
from rigBuilder.components.nodeUtils import MultMatrix, DecomposeMatrix, QuatToEuler, RotateOrder, ComposeMatrix, \
    Transform, BlendMatrix
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.types import UnsignedInt


class Leg(Component):

    def __init__(
            self,
            hipGuide='',
            kneeGuide='',
            ankleGuide='',

            toesGuide='',

            legSection=4,
            forelegSection=4,

            footTipGuide='',
            footBackGuide='',
            footInGuide='',
            footOutGuide='',

            **kwargs
    ):
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

        # # Create joints
        # joints = jointChainBetweenTwoMatrices(
        #     elbowTransform.worldMatrix.get(),
        #     wristTransform.worldMatrix.get(),
        #     sections=sections,
        #     namePattern=jointNamePattern
        # )

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
            self.influencers.append(joint)
            blendMatrix = matrixConstraint((elbowTransform.resultMatrix, wristResultMatrix.matrixSum), joint)
            blendMatrix.blender.set(float(index) / float(self.forelegSection))

            if index == 0:
                self.children.append(joint)

            joints.append(joint)

        return joints

    # def buildLegSkinJointsSetup(self, parentTransform, startTransform, endTransform, sections=4, jointNamePattern='twist#'):
    #     parentTransform = Transform(parentTransform)
    #     startTransform = Transform(startTransform)
    #     endTransform = Transform(endTransform)
    #
    #     startWorldMatrix = OpenMaya.MMatrix(startTransform.worldMatrix.get())
    #     parentWorldInverseMatrix = OpenMaya.MMatrix(parentTransform.worldInverseMatrix.get())
    #     localStartMatrix = startWorldMatrix * parentWorldInverseMatrix  # type: OpenMaya.MMatrix
    #     localStartMatrix.setElement(3, 0, 0.0)
    #     localStartMatrix.setElement(3, 1, 0.0)
    #     localStartMatrix.setElement(3, 2, 0.0)
    #
    #     resultMatrices = list()
    #     for parent, child, offset, x, y, z, rotateOrder in (
    #             (parentTransform, startTransform, localStartMatrix, False, True, True, RotateOrder.xyz),
    #             (startTransform, endTransform, OpenMaya.MMatrix(), True, False, False, RotateOrder.yzx)
    #     ):
    #         inverseLocalStartMatrix = offset.inverse()
    #
    #         localStartMatrixNode = MultMatrix.create('localStartMatrix#')
    #         localStartMatrixNode.matrixIn.index(0).connectIn(child.worldMatrix)
    #         localStartMatrixNode.matrixIn.index(1).connectIn(parent.worldInverseMatrix)
    #
    #         localStartRotateMatrix = MultMatrix.create('localStartRotateMatrix#')
    #         localStartRotateMatrix.matrixIn.index(0).connectIn(localStartMatrixNode.matrixSum)
    #         localStartRotateMatrix.matrixIn.index(1).set(list(inverseLocalStartMatrix))
    #
    #         localStartRotateMatrixDecomposed = DecomposeMatrix.create('localStartMatrixDecomposed#')
    #         localStartRotateMatrixDecomposed.inputMatrix.connectIn(localStartRotateMatrix.matrixSum)
    #
    #         localStartQuatToEuler = QuatToEuler.create('localStartQuatToEuler#')
    #         localStartQuatToEuler.inputRotateOrder.set(rotateOrder)
    #         localStartQuatToEuler.inputQuat.connectIn(localStartRotateMatrixDecomposed.outputQuat)
    #
    #         localStartRotation = ComposeMatrix.create('localStartRotation#')
    #         if x:
    #             localStartRotation.inputRotateX.connectIn(localStartQuatToEuler.outputRotateX)
    #         if y:
    #             localStartRotation.inputRotateY.connectIn(localStartQuatToEuler.outputRotateY)
    #         if z:
    #             localStartRotation.inputRotateZ.connectIn(localStartQuatToEuler.outputRotateZ)
    #
    #         localStartMatrixDecomposed = DecomposeMatrix.create('localStartMatrixDecomposed#')
    #         localStartMatrixDecomposed.inputMatrix.connectIn(localStartMatrixNode.matrixSum)
    #
    #         localStartTranslateMatrix = ComposeMatrix.create('localStartTranslateMatrix#')
    #         localStartTranslateMatrix.inputTranslate.connectIn(localStartMatrixDecomposed.outputTranslate)
    #
    #         startResultMatrix = MultMatrix.create('startResultMatrix#')
    #         startResultMatrix.matrixIn.index(0).connectIn(localStartRotation.outputMatrix)
    #         startResultMatrix.matrixIn.index(1).set(list(offset))
    #         startResultMatrix.matrixIn.index(2).connectIn(localStartTranslateMatrix.outputMatrix)
    #         startResultMatrix.matrixIn.index(3).connectIn(parent.worldMatrix)
    #
    #         resultMatrices.append(startResultMatrix)
    #
    #     joints = jointChainBetweenTwoMatrices(
    #         startTransform.worldMatrix.get(),
    #         endTransform.worldMatrix.get(),
    #         namePattern=jointNamePattern
    #     )
    #
    #     for index, joint in enumerate(joints):
    #         blender = index / sections
    #         blendMatrix = matrixConstraint((resultMatrices[0].matrixSum, resultMatrices[1].matrixSum), joint)
    #         blendMatrix.blender.set(blender)
    #
    #     return joints

    def build(self):
        # settings ctrl
        settingsCtrlBuffer = cmds.group(empty=True, name='settings_{}_ctlBfr'.format(self))
        settingsCtrl, = cmds.circle(ch=False, name='settings_{}_ctl'.format(self), normal=(1, 0, 0), radius=self.size * 1.5)
        cmds.parent(settingsCtrl, settingsCtrlBuffer)
        self.interfaces.append(settingsCtrl)
        self.controllers.append(settingsCtrl)
        self.children.append(settingsCtrlBuffer)
        cmds.xform(settingsCtrlBuffer, matrix=list(self.hipGuide.matrix))

        # ik joints
        ikJoints = list()
        for index, guide in enumerate((self.hipGuide, self.kneeGuide, self.ankleGuide, self.toesGuide)):
            joint = cmds.joint(name='ik{}_{}_jnt'.format(index, self))
            ikJoints.append(joint)

            if index == 0:
                self.children.append(joint)

            cmds.xform(joint, matrix=list(guide.matrix), worldSpace=True)

        # ik setup
        cmds.makeIdentity(ikJoints[0], rotate=True, apply=True)

        legIkCtrlBuffer = cmds.group(empty=True, name='ikLeg_{}_ctlBfr'.format(self))
        legIkCtrl, = cmds.circle(ch=False, name='ikLeg_{}_ctl'.format(self), normal=(1, 0, 0), radius=self.size)
        cmds.parent(legIkCtrl, legIkCtrlBuffer)
        self.controllers.append(legIkCtrl)
        cmds.xform(legIkCtrlBuffer, matrix=list(self.ankleGuide.matrix))
        legIkHandle, _ = cmds.ikHandle(startJoint=ikJoints[0], endEffector=ikJoints[2], solver='ikRPsolver')
        self.children.append(legIkHandle)

        footIkCtrlBuffer = cmds.group(empty=True, name='ikFoot_{}_ctlBfr'.format(self))
        footIkCtrl, = cmds.circle(ch=False, name='ikFoot_{}_ctl'.format(self), normal=(1, 0, 0), radius=self.size)
        cmds.parent(footIkCtrl, footIkCtrlBuffer)
        self.controllers.append(footIkCtrl)
        cmds.xform(footIkCtrlBuffer, matrix=list(self.toesGuide.matrix))
        footIkHandle, _ = cmds.ikHandle(startJoint=ikJoints[2], endEffector=ikJoints[3], solver='ikSCsolver')
        self.children.append(footIkHandle)

        toesIkCtrlBuffer = cmds.group(empty=True, name='ikToes_{}_ctlBfr'.format(self))
        toesIkCtrl, = cmds.circle(ch=False, name='ikToes_{}_ctl'.format(self), normal=(1, 0, 0), radius=self.size * 1.2)
        cmds.parent(toesIkCtrl, toesIkCtrlBuffer)
        self.controllers.append(toesIkCtrl)
        cmds.xform(toesIkCtrlBuffer, matrix=list(self.toesGuide.matrix))

        cmds.parentConstraint(footIkCtrl, legIkHandle, maintainOffset=True)
        cmds.parentConstraint(footIkCtrl, footIkHandle)
        matrixConstraint((toesIkCtrl,), ikJoints[3], translate=False, rotate=True, scale=True, shear=True)

        self.children.append(legIkCtrlBuffer)

        # reverseFoot setup
        footInIkCtrlBuffer = cmds.group(empty=True, name='ikFootIn_{}_ctlBfr'.format(self))
        footInIkCtrl, = cmds.circle(ch=False, name='ikFootIn_{}_ctl'.format(self), normal=(1, 0, 0), radius=self.size * 0.5)
        cmds.parent(footInIkCtrl, footInIkCtrlBuffer)
        self.controllers.append(footInIkCtrl)
        cmds.xform(footInIkCtrlBuffer, matrix=list(self.footInGuide.matrix))

        footOutIkCtrlBuffer = cmds.group(empty=True, name='ikFootOut_{}_ctlBfr'.format(self))
        footOutIkCtrl, = cmds.circle(ch=False, name='ikFootOut_{}_ctl'.format(self), normal=(1, 0, 0), radius=self.size * 0.5)
        cmds.parent(footOutIkCtrl, footOutIkCtrlBuffer)
        self.controllers.append(footOutIkCtrl)
        cmds.xform(footOutIkCtrlBuffer, matrix=list(self.footOutGuide.matrix))

        footBackIkCtrlBuffer = cmds.group(empty=True, name='ikFootBack_{}_ctlBfr'.format(self))
        footBackIkCtrl, = cmds.circle(ch=False, name='ikFootBack_{}_ctl'.format(self), normal=(1, 0, 0), radius=self.size * 0.5)
        cmds.parent(footBackIkCtrl, footBackIkCtrlBuffer)
        self.controllers.append(footBackIkCtrl)
        cmds.xform(footBackIkCtrlBuffer, matrix=list(self.footBackGuide.matrix))

        footTipIkCtrlBuffer = cmds.group(empty=True, name='ikFootTip_{}_ctlBfr'.format(self))
        footTipIkCtrl, = cmds.circle(ch=False, name='ikFootTip_{}_ctl'.format(self), normal=(1, 0, 0), radius=self.size * 0.5)
        cmds.parent(footTipIkCtrl, footTipIkCtrlBuffer)
        self.controllers.append(footTipIkCtrl)
        cmds.xform(footTipIkCtrlBuffer, matrix=list(self.footTipGuide.matrix))

        cmds.parent(footInIkCtrlBuffer, legIkCtrl)
        cmds.parent(footOutIkCtrlBuffer, footInIkCtrl)
        cmds.parent(footTipIkCtrlBuffer, footOutIkCtrl)
        cmds.parent(footBackIkCtrlBuffer, footTipIkCtrl)

        cmds.parent(footIkCtrlBuffer, footBackIkCtrl)
        cmds.parent(toesIkCtrlBuffer, footBackIkCtrl)

        # fk ctrls
        fkCtrls = list()
        latestCtrl = None
        for index, guide in enumerate((self.hipGuide, self.kneeGuide, self.ankleGuide, self.toesGuide)):
            ctrlBuffer = cmds.group(name='fk{}_{}_ctlBfr'.format(index, self), empty=True)
            ctrl, = cmds.circle(name='fk{}_{}_ctl'.format(index, self), ch=False, radius=self.size, normal=(1, 0, 0))
            fkCtrls.append(ctrl)
            self.controllers.append(ctrl)
            cmds.parent(ctrl, ctrlBuffer)

            if index == 0:
                self.children.append(ctrlBuffer)
            else:
                cmds.parent(ctrlBuffer, latestCtrl)
            latestCtrl = ctrl

            cmds.xform(ctrlBuffer, matrix=list(guide.matrix.normalized()), worldSpace=True)

        # Result Matrices and switch
        switchAttr = 'switchFkIk'
        switchPlug = '{}.{}'.format(settingsCtrl, switchAttr)
        cmds.addAttr(settingsCtrl, longName=switchAttr, min=0, max=1, keyable=True)

        resultMatrices = list()
        for ik, fk in zip(ikJoints, fkCtrls):
            resultMatrix = cmds.createNode('blendMatrix')
            resultMatrices.append(resultMatrix)

            cmds.connectAttr('{}.worldMatrix'.format(fk), '{}.matrices[0].matrix'.format(resultMatrix))
            cmds.connectAttr('{}.worldMatrix'.format(ik), '{}.matrices[1].matrix'.format(resultMatrix))
            cmds.connectAttr(switchPlug, '{}.blender'.format(resultMatrix))

            lct, = cmds.spaceLocator()
            for attr in ('t', 'r', 's'):
                cmds.connectAttr('{}.{}'.format(resultMatrix, attr), '{}.{}'.format(lct, attr))

        # skin joints
        for x in range(self.legSection):
            joint = cmds.joint(name='leg{}_{}_skn'.format(x, self))
            self.influencers.append(joint)
            const = matrixConstraint((ikJoints[0], ikJoints[1]), joint)
            cmds.setAttr('{}.blender'.format(const), float(x) / float(self.legSection))

            if x == 0:
                self.children.append(joint)

        forelegJoints = self.buildForelegSkinJointsSetup(resultMatrices[1], resultMatrices[2])

        ankleJnt = cmds.joint(name='ankle_{}_skn'.format(self))
        self.influencers.append(ankleJnt)
        for attr in ('translate', 'rotate', 'scale', 'shear'):
            cmds.connectAttr('{}.{}'.format(resultMatrices[2], attr), '{}.{}'.format(ankleJnt, attr))
        cmds.connectAttr('{}.parentInverseMatrix'.format(ankleJnt), '{}.parentInverseMatrix'.format(resultMatrices[2]))
        cmds.connectAttr('{}.jointOrient'.format(ankleJnt), '{}.jointOrient'.format(resultMatrices[2]))

        toesJnt = cmds.joint(name='toes_{}_skn'.format(self))
        self.influencers.append(toesJnt)
        for attr in ('translate', 'rotate', 'scale', 'shear'):
            cmds.connectAttr('{}.{}'.format(resultMatrices[3], attr), '{}.{}'.format(toesJnt, attr))
        cmds.connectAttr('{}.parentInverseMatrix'.format(toesJnt), '{}.parentInverseMatrix'.format(resultMatrices[3]))
        cmds.connectAttr('{}.jointOrient'.format(toesJnt), '{}.jointOrient'.format(resultMatrices[3]))

        # cmds.parent(toesJnt, ankleJnt)
        cmds.parent(ankleJnt, forelegJoints[-1])

        self.buildFolder()
