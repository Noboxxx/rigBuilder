from .utils import matrixConstraint
from maya import cmds
from .core import Component, Guide
from .utils2 import controller


class OneCtrl(Component):

    def __init__(self, guide='', **kwargs):
        super(OneCtrl, self).__init__(**kwargs)
        self.guide = Guide(guide)

    def build(self):
        bfr, ctrl = controller('{}_ctl'.format(self), color=self.color, size=self.size, matrix=self.guide.matrix)
        skinJoint = cmds.joint(name='{}_skn'.format(self))
        matrixConstraint((ctrl,), skinJoint)

        self.interfaces.append(ctrl)
        self.influencers.append(skinJoint)
        self.inputs.append(bfr)
        self.outputs.append(ctrl)
        self.controllers.append(ctrl)
        self.children.append(bfr)

        self.buildFolder()

    def mirror(self):
        super(OneCtrl, self).mirror()
        self.guide = self.guide.mirrored()

    def createGuides(self, name):
        self.guide = Guide.create(name)