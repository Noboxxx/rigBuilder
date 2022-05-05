from rigBuilder.files.skinFile2 import SkinFile2
from rigBuilder.steps.core import Step
from rigBuilder.types import Node, Choice


class SkinMethod(Choice):
    choices = (
        'index',
        'nearest',
        'barycentric',
        'bilinear',
        'over'
    )


class ImportSkin2(Step):

    def __init__(self, file='', mesh='', method='index'):
        super(ImportSkin2, self).__init__()

        self.file = SkinFile2(file)
        self.mesh = Node(mesh)
        self.method = SkinMethod(method)

    def build(self, workspace=''):
        f = SkinFile2(self.file.replace('...', workspace))
        f.import_(self.mesh, method=self.method)
