from RBuild.steps.core import Step
from maya import cmds
import os


class MayaFile(str):

    def import_(self):
        cmds.file(self, i=True)


class ImportMayaFile(Step):

    def __init__(self, file=str(), **kwargs):
        super(ImportMayaFile, self).__init__(**kwargs)
        self.file = MayaFile(os.path.normpath(file))

    def build(self):
        self.file.import_()
