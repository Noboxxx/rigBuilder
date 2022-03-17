from maya import cmds
from rigBuilder.components.core import Guide
from rigBuilder.components.limb import Limb, poleVectorMatrix
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.components.utils2 import controller


class Leg(Limb):

    aName = 'hip'
    bName = 'knee'
    cName = 'ankle'

    abName = 'leg'
    bcName = 'foreleg'

    def __init__(self, toesGuide='', footTipGuide='', footBackGuide='', footInGuide='', footOutGuide='', **kwargs):
        super(Leg, self).__init__(**kwargs)

        self.footTipGuide = Guide(footTipGuide)
        self.footBackGuide = Guide(footBackGuide)
        self.footInGuide = Guide(footInGuide)
        self.footOutGuide = Guide(footOutGuide)
        self.toesGuide = Guide(toesGuide)

    def mirror(self):
        super(Leg, self).mirror()
        self.footTipGuide = self.footTipGuide.mirrored()
        self.footBackGuide = self.footBackGuide.mirrored()
        self.footInGuide = self.footInGuide.mirrored()
        self.footOutGuide = self.footOutGuide.mirrored()
        self.toesGuide = self.toesGuide.mirrored()

    def ikSetup(self, mainCtrl, switchPlug):
        joints, legIkCtrlBuffer, legIkCtrl, legIkHandle = super(Leg, self).ikSetup(mainCtrl, switchPlug)

        #
        constraints = [n for n in cmds.listHistory(legIkHandle, levels=1) if cmds.objectType(n, isAType='parentConstraint')]
        cmds.delete(constraints)

        # joints
        cmds.select(joints[-1])

        joint = cmds.joint(name='ik{}_{}_jnt'.format(len(joints), self))
        joints.append(joint)

        cmds.xform(joint, matrix=list(self.toesGuide.matrix), worldSpace=True)

        #
        footIkCtrlBuffer, footIkCtrl = controller(
            'ikFoot_{}_ctl'.format(self), size=self.size, matrix=self.toesGuide.matrix, color=self.color - 100,
            ctrlParent=legIkCtrl, visParent=switchPlug, normal=(0, 0, 1))
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

        return joints, legIkCtrlBuffer, legIkCtrl, legIkHandle

    def fkSetup(self, mainCtrl, switchPlug):
        ctrls, reverseNode = super(Leg, self).fkSetup(mainCtrl, switchPlug)

        ctrlBuffer, ctrl = controller(
            'fk{}_{}_ctl'.format(len(ctrls), self), size=self.size, matrix=list(self.toesGuide.matrix.normalized()),
            color=self.color, ctrlParent=ctrls[-1], visParent='{}.outputX'.format(reverseNode))
        cmds.parent(ctrlBuffer, ctrls[-1])
        ctrls.append(ctrl)

        return ctrls, reverseNode

    def skinSetup(self, mainCtrl, resultMatrices):
        skinJoints = super(Leg, self).skinSetup(mainCtrl, resultMatrices)

        toesJnt = cmds.joint(name='toes_{}_skn'.format(self))
        cmds.setAttr('{}.segmentScaleCompensate'.format(toesJnt), False)
        self.influencers.append(toesJnt)
        for attr in ('translate', 'rotate', 'scale', 'shear'):
            cmds.connectAttr('{}.{}'.format(resultMatrices[3], attr), '{}.{}'.format(toesJnt, attr))
        cmds.connectAttr('{}.parentInverseMatrix'.format(toesJnt), '{}.parentInverseMatrix'.format(resultMatrices[3]))
        cmds.connectAttr('{}.jointOrient'.format(toesJnt), '{}.jointOrient'.format(resultMatrices[3]))

        cmds.parent(toesJnt, skinJoints[-1])

        return skinJoints + [toesJnt]

    def createGuides(self, name):
        self.aGuide = Guide.create('{}Hip'.format(name))
        self.bGuide = Guide.create('{}Knee'.format(name))
        self.cGuide = Guide.create('{}Ankle'.format(name))

        self.toesGuide = Guide.create('{}Toes'.format(name))

        self.footTipGuide = Guide.create('{}FootTip'.format(name))
        self.footBackGuide = Guide.create('{}FootBack'.format(name))
        self.footInGuide = Guide.create('{}FootIn'.format(name))
        self.footOutGuide = Guide.create('{}FootOut'.format(name))

        cmds.parent(self.cGuide, self.bGuide)
        cmds.parent(self.bGuide, self.aGuide)
        cmds.parent(self.toesGuide, self.cGuide)

        cmds.parent(
            self.footTipGuide,
            self.footBackGuide,
            self.footInGuide,
            self.footOutGuide,
            self.cGuide
        )

        # aGuide
        cmds.setAttr('{}.rx'.format(self.aGuide), -90)
        cmds.setAttr('{}.ry'.format(self.aGuide), -5)
        cmds.setAttr('{}.rz'.format(self.aGuide), -90)

        # bGuide
        cmds.setAttr('{}.tx'.format(self.bGuide), 10)
        cmds.setAttr('{}.ty'.format(self.bGuide), lock=True)
        cmds.setAttr('{}.tz'.format(self.bGuide), lock=True)

        cmds.setAttr('{}.rx'.format(self.bGuide), lock=True)
        cmds.setAttr('{}.ry'.format(self.bGuide), lock=True)
        cmds.setAttr('{}.rz'.format(self.bGuide), 10)

        # cGuide
        cmds.setAttr('{}.tx'.format(self.cGuide), 10)
        cmds.setAttr('{}.ty'.format(self.cGuide), lock=True)
        cmds.setAttr('{}.tz'.format(self.cGuide), lock=True)

        cmds.setAttr('{}.rz'.format(self.cGuide), -95)

        # toesGuide
        cmds.setAttr('{}.tx'.format(self.toesGuide), 5)
        cmds.setAttr('{}.ty'.format(self.toesGuide), lock=True)
        cmds.setAttr('{}.tz'.format(self.toesGuide), lock=True)

        # footTip
        cmds.setAttr('{}.ty'.format(self.footTipGuide), 1)
        cmds.setAttr('{}.tx'.format(self.footTipGuide), 5)

        cmds.setAttr('{}.rx'.format(self.footTipGuide), -180)
        cmds.setAttr('{}.ry'.format(self.footTipGuide), -90)

        # footBack
        cmds.setAttr('{}.ty'.format(self.footBackGuide), 1)

        cmds.setAttr('{}.rx'.format(self.footBackGuide), -180)
        cmds.setAttr('{}.ry'.format(self.footBackGuide), -90)

        # footIn
        cmds.setAttr('{}.tx'.format(self.footInGuide), 5)
        cmds.setAttr('{}.ty'.format(self.footInGuide), 1)
        cmds.setAttr('{}.tz'.format(self.footInGuide), -1)

        cmds.setAttr('{}.rx'.format(self.footInGuide), -180)
        cmds.setAttr('{}.ry'.format(self.footInGuide), -90)

        # footOut
        cmds.setAttr('{}.tx'.format(self.footOutGuide), 5)
        cmds.setAttr('{}.ty'.format(self.footOutGuide), 1)
        cmds.setAttr('{}.tz'.format(self.footOutGuide), 1)

        cmds.setAttr('{}.rx'.format(self.footOutGuide), -180)
        cmds.setAttr('{}.ry'.format(self.footOutGuide), -90)

        cmds.select(self.aGuide)
