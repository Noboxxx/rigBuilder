from maya import cmds
from .core import Component
from .utils import matrixConstraint
from .utils2 import controller


class Base(Component):

    def build(self):
        # World Ctrl
        worldCtrlBuffer, worldCtrl = controller(
            'world_{}_ctl'.format(self), color=self.color + 100, size=self.size, normal=(0, 1, 0))
        self.interfaces.append(worldCtrl)
        self.children.append(worldCtrlBuffer)
        self.controllers.append(worldCtrl)
        worldSkinJoint = cmds.joint(name='world_{}_skn'.format(self))
        self.children.append(worldSkinJoint)
        self.influencers.append(worldSkinJoint)
        matrixConstraint((worldCtrl,), worldSkinJoint)

        # Local Ctrl
        localCtrlBuffer, localCtrl = controller(
            'local_{}_ctl'.format(self), color=self.color, size=self.size * 0.8, normal=(0, 1, 0))
        self.controllers.append(localCtrl)
        localSkinJoint = cmds.joint(name='local_{}_skn'.format(self))
        self.influencers.append(localSkinJoint)
        matrixConstraint((localCtrl,), localSkinJoint)

        # Parent ctrls together
        cmds.parent(localCtrlBuffer, worldCtrl)
        cmds.parent(localSkinJoint, worldSkinJoint)

        # fill up
        self.outputs += localCtrl, worldCtrl

        self.buildFolder()
