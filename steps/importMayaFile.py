from rigBuilder.steps.core import Step
from maya import cmds
from rigBuilder.types import Path


class MayaFile(Path):

    def import_(self):
        cmds.file(self, i=True)


class ImportMayaFile(Step):

    def __init__(self, file=str(), **kwargs):
        super(ImportMayaFile, self).__init__(**kwargs)
        self.file = MayaFile(file)

    def build(self, workspace=''):
        f = MayaFile(self.file.replace('...', workspace))
        f.import_()
