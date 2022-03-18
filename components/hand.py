from maya import cmds
from rigBuilder.components.core import Component, GuideArray, Guide
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.components.utils2 import controller


class Hand(Component):

    def __init__(
            self,
            handGuide='',
            indexGuides=None,
            middleGuides=None,
            ringGuides=None,
            pinkyGuides=None,
            thumbGuides=None,
            **kwargs
    ):
        super(Hand, self).__init__(**kwargs)

        self.handGuide = Guide(handGuide)

        self.indexGuides = GuideArray() if indexGuides is None else GuideArray(indexGuides)
        self.middleGuides = GuideArray() if middleGuides is None else GuideArray(middleGuides)
        self.ringGuides = GuideArray() if ringGuides is None else GuideArray(ringGuides)
        self.pinkyGuides = GuideArray() if pinkyGuides is None else GuideArray(pinkyGuides)
        self.thumbGuides = GuideArray() if thumbGuides is None else GuideArray(thumbGuides)

    def mirror(self):
        super(Hand, self).mirror()

        self.handGuide = self.handGuide.mirrored()

        self.indexGuides = self.indexGuides.mirrored()
        self.middleGuides = self.middleGuides.mirrored()
        self.ringGuides = self.ringGuides.mirrored()
        self.pinkyGuides = self.pinkyGuides.mirrored()
        self.thumbGuides = self.thumbGuides.mirrored()

    def fingerChain(self, fingerName, guideArray, ctrlParent, jointParent):
        latestCtrl = None
        latestJoint = None
        for index, guide in enumerate(guideArray):
            parent = ctrlParent if index == 0 else latestCtrl
            bfr, ctrl = controller('{}{}_{}_ctl'.format(fingerName, index, self), size=self.size * 0.5,
                                   color=self.color, ctrlParent=parent, matrix=guide.matrix)
            joint = cmds.joint(name='{}{}_{}_skn'.format(fingerName, index, self))
            cmds.setAttr('{}.segmentScaleCompensate'.format(joint), False)

            # add to self
            self.influencers.append(joint)
            self.controllers.append(ctrl)

            # parent joint
            parent = jointParent if index == 0 else latestJoint
            cmds.parent(joint, parent)
            latestJoint = joint

            # place and constraint ctrl
            matrixConstraint((ctrl,), joint)

            parent = ctrlParent if index == 0 else latestCtrl
            cmds.parent(bfr, parent)
            latestCtrl = ctrl

    def build(self):
        # main ctrl
        mainBuffer, mainCtrl = controller('main_{}_ctl'.format(self), size=self.size, matrix=self.handGuide.matrix,
                                          color=self.color)
        mainJoint = cmds.joint(name='main_{}_skn'.format(self))

        self.children.append(mainBuffer)
        self.interfaces.append(mainCtrl)

        self.inputs.append(mainBuffer)
        self.outputs.append(mainCtrl)

        # fingers
        guideArrays = (self.indexGuides, self.middleGuides, self.ringGuides, self.pinkyGuides, self.thumbGuides)
        names = ('index', 'middle', 'ring', 'pinky', 'thumb')

        for name, guideArray in zip(names, guideArrays):
            self.fingerChain(name, guideArray, mainCtrl, mainJoint)

        self.buildFolder()

    def createGuides(self, name):
        self.handGuide = Guide.create('{}Hand'.format(name))

        tzValues = (5, 2, 0, -2, -4)
        rxValues = (90, 0, 0, 0, 0)
        txValues = (2, 5, 5, 5, 5)
        finger = ('thumb', 'index', 'middle', 'ring', 'pinky')

        for tx, tz, rx, f in zip(txValues, tzValues, rxValues, finger):
            lastGuide = None
            for n in range(3):
                g = Guide.create('{}{}{}'.format(name, f.title(), n))

                if lastGuide is None:
                    self.__setattr__('{}Guides'.format(f), GuideArray())

                guideArray = self.__getattribute__('{}Guides'.format(f))
                guideArray.append(g)

                if lastGuide is None:
                    cmds.parent(g, self.handGuide)
                    cmds.setAttr('{}.tx'.format(g), tx)
                    cmds.setAttr('{}.tz'.format(g), tz)
                    cmds.setAttr('{}.rx'.format(g), rx)
                else:
                    cmds.parent(g, lastGuide)
                    for attr in ('t', 'r'):
                        for axis in ('x', 'y', 'z'):
                            cmds.setAttr('{}.{}{}'.format(g, attr, axis), 0)
                    cmds.setAttr('{}.tx'.format(g), 3)

                lastGuide = g

        cmds.select(self.handGuide)
