from . import rigBuilderCore
from maya import cmds




def test():
    world = OneCtrl('world', rigBuilderCore.Component.centerSide, 0)
    world.create()

    leftArm = Arm('arm', rigBuilderCore.Component.leftSide, 0)
    leftArm.create()

    rightArm = leftArm.mirror()
    rightArm.create()
