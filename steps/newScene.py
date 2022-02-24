from .core import Step
from maya import cmds


class NewScene(Step):

    def build(self):
        cmds.file(new=True, force=True)
