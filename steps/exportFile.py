from maya import cmds
from rigBuilder.steps.core import Step
from rigBuilder.steps.importMayaFile import MayaFile


class ExportFile(Step):

    def __init__(self, file='', force=False, type='mayaAscii', **kwargs):
        super(ExportFile, self).__init__(**kwargs)

        self.file = MayaFile(file)
        self.force = bool(force)
        self.type = str(type)

    def build(self, workspace=''):
        f = MayaFile(self.file.replace('...', workspace))

        sceneName = cmds.file(q=True, sn=True)
        sceneType = cmds.file(q=True, type=True)[0]

        cmds.file(rename=f)
        cmds.file(type=str(self.type))
        cmds.file(save=True)

        cmds.file(rename=sceneName if sceneName else None)
        cmds.file(type=sceneType)
