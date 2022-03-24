from __future__ import division
from rigBuilder.components.core import Component, GuideArray, Guide
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.components.utils2 import controller, distance
from maya import cmds


class IkFkChain(Component):

    def __init__(self, guides=None, **kwargs):
        super(IkFkChain, self).__init__(**kwargs)
        self.guides = GuideArray() if guides is None else GuideArray(guides)

    def mirror(self):
        super(IkFkChain, self).mirror()
        self.guides = self.guides.mirrored()

    def build(self):
        # root ctrl
        rootBfr, rootCtrl = controller('rootIk_{}_ctl'.format(self), size=self.guides[0].size, color=self.color - 100,
                                       matrix=self.guides[0].matrix, shape='square')
        self.controllers.append(rootCtrl)
        self.inputs.append(rootBfr)
        self.interfaces.append(rootBfr)
        self.children.append(rootBfr)

        # fk ctrls
        lastCtrl = None
        for index, guide in enumerate(self.guides[1:-1]):
            fkBfr, fkCtrl = controller('fk{}_{}_ctl'.format(index, self), size=guide.size, color=self.color,
                                       matrix=guide.matrix)
            if lastCtrl:
                cmds.parent(fkBfr, lastCtrl)
            else:
                cmds.parent(fkBfr, rootCtrl)

            lastCtrl = fkCtrl
            self.controllers.append(fkCtrl)

        # end ctrl
        endBfr, endCtrl = controller('endIk_{}_ctl'.format(self), size=self.guides[-1].size, color=self.color - 100,
                                     matrix=self.guides[-1].matrix, shape='square')
        cmds.parent(endBfr, lastCtrl)
        self.controllers.append(endCtrl)

        # curve
        points = [g.matrix[12:15] for g in self.guides]
        curve = cmds.curve(d=3, editPoint=points, name='{}_crv'.format(self))
        cmds.setAttr('{}.inheritsTransform'.format(curve), False)
        self.children.append(curve)

        # joints
        joints = list()
        for index, guide in enumerate(self.guides):
            if joints:
                cmds.select(joints[-1])
            joint = cmds.joint(name='part{}_{}_skn'.format(index, self))
            if index == 0:
                self.children.append(joint)
            cmds.xform(joint, matrix=guide.matrix, worldSpace=True)
            joints.append(joint)
            self.influencers.append(joint)
            self.outputs.insert(0, joint)

        cmds.makeIdentity(joints[0], apply=True, rotate=True)
        for joint in joints:
            cmds.setAttr('{}.segmentScaleCompensate'.format(joint), False)

        # plop
        matrixConstraint((rootCtrl,), joints[0])

        # ik
        cmds.select(joints[0], joints[-1], curve)
        ikHandle, _ = cmds.ikHandle(solver='ikSplineSolver', ccv=False, roc=False, pcv=False)
        self.children.append(ikHandle)

        cmds.setAttr('{}.dTwistControlEnable'.format(ikHandle), True)
        cmds.setAttr('{}.dWorldUpType'.format(ikHandle), 4)
        cmds.connectAttr('{}.worldMatrix[0]'.format(rootCtrl), '{}.dWorldUpMatrix'.format(ikHandle))
        cmds.connectAttr('{}.worldMatrix[0]'.format(endCtrl), '{}.dWorldUpMatrixEnd'.format(ikHandle))

        # curve joints
        cmds.select(clear=True)
        rootJoint = cmds.joint(name='rootIk_{}_jnt'.format(self))
        matrixConstraint((rootCtrl,), rootJoint)
        self.children.append(rootJoint)

        endJoint = cmds.joint(name='endIk_{}_jnt'.format(self))
        matrixConstraint((endCtrl,), endJoint)
        self.children.append(endJoint)

        # skin curve
        skinCluster, = cmds.skinCluster(curve, rootJoint, endJoint)
        cvCount = len(self.guides) + 2
        rootPos = self.guides[0].matrix[12:15]
        endPos = self.guides[-1].matrix[12:15]

        for index in range(cvCount):
            cvPlug = '{}.cv[{}]'.format(curve, index)
            cvPos = cmds.xform(cvPlug, q=True, translation=True)

            distanceRoot = distance(cvPos, rootPos)
            distanceEnd = distance(cvPos, endPos)
            totalLength = distanceRoot + distanceEnd

            ratio = distanceRoot / totalLength

            cmds.skinPercent(
                skinCluster,
                '{}.cv[{}]'.format(curve, index),
                transformValue=[
                    (rootJoint, 1 - ratio),
                    (endJoint, ratio),
                ],
            )

        self.buildFolder()

    def createGuides(self, name='untitled', number=3):
        self.guides = GuideArray()
        for index in range(number):
            guide = Guide.create('{}{}'.format(name, index))
            cmds.xform(guide, translation=(index * 10, 0, 0))
            if self.guides:
                cmds.parent(guide, self.guides[-1])
            self.guides.append(guide)

        cmds.select(self.guides[0])