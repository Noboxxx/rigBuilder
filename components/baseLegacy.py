import os
from maya import cmds
from rigBuilder.components.core import Component
from rigBuilder.components.utils2 import scaleController


class BaseLegacy(Component):

    def __init__(self, **kwargs):
        super(BaseLegacy, self).__init__(**kwargs)

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

        self.buildFolder()
