from .utils import Controller, createBuffer
from maya import cmds
from .core import Component, Guide
from ..types import Matrix


class OneCtrl(Component):

    def __init__(self, guide=str(), **kwargs):
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

    def mirror(self, mirrorAxis='x'):
        super(OneCtrl, self).mirror()
        self.guide = self.guide.mirrored(mirrorAxis=mirrorAxis)

    def createGuides(self, key):
        self.guide = Guide.create(key)
