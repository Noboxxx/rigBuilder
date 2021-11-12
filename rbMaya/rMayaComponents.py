from ..rCore import *
from ..rUtils import *
import re
from maya import cmds


def checkName(value):
    pattern = r'^[a-zA-Z_][A-Z0-9a-z_]*$'

    if not re.match(pattern, value):
        raise ValueError('The given name \'{}\' is not valid'.format(value))


def checkSide(value):
    if value not in RSide.mirrorTable:
        raise ValueError('The given side \'{}\' is not part of {}'.format(value, RSide.mirrorTable.keys()))


def mirrorSide(value):
    if value not in RSide.mirrorTable:
        return None

    return RSide.mirrorTable[value]


class RMayaComponent(RComponent):

    shortTypeName = 'cmpnt'

    parameters = dict(
        name=(None, checkName, None),
        side=(RSide.center, checkSide, mirrorSide),
        index=(0, None, None),
        color=(RColor.yellow, None, None)
    )

    def __init__(self, **kwargs):
        super(RMayaComponent, self).__init__(**kwargs)

        self.folder = None
        self.rootDags = list()

    def _initializeCreation(self):
        """
        Create the folder
        :return:
        """
        if self.folder is not None:
            raise RuntimeError('The component has already been created')

        folderName = '{}_{}_{}_{}'.format(self.name, self.side, self.index, self.shortTypeName)

        if cmds.objExists(folderName):
            raise RuntimeError('The folder \'{}\' already exists'.format(folderName))

        self.folder = cmds.group(empty=True, name=folderName)

    def _doCreation(self):
        ctrl, = cmds.circle(name=self.composeObjectName('plop', 'ctrl'), constructionHistory=False)
        self.rootDags.append(ctrl)

    def _finalizeCreation(self):
        """
        Store useful info into the folder
        :return:
        """
        print '_finalizeCreation'
        cmds.parent(self.rootDags, self.folder)

    def composeObjectName(self, name, objectType):
        return '{}_{}_{}_{}_{}'.format(name, self.name, self.side, self.index, objectType)


class ROneCtrl(RMayaComponent):
    pass
