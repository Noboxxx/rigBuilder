from __future__ import division
from PySide2 import QtWidgets
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance


def getMayaMainWindow():
    """
    Get the beloved main window of Maya as a QMainWindow.
    """
    pointer = MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtWidgets.QMainWindow)


def deleteSiblingWidgets(widget):
    """
    Delete widgets with the same type and parent as the given widget
    """
    parent = widget.parent()

    if not parent:
        return

    for child in parent.children():
        if child == widget:
            continue
        if str(type(child)) != str(type(widget)):
            continue
        child.deleteLater()


def size(value):
    """
    Multiply the given value by the ratio of the current dpi and the standard dpi.
    """
    value = float(value)
    dpi = QtWidgets.QApplication.primaryScreen().logicalDotsPerInch()
    ratio = dpi / 96.0
    result = value * ratio
    return result


class Signal(object):

    debug = False

    def __init__(self):
        self.funcs = list()
        self.held = False

    def connect(self, func):
        self.funcs.append(func)

    def emit(self, *args, **kwargs):
        if self.held:
            return

        for func in self.funcs:
            # print func, args, kwargs
            if args or kwargs:
                func(*args, **kwargs)
            else:
                func()

    def hold(self, state):
        self.held = bool(state)
