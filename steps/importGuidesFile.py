from RBuild.steps.core import Step
import os
from rigBuilder.files.guidesFile import GuidesFile


class ImportGuidesFile(Step):

    def __init__(self, file=str(), **kwargs):
        super(ImportGuidesFile, self).__init__(**kwargs)
        self.file = GuidesFile(os.path.normpath(file))

    def build(self):
        self.file.import_()