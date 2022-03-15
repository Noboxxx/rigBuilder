from rigBuilder.components.core import Component, GuideArray
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
        rootBfr, rootCtrl = controller('rootIk_{}_ctl'.format(self), size=self.size, color=self.color,
                                       matrix=self.guides[0].matrix, shape='cube')
        self.controllers.append(rootCtrl)
        self.inputs.append(rootBfr)
        self.interfaces.append(rootBfr)
        self.children.append(rootBfr)

        # fk ctrls
        lastCtrl = None
        for index, guide in enumerate(self.guides[1:-1]):
            fkBfr, fkCtrl = controller('fk{}_{}_ctl'.format(index, self), size=self.size, color=self.color,
                                       matrix=guide.matrix)
            if lastCtrl:
                cmds.parent(fkBfr, lastCtrl)
            else:
                cmds.parent(fkBfr, rootCtrl)

            lastCtrl = fkCtrl
            self.controllers.append(fkCtrl)

        # end ctrl
        endBfr, endCtrl = controller('endIk_{}_ctl'.format(self), size=self.size, color=self.color,
                                     matrix=self.guides[-1].matrix, shape='cube')
        cmds.parent(endBfr, lastCtrl)
        self.controllers.append(endCtrl)

        # curve
        points = [g.matrix[12:15] for g in self.guides]
        for p in points:
            lct, = cmds.spaceLocator()
            cmds.xform(lct, translation=p)

        curve = cmds.curve(d=3, editPoint=points, name='{}_crv'.format(self))
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

        # ik
        cmds.select(joints[0], joints[-1], curve)
        ikHandle, _ = cmds.ikHandle(solver='ikSplineSolver', ccv=False, roc=False, pcv=False)
        self.children.append(ikHandle)

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


            print position

            cmds.skinPercent(
                skinCluster,
                '{}.cv[{}]'.format(curve, index),
                transformValue=[
                    (rootJoint, 1 - percent),
                    (endJoint, percent),
                ],
            )

        self.buildFolder()
