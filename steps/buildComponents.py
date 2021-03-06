from .core import Step
from ..files.core import JsonFile


class ComponentBuilderFile(JsonFile):
    pass


class BuildComponents(Step):

    def __init__(self, file=str(), controlSet=True, **kwargs):
        super(BuildComponents, self).__init__(**kwargs)
        self.file = ComponentBuilderFile(file)
        self.controlSet = bool(controlSet)

    def build(self, workspace=''):
        f = ComponentBuilderFile(self.file.replace('...', workspace))
        f.load().build(controlSet=self.controlSet)
