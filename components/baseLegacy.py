import os
from maya import cmds
from rigBuilder.components.core import Component
from rigBuilder.types import Node
from rigBuilder.components.utils2 import scaleController


class Nodes(list):

    def __init__(self, seq=None):
        super(Nodes, self).__init__(list() if seq is None else [Node(i) for i in seq])


class BaseLegacy(Component):

    def __init__(self, size=1.0, geometryDags=None, **kwargs):
        super(BaseLegacy, self).__init__(**kwargs)

        self.size = size
        self.geometryDags = Nodes(geometryDags if geometryDags is not None else ('geometry',))

        self.globalBfr = 'global_C0_srt'
        self.globalCtrl = 'global_C0_ctl'
        self.localCtrl = 'local_C0_ctl'
        self.orientCamCtrl = 'orient_cam_C0_ctl'
        self.infoCtrl = 'info_C0_ctl'
        self.infoCtrlBuffer = 'info_C0_srt'
        self.cogMasterCtrl = 'cog_master_C0_ctl'
        self.cogCtrl = 'cog_C0_ctl'
        self.cogJnt = 'cog_guide_C0_jnt'

    def build(self):
        currentDirectory = os.path.dirname(os.path.realpath(__file__))
        cmds.file('{}/src/baseLegacy.ma'.format(currentDirectory), i=True)

        # resize ctrls
        ctrls = [
            self.globalCtrl,
            self.localCtrl,
            self.orientCamCtrl,
            self.infoCtrl,
            self.cogMasterCtrl,
            self.cogCtrl
        ]

        # scaling setting ctrls
        for ctrl in ctrls:
            cmds.controller(ctrl)
            scaleController(ctrl, self.size)

        # parenting controllers
        cmds.controller(self.localCtrl, self.globalCtrl, p=True)
        cmds.controller(self.orientCamCtrl, self.localCtrl, p=True)
        cmds.controller(self.cogMasterCtrl, self.orientCamCtrl, p=True)
        cmds.controller(self.cogCtrl, self.cogMasterCtrl, p=True)
        cmds.controller(self.infoCtrl, self.globalCtrl, p=True)

        # moving info ctrl
        cmds.setAttr('{}.tz'.format(self.infoCtrlBuffer), self.size * 8)

        #
        self.children.append(self.globalBfr)
        self.controllers += ctrls
        self.outputs.append(self.cogCtrl)
        self.influencers.append(self.cogJnt)
        self.interfaces.append(self.infoCtrl)

        # geometry
        for node in self.geometryDags:
            # connect mesh vis
            cmds.connectAttr('{}.Mesh'.format(self.infoCtrl), '{}.v'.format(node), force=True)

            # connect mesh smooth
            for mesh in cmds.listRelatives(node, allDescendents=True, type='mesh') or list():
                cmds.connectAttr('{}.smooth'.format(self.infoCtrl), '{}.smoothLevel'.format(mesh), force=True)

        self.buildFolder()
