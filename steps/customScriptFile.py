from rigBuilder.steps.core import Step
from rigBuilder.types import File


class PythonFile(File):
    pass


class CustomScriptFile(Step):

    def __init__(self, file=''):
        super(CustomScriptFile, self).__init__()
        self.file = PythonFile(file)

    def build(self):
        execfile(self.file)
