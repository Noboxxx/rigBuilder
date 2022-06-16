from __future__ import division
from maya import cmds
from maya.api import OpenMaya
from rigBuilder.components.core import Component, Guide, Storage
from rigBuilder.components.nodeUtils import MultMatrix, DecomposeMatrix, QuatToEuler, RotateOrder, ComposeMatrix, \
    BlendMatrixCustom, Transform, DistanceBetween, MultiplyDivide, BlendColors, Node
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.components.utils2 import controller, distance
from rigBuilder.components.utilss.ikUtils import ikFullStretchSetup, poleVectorMatrix
from rigBuilder.components.utilss.mathUtils import blendMatrices
from rigBuilder.components.utilss.setupUtils import jointChain, ribbon, decomposeMatrix
from rigBuilder.types import UnsignedInt, UnsignedFloat


class Limb(Component):

    aName = str()
    bName = str()
    cName = str()

    abName = str()
    bcName = str()

    def __init__(self, aGuide='', bGuide='', cGuide='', uiGuide='', firstSection=4, secondSection=4, pvDistance=5.0, **kwargs):
        super(Limb, self).__init__(**kwargs)

        self.aGuide = Guide(aGuide)
        self.bGuide = Guide(bGuide)
        self.cGuide = Guide(cGuide)
        self.uiGuide = Guide(uiGuide)

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
        self.uiGuide = self.uiGuide.mirrored()

    def buildSecondSegmentSkinJointsSetup(self, elbowMatrix, wristMatrix):

        inverseMatrix = cmds.createNode('inverseMatrix')
        cmds.connectAttr(elbowMatrix, '{}.inputMatrix'.format(inverseMatrix))

        # Stuff
        localWristMatrix = MultMatrix.create('localWristMatrix#')
        localWristMatrix.matrixIn.index(0).connectIn(wristMatrix)
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
        wristResultMatrix.matrixIn.index(3).connectIn(elbowMatrix)

        return '{}.matrixSum'.format(wristResultMatrix)

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

        return ['{}.matrixSum'.format(m) for m in resultMatrices]

    def ikSetup(self, mainCtrl, switchPlug):
        # joints
        joints = list()
        for index, guide in enumerate((self.aGuide, self.bGuide, self.cGuide)):
            if index == 0:
                cmds.select(mainCtrl)

            joint = cmds.joint(name='ik{}_{}_jnt'.format(index, self))
            joints.append(joint)

            cmds.xform(joint, matrix=list(guide.matrix), worldSpace=True)

        cmds.setAttr('{}.v'.format(joints[0]), False)

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
        cmds.setAttr('{}.v'.format(legIkHandle), False)
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
        cmds.addAttr(self.interfaces[0], longName='minStretch', min=0, defaultValue=1, keyable=True)
        cmds.addAttr(self.interfaces[0], longName='maxStretch', min=0, defaultValue=2, keyable=True)
        cmds.addAttr(self.interfaces[0], longName='pvLock', min=0, max=1, defaultValue=0, keyable=True)
        cmds.addAttr(self.interfaces[0], longName='offStretchA', keyable=True)
        cmds.addAttr(self.interfaces[0], longName='offStretchB', keyable=True)

        elbowStretchPlug, wristStretchPlug = ikFullStretchSetup(
            rootSpaceWorldMatrixPlug='{}.worldMatrix'.format(mainCtrl),
            shoulderCtrlWorldMatrixPlug='{}.worldMatrix'.format(mainCtrl),
            poleVectorCtrlWorldMatrixPlug='{}.worldMatrix'.format(pvCtrl),
            handCtrlWorldMatrixPlug='{}.worldMatrix'.format(legIkCtrl),
            elbowForwardValueOrig=cmds.getAttr('{}.tx'.format(joints[1])),
            wristForwardValueOrig=cmds.getAttr('{}.tx'.format(joints[2])),
            minStretchPlug='{}.minStretch'.format(self.interfaces[0]),
            maxStretchPlug='{}.maxStretch'.format(self.interfaces[0]),
            pvLockPlug='{}.pvLock'.format(self.interfaces[0]),
            offsetAPlug='{}.offStretchA'.format(self.interfaces[0]),
            offsetBPlug='{}.offStretchB'.format(self.interfaces[0])
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

    def resultSetup(self, mainCtrl, fkCtrls, ikJoints, switchPlug):
        freeBBfr, freeBCtrl = controller(
            'free{}_{}_ctl'.format(self.bName.title(), self),
            size=self.bGuide.size * .9,
            matrix=self.bGuide.matrix,
            color=self.color + 100,
            shape='sphere',
            lockAttrs=('ry', 'rz', 'sx', 'sy', 'sz'),
            ctrlParent=mainCtrl,
        )
        self.controllers.append(freeBCtrl)
        self.children.append(freeBBfr)

        resultPlugMatrices = list()
        for index, (ik, fk) in enumerate(zip(ikJoints, fkCtrls)):
            resultMatrix = cmds.createNode('blendMatrixCustom')
            resultPlugMatrices.append('{}.resultMatrix'.format(resultMatrix))

            if index != 1:
                cmds.connectAttr('{}.worldMatrix'.format(fk), '{}.matrices[0].matrix'.format(resultMatrix))
                cmds.connectAttr('{}.worldMatrix'.format(ik), '{}.matrices[1].matrix'.format(resultMatrix))
                cmds.connectAttr(switchPlug, '{}.blender'.format(resultMatrix))
            else:
                b = matrixConstraint((fk, ik), freeBBfr)
                cmds.connectAttr(switchPlug, '{}.blender'.format(b))
                cmds.connectAttr('{}.worldMatrix'.format(freeBCtrl), '{}.matrices[0].matrix'.format(resultMatrix))

            self.outputs.insert(0, '{}.resultMatrix'.format(resultMatrix))

        return resultPlugMatrices

    def ribbonSetup(self, mainCtrl, startMatrixPlug, endMatrixPlug, sections, name, squashStrengthPlug, benderPlug):
        startMatrix = cmds.getAttr(startMatrixPlug)
        endMatrix = cmds.getAttr(endMatrixPlug)

        # Create surface
        surface, matrixPlugs = ribbon(startMatrix, endMatrix, nEdges=3, nOutputs=sections + 1)
        cmds.setAttr('{}.v'.format(surface), False)
        cmds.setAttr('{}.inheritsTransform'.format(surface), False)
        self.children.append(surface)

        # curveFromSurfaceIso
        curveFromSurface = cmds.createNode('curveFromSurfaceIso')
        cmds.setAttr('{}.isoparmDirection'.format(curveFromSurface), 1)
        cmds.connectAttr('{}.local'.format(surface), '{}.inputSurface'.format(curveFromSurface))

        # curveInfo
        curveInfo = cmds.createNode('curveInfo')
        cmds.connectAttr('{}.outputCurve'.format(curveFromSurface), '{}.inputCurve'.format(curveInfo))

        # ratio
        lengthRatio = cmds.createNode('multiplyDivide')
        cmds.connectAttr('{}.arcLength'.format(curveInfo), '{}.input1X'.format(lengthRatio))
        cmds.setAttr('{}.input2X'.format(lengthRatio), cmds.getAttr('{}.arcLength'.format(curveInfo)))
        cmds.setAttr('{}.operation'.format(lengthRatio), 2)

        # Create skin joints
        skinJoints = jointChain(
            startMatrix, endMatrix, nJoints=sections + 1, name='{}<i>_{}_skn'.format(name, self), scaleCompensate=True)
        self.children.append(skinJoints[0])
        self.influencers += skinJoints

        for index, (output, joint) in enumerate(zip(matrixPlugs, skinJoints)):
            pwr = index / (len(skinJoints) - 1)
            if pwr > .5:
                pwr = 1.0 - pwr

            # blender
            blender = cmds.createNode('blendColors')
            cmds.setAttr('{}.color1R'.format(blender), pwr)
            cmds.setAttr('{}.color2R'.format(blender), 0.0)
            cmds.connectAttr(squashStrengthPlug, '{}.blender'.format(blender))

            # power
            powerValue = cmds.createNode('multiplyDivide')
            cmds.setAttr('{}.operation'.format(powerValue), 3)
            cmds.connectAttr('{}.outputR'.format(blender), '{}.input2X'.format(powerValue))
            cmds.connectAttr('{}.outputX'.format(lengthRatio), '{}.input1X'.format(powerValue))

            # div
            divideValue = cmds.createNode('multiplyDivide')
            cmds.setAttr('{}.input1X'.format(divideValue), 1.0)
            cmds.setAttr('{}.operation'.format(divideValue), 2)
            cmds.connectAttr('{}.outputX'.format(powerValue), '{}.input2X'.format(divideValue))

            # cmds.connectAttr('{}.outputX'.format(lengthRatio), '{}.sx'.format(joint))
            cmds.connectAttr('{}.outputX'.format(divideValue), '{}.sy'.format(joint))
            cmds.connectAttr('{}.outputX'.format(divideValue), '{}.sz'.format(joint))

            matrixConstraint((output,), joint, scale=False)
            # matrixConstraint((mainCtrl,), joint, translate=False, rotate=False, shear=False)

        # Driver joints
        driverJoints = list()
        for letter, plug in (('A', startMatrixPlug), ('B', endMatrixPlug)):
            j = cmds.joint(name='{}Driver{}_{}_jnt'.format(name, letter, self))
            cmds.setAttr('{}.inheritsTransform'.format(j), False)
            cmds.setAttr('{}.v'.format(j), False)
            decomposeMatrix(plug, j)
            driverJoints.append(j)
            self.children.append(j)

        # Bender ctrl / joint
        bendBfr, bendCtrl = controller(name='{}Bend_{}_ctl'.format(name, self), shape='sphere',
                                       color=self.color + 100, size=self.bGuide.size, ctrlParent=mainCtrl)
        bendJoint = cmds.joint(name='{}Bend_{}_jnt'.format(name, self))
        self.controllers.append(bendCtrl)
        self.children.append(bendBfr)

        constraint = matrixConstraint(driverJoints, bendBfr)
        cmds.setAttr('{}.blender'.format(constraint), .5)

        # benders
        cmds.connectAttr(benderPlug, '{}.v'.format(bendBfr))

        # Skin Surface
        skinCluster, = cmds.skinCluster(driverJoints[0], bendJoint, driverJoints[1], surface)
        nPointsU = cmds.getAttr('{}.spansU'.format(surface)) + cmds.getAttr('{}.degreeU'.format(surface))
        skinValues = (
            (1.0, 0.0, 0.0),
            (2/3, 1/3, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 1/3, 2/3),
            (0.0, 0.0, 1.0),
        )
        for u in range(nPointsU):
            for v, (a, b, c) in enumerate(skinValues):
                cvPlug = '{}.cv[{}][{}]'.format(surface, u, v)

                cmds.skinPercent(
                    skinCluster,
                    cvPlug,
                    transformValue=[
                        (driverJoints[0], a),
                        (bendJoint, b),
                        (driverJoints[1], c),
                    ],
                )

        return skinJoints

    def skinSetup(self, mainCtrl, resultPlugMatrices):
        # Ribbons and joint chains
        aDriverMPlug, aEndDriverMPlug = self.buildFirstSegmentSkinJointsSetup(
            '{}.worldMatrix'.format(mainCtrl), resultPlugMatrices[0], resultPlugMatrices[1])
        bEndDriverMPlug = self.buildSecondSegmentSkinJointsSetup(resultPlugMatrices[1], resultPlugMatrices[2])

        squashStretchPlugs = list()
        for n in (self.abName, self.bcName):
            squashStretchAttr = 'squashStrength{}'.format(n.title())
            squashStretchPlug = '{}.{}'.format(self.interfaces[0], squashStretchAttr)
            cmds.addAttr(self.interfaces[0], longName=squashStretchAttr, keyable=True, min=0.0)
            squashStretchPlugs.append(squashStretchPlug)

        benderAttr = 'benders'
        benderPlug = '{}.{}'.format(self.interfaces[0], benderAttr)
        if not cmds.objExists(benderPlug):
            cmds.addAttr(self.interfaces[0], longName=benderAttr, attributeType='bool', defaultValue=False, k=True)

        self.ribbonSetup(mainCtrl, aDriverMPlug, aEndDriverMPlug, self.firstSection, self.abName, squashStretchPlugs[0], benderPlug)
        self.ribbonSetup(mainCtrl, resultPlugMatrices[1], bEndDriverMPlug, self.secondSection, self.bcName, squashStretchPlugs[1], benderPlug)

    def build(self):
        # main ctrl
        mainCtrlBuffer, mainCtrl = controller(
            'main_{}_ctl'.format(self), size=self.aGuide.size * 1.25, color=self.color + 100, matrix=self.aGuide.matrix)
        self.controllers.append(mainCtrl)
        self.children.append(mainCtrlBuffer)
        self.inputs.append(mainCtrlBuffer)

        # ui ctrl
        uiBfr, uiCtrl = controller(
            'ui_{}_ctl'.format(self),
            size=self.uiGuide.size,
            matrix=self.uiGuide.matrix,
            color=(0, 255, 255),
            ctrlParent=mainCtrl,
            shape='diamond',
            lockAttrs=[a + x for a in ('t', 'r', 's') for x in ('x', 'y', 'z')]
        )
        self.children.append(uiBfr)
        self.controllers.append(uiCtrl)
        self.interfaces.append(uiCtrl)
        matrixConstraint((mainCtrl,), uiBfr, maintainOffset=True)

        # switch plug
        switchAttr = 'switchFkIk'
        switchPlug = '{}.{}'.format(self.interfaces[0], switchAttr)
        cmds.addAttr(self.interfaces[0], longName=switchAttr, min=0, max=1, keyable=True)

        # ik setup
        ikJoints = self.ikSetup(mainCtrl, switchPlug)[0]

        # fk ctrls
        fkCtrls = self.fkSetup(mainCtrl, switchPlug)[0]

        # Result Matrices and switch
        resultPlugMatrices = self.resultSetup(mainCtrl, fkCtrls, ikJoints, switchPlug)

        # skin joints
        self.skinSetup(mainCtrl, resultPlugMatrices)

        # buildFolder
        self.buildFolder()
