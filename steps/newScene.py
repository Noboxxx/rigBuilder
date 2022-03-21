from .core import Step
from maya import cmds


class NewScene(Step):

    def build(self):
        # old scene name
        sceneName = cmds.file(q=True, sn=True)
        sceneType = cmds.file(q=True, type=True)
        print sceneName, sceneType

        perspMatrix = cmds.xform('persp', q=True, matrix=True)

        # new scene
        cmds.file(new=True, force=True)

        # restore
        if sceneName:
            cmds.file(rename=sceneName)
        cmds.file(type=sceneType[0])

        cmds.xform('persp', matrix=perspMatrix)
