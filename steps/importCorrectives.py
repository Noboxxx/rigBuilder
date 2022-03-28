from rigBuilder.files.blendShapeFile import BlendShapeFile
from rigBuilder.steps.core import Step
from rigBuilder.types import File


class ImportCorrectives(Step):

    def __init__(self, shapeFile='', driverFile='', **kwargs):
        super(ImportCorrectives, self).__init__(**kwargs)

        self.shapeFile = BlendShapeFile(shapeFile)
        self.driverFile = File(driverFile)

    def build(self):
        self.shapeFile.import_()
