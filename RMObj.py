from .RObj import *
from maya import cmds


def createTransform(name):
    return cmds.group(empty=True, name=name)


def parentTransform(children, parent):
    cmds.parent(children, parent)


def createController(name, normal, radius):
    ctrl, = cmds.circle(name=name, constructionHistory=False, radius=radius, normal=normal)
    return ctrl


Transform.createFunc = createTransform
Transform.parentFunc = parentTransform
Controller.createFunc = createController
