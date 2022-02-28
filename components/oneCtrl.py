from .utils import Controller, createBuffer
from maya import cmds
from .core import Component, Guide


class OneCtrl(Component):

    def __init__(self, guide='', **kwargs):
        super(OneCtrl, self).__init__(**kwargs)
        self.guide = Guide(guide)

    def build(self):
        ctrl = Controller.create(name='{}_ctrl'.format(self), color=self.color, size=self.size)
        skinJoint = cmds.joint(name='{}_skn'.format(self))
        ctrlBuffer = createBuffer(ctrl)
        cmds.xform(ctrlBuffer, matrix=list(self.guide.matrix))

        self.interface = ctrl
        self.influencers.append(skinJoint)
        self.inputs.append(ctrlBuffer)
        self.controllers.append(ctrl)
        self.children.append(ctrlBuffer)

        self.buildFolder()
