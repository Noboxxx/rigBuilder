from maya import cmds
from rigBuilder.steps.core import Step
from rigBuilder.steps.importMayaFile import MayaFile


class Enum(int):

    ls = list()

    def __init__(self, value):
        super(Enum, self).__init__(value)

    def __repr__(self):
        return self

    def __str__(self):
        return self.ls[self]


class MayaFileType(Enum):

    ls = (
        'mayaAscii',
        'mayaBinary',
    )


class ExportFile(Step):

    def __init__(self, file='', force=False, type=0, **kwargs):
        super(ExportFile, self).__init__(**kwargs)

        self.file = MayaFile(file)
        self.force = bool(force)
        self.type = MayaFileType(type)

    def build(self, workspace=''):
        f = MayaFile(self.file.replace('...', workspace))

        sceneName = cmds.file(q=True, sn=True)
        sceneType = cmds.file(q=True, type=True)[0]

        cmds.file(rename=f)
        cmds.file(type=str(self.type))
        cmds.file(save=True)

        cmds.file(rename=sceneName if sceneName else None)
        cmds.file(type=sceneType)
