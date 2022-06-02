from rigBuilder.files.ctrlShapeFile import CtrlShapeFile
from rigBuilder.steps.core import Step


class ImportCtrlShapes(Step):

    def __init__(self, file=str(), scale=1.0):
        super(ImportCtrlShapes, self).__init__()
        self.file = CtrlShapeFile(file)
        self.scale = float(scale)

    def build(self, workspace=''):
        self.file.import_(scale=self.scale)

