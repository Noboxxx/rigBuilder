from rigBuilder.files.skinFile import SkinFile
from rigBuilder.steps.core import Step


class ImportSkin(Step):

    def __init__(self, file=''):
        super(ImportSkin, self).__init__()
        self.file = SkinFile(file)

    def build(self, workspace=''):
        f = SkinFile(self.file.replace('...', workspace))
        f.import_()
