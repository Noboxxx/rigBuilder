from maya import cmds
from rigBuilder.components.core import Component, Guide
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.components.utils2 import controller


class Clavicle(Component):

    def __init__(self, clavicleGuide='', shoulderGuide='', **kwargs):
        super(Clavicle, self).__init__(**kwargs)

        self.clavicleGuide = Guide(clavicleGuide)
        self.shoulderGuide = Guide(shoulderGuide)

    def mirror(self):
        super(Clavicle, self).mirror()
        self.clavicleGuide = self.clavicleGuide.mirrored()
        self.shoulderGuide = self.shoulderGuide.mirrored()

    def build(self):
        shoulderMatrix = list(self.clavicleGuide.matrix)[:12] + list(self.shoulderGuide.matrix)[12:]

        fkBfr, fkCtrl = controller(
            'fk_{}_ctl'.format(self), size=self.size, color=self.color, matrix=self.clavicleGuide.matrix)
        self.inputs.append(fkBfr)
        self.interfaces.append(fkCtrl)
        self.controllers.append(fkCtrl)

        ikBfr, ikCtrl = controller(
            'ik_{}_ctl'.format(self), size=self.size, color=self.color, matrix=shoulderMatrix, shape='cube')
        cmds.setAttr('{}.r'.format(ikCtrl), lock=True, keyable=False)
        cmds.setAttr('{}.s'.format(ikCtrl), lock=True, keyable=False)
        self.controllers.append(ikCtrl)

        cmds.parent(ikBfr, fkCtrl)
        self.children.append(fkBfr)

        clavicleJnt = cmds.joint(name='start_{}_skn'.format(self))
        cmds.xform(clavicleJnt, matrix=list(self.clavicleGuide.matrix), worldSpace=True)
        cmds.setAttr('{}.segmentScaleCompensate'.format(clavicleJnt), False)

        shoulderJnt = cmds.joint(name='end_{}_skn'.format(self))
        cmds.xform(shoulderJnt, matrix=shoulderMatrix, worldSpace=True)
        cmds.setAttr('{}.segmentScaleCompensate'.format(shoulderJnt), False)

        self.children.append(clavicleJnt)

        self.outputs.append(shoulderJnt)
        self.outputs.append(clavicleJnt)

        ikHandle, _ = cmds.ikHandle(startJoint=clavicleJnt, endEffector=shoulderJnt, solver='ikSCsolver')
        self.children.append(ikHandle)

        matrixConstraint((fkCtrl,), clavicleJnt, rotate=False)
        matrixConstraint((ikCtrl,), ikHandle)

        self.buildFolder()
