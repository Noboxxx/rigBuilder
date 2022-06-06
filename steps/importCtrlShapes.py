from rigBuilder.files.ctrlShapeFile import CtrlShapeFile
from rigBuilder.steps.core import Step


class ImportCtrlShapes(Step):

    def __init__(self, file=str(), scale=1.0, useColor=True):
        super(ImportCtrlShapes, self).__init__()
        self.file = CtrlShapeFile(file)
        self.scale = float(scale)
        self.useColor = bool(useColor)

    def build(self, workspace=''):
        self.file.import_(scale=self.scale, useColor=self.useColor)

