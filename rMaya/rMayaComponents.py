from .. import rCore
from maya import cmds
from . import rMayaParameters


class BaseMayaComponent(rCore.BaseComponent):

    name = rCore.ParameterHint(rMayaParameters.Name, rMayaParameters.Name('untitled'))
    side = rCore.ParameterHint(rMayaParameters.Side, rMayaParameters.Side('C'))
    index = rCore.ParameterHint(int, 0)

    shorType = 'cmpnt'
    folderNamePattern = '{name}_{side}_{index}_{shorType}'

    def __init__(self, **kwargs):
        super(BaseMayaComponent, self).__init__(**kwargs)

        self.folder = None
        self.rootDags = list()

    def _initializeCreation(self):
        folderName = self.folderNamePattern.format(
            name=self.name,
            side=self.side,
            index=self.index,
            shorType=self.shorType
        )
        if cmds.objExists(folderName):
            raise RuntimeError('A folder named \'{}\' already exists.'.format(folderName))

        self.folder = cmds.group(empty=True, name=folderName)

    def _finalizeCreation(self):
        if self.rootDags:
            cmds.parent(self.rootDags, self.folder)


class OneCtrl(BaseMayaComponent):

    matrix = rCore.ParameterHint(int, 0)

    def _doCreation(self):
        ctrlBuffer = cmds.group(empty=True)
        ctrl = cmds.circle()
        cmds.parent(ctrl, ctrlBuffer)

        self.rootDags.append(ctrlBuffer)
