from ..rCore import *
from ..rUtils import *
import re


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

    parameters = dict(
        name=(None, checkName, None),
        side=(RSide.center, checkSide, mirrorSide),
        index=(0, None, None),
        color=(RColor.yellow, None, None)
    )

    def _initializeCreation(self):
        print '_initializeCreation'

    def _doCreation(self):
        print '_doCreation'

    def _finalizeCreation(self):
        print '_finalizeCreation'


class ROneCtrl(RMayaComponent):
    pass
