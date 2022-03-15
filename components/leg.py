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
