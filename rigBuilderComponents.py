from . import rigBuilderCore
from maya import cmds


ctrlTypeStr = 'ctrl'
ctrlBufferTypeStr = 'ctrlBuffer'
componentFolder = 'cmpnt'

defaultGuide = None


class MayaComponent(rigBuilderCore.Component):

    def create(self):
        raise NotImplementedError

    def finalizeCreation(self, rootDags, ctrls):
        super(MayaComponent, self).finalizeCreation(ctrls)
        folderName = self.formatObjectName(type=componentFolder)
        folder = cmds.group(empty=True, name=folderName)
        if rootDags:
            cmds.parent(rootDags, folder)


class OneCtrl(MayaComponent):

    def setGuides(self, guide=defaultGuide):
        self.guides = guide

    def create(self):
        ctrlName = self.formatObjectName(prefix=None, type=ctrlTypeStr)
        ctrl, = cmds.circle(name=ctrlName, constructionHistory=False)

        ctrlBufferName = self.formatObjectName(prefix=None, type=ctrlBufferTypeStr)
        ctrlBuffer = cmds.group(empty=True, name=ctrlBufferName)

        cmds.parent(ctrl, ctrlBuffer)

        self.finalizeCreation([ctrlBufferName], [ctrl])


class Arm(MayaComponent):

    def create(self):
        self.finalizeCreation([], [])
