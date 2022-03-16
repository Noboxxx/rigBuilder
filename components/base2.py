from maya import cmds
from rigBuilder.components.core import Component
from rigBuilder.components.utils2 import scaleController


class Base2(Component):

    def __init__(self, **kwargs):
        super(Base2, self).__init__(**kwargs)

        self.globalCtrl = 'global_C0_ctl'
        self.localCtrl = 'local_C0_ctl'
        self.orientCamCtrl = 'orient_cam_C0_ctl'
        self.infoCtrl = 'info_C0_ctl'
        self.infoCtrlBuffer = 'info_C0_srt'
        self.cogMasterCtrl = 'cog_master_C0_ctl'
        self.cogCtrl = 'cog_C0_ctl'

    def build(self):
        cmds.file('C:/Users/plaurent/Desktop/base_hierarchy_cleaned.ma', i=True)

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
        self.children.append('global_C0_srt')
        self.controllers += ctrls
        self.outputs.append('cog_C0_ctl')
        self.influencers.append('cog_guide_C0_jnt')
        self.interfaces.append('info_C0_ctl')

        self.buildFolder()
