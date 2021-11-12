from .rbMaya.rbMayaComponents import *


def test():
    component = OneCtrl('untitled', 'L', 0)
    print dict(component)
    print component.keys()
    print component.values()
    print component.items()
