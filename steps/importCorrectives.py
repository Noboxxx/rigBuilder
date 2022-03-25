from maya import cmds
from rigBuilder.steps.core import Step
from rigBuilder.types import File


class ImportCorrectives(Step):

    def __init__(self, shapeFile='', driverFile='', **kwargs):
        super(ImportCorrectives, self).__init__(**kwargs)

        self.shapeFile = File(shapeFile)
        self.driverFile = File(driverFile)

    def build(self):
        mesh = 'pr_clothes_C0_geo'
        cmds.select(mesh)
        bs, = cmds.blendShape(automatic=True)
        cmds.blendShape(bs, e=True, ip=self.shapeFile)
        print bs
