from .core import Step
from ..files.core import JsonFile


class BuildComponents(Step):

    def __init__(self, file=str(), **kwargs):
        super(BuildComponents, self).__init__(**kwargs)
        self.file = JsonFile(file)

    def build(self):
        self.file.load().build()
