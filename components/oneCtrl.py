from .utils import Controller, createBuffer
from maya import cmds
from .core import Component
from ..types import Matrix


class OneCtrl(Component):

    def __init__(self, matrix=None, **kwargs):
        super(OneCtrl, self).__init__(**kwargs)
        self.matrix = Matrix() if matrix is None else Matrix(*matrix)

    def build(self):
        ctrl = Controller.create(name='{}_ctrl'.format(self), color=self.color, size=self.size)
        skinJoint = cmds.joint(name='{}_skn'.format(self))
        ctrlBuffer = createBuffer(ctrl)
        cmds.xform(ctrlBuffer, matrix=list(self.matrix))

        self.influencers.append(skinJoint)
        self.inputs.append(ctrlBuffer)
        self.interface = ctrl
        self.controllers.append(ctrl)
        self.children.append(ctrlBuffer)

        self.buildFolder()

    def mirror(self, mirrorAxis='x'):
        super(OneCtrl, self).mirror()
        self.matrix = self.matrix.mirrored(mirrorAxis=mirrorAxis)

    def createGuide(self, key):
        cmds.spaceLocator(name='{}_guide'.format(key))