from rigBuilder.steps.core import Step
import os
from rigBuilder.files.guidesFile import GuidesFile


class ImportGuidesFile(Step):

    def __init__(self, file=str(), **kwargs):
        super(ImportGuidesFile, self).__init__(**kwargs)
        self.file = GuidesFile(file)

    def build(self, workspace=''):
        f = GuidesFile(self.file.replace('...', workspace))
        f.import_()
