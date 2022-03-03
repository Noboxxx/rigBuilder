from .utils import Controller, createBuffer
from maya import cmds
from .core import Component


class Base(Component):

    def build(self):
        # World Ctrl
        worldCtrl = Controller.create(
            name='world_{}_ctl'.format(self),
            color=self.color,
            size=self.size,
            normal=(0.0, 1.0, 0.0)
        )
        worldSkinJoint = cmds.joint(name='world_{}_skn'.format(self))
        worldCtrlBuffer = createBuffer(worldCtrl)

        # Local Ctrl
        localCtrl = Controller.create(
            name='local_{}_ctl'.format(self),
            color=self.color + 150,
            size=self.size * 0.8,
            normal=(0.0, 1.0, 0.0)
        )
        localSkinJoint = cmds.joint(name='local_{}_skn'.format(self))
        localCtrlBuffer = createBuffer(localCtrl)

        # Parent ctrls together
        cmds.parent(localCtrlBuffer, worldCtrl)

        # fill up
        self.interface = worldCtrl
        self.children.append(worldCtrlBuffer)
        self.influencers += [worldSkinJoint, localSkinJoint]
        self.outputs += [localCtrl, worldCtrl]

        self.buildFolder()
