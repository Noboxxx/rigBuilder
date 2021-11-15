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


class RParameter(object):

    def __mirror__(self):
        return None

    @classmethod
    def __default__(cls):
        return None


class RName(RParameter):

    pattern = r'^[a-zA-Z_][A-Z0-9a-z_]*$'

    def __init__(self, name):
        if not self.isOne(name):
            raise ValueError('The given name \'{}\' is not valid'.format(name))
        self.name = str(name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return str(other) == self.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __mirror__(self):
        return self

    @classmethod
    def isOne(cls, name):
        return re.match(cls.pattern, name)


class RSide(RParameter):

    left = 'L'
    right = 'R'
    center = 'C'

    mirrorTable = {
        left: right,
        right: left,
        center: None
    }

    def __init__(self, side):
        if not self.isOne(side):
            raise ValueError('The given side \'{}\' is not valid'.format(side))
        self.side = str(side)

    def __str__(self):
        return self.side

    def __eq__(self, other):
        return str(other) == str(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __mirror__(self):
        mirroredSide = self.mirrorTable[str(self)]
        if mirroredSide:
            return self.__class__(mirroredSide)
        return None

    def isOne(self, side):
        return str(side) in self.mirrorTable


class RIndex(RParameter):

    def __init__(self, index):
        if not self.isOne(index):
            raise ValueError('The given index \'{}\' is not valid'.format(index))
        self.index = int(index)

    def __eq__(self, other):
        return int(other) == self.index

    def __ne__(self, other):
        return not self.__eq__(other)

    def __mirror__(self):
        return self

    @classmethod
    def isOne(cls, index):
        return int(index) >= 0


class RMayaComponent(RComponent):

    shortTypeName = 'cmpnt'

    name = None  # for autocompletion only
    side = None  # for autocompletion only
    index = None  # for autocompletion only

    parameters = dict(
        name=RName,
        side=RSide,
        index=RIndex,
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
