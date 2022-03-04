from .utils import Controller, createBuffer
from maya import cmds
from .core import Component, Guide


class OneCtrl(Component):

    def __init__(self, guide='', **kwargs):
        super(OneCtrl, self).__init__(**kwargs)
        self.guide = Guide(guide)

    def build(self):
        ctrl = Controller.create(name='{}_ctl'.format(self), color=self.color, size=self.size)
        skinJoint = cmds.joint(name='{}_skn'.format(self))
        ctrlBuffer = createBuffer(ctrl)
        cmds.xform(ctrlBuffer, matrix=list(self.guide.matrix))

        self.interfaces.append(ctrl)
        self.influencers.append(skinJoint)
        self.inputs.append(ctrlBuffer)
        self.outputs.append(ctrl)
        self.controllers.append(ctrl)
        self.children.append(ctrlBuffer)

        self.buildFolder()

    def mirror(self):
        super(OneCtrl, self).mirror()
        self.guide = self.guide.mirrored()
