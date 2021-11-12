from .rbMaya.rMayaComponents import *
from .rUtils import *


def test():
    component = ROneCtrl(name='untitled', side=RSide.left)  # , side=RSide.left, index=0)
    mirroredComponent = component.getMirror()
    print component.asdict()
    print mirroredComponent.asdict()

    print component.create()
    print mirroredComponent.create()
