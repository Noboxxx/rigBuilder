from maya import cmds
from rigBuilder.components.core import Component, GuideArray, Guide
from rigBuilder.components.utils import matrixConstraint


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
            # create objects
            bufferGrp = cmds.group(name='{}{}_{}_bfr'.format(fingerName, index, self), empty=True)
            offsetGrp = cmds.group(name='{}{}_{}_off'.format(fingerName, index, self), empty=True)
            joint = cmds.joint(name='{}{}_{}_skn'.format(fingerName, index, self))
            ctrl, = cmds.circle(name='{}{}_{}_ctl'.format(fingerName, index, self), ch=False, radius=self.size * .5, normal=(1, 0, 0))

            # add to self
            self.influencers.append(joint)
            self.controllers.append(ctrl)

            # parent joint
            parent = jointParent if index == 0 else latestJoint
            cmds.parent(joint, parent)
            latestJoint = joint

            # place and constraint ctrl
            cmds.parent(offsetGrp, bufferGrp)
            cmds.parent(ctrl, offsetGrp)

            cmds.xform(bufferGrp, matrix=list(guide.matrix.normalized()))
            matrixConstraint((ctrl,), joint)

            # parent ctrls
            parent = ctrlParent if index == 0 else latestCtrl
            cmds.parent(bufferGrp, parent)
            latestCtrl = ctrl

    def build(self):
        # main ctrl
        mainBufferGrp = cmds.group(name='main_{}_bfr'.format(self), empty=True)
        mainCtrl, = cmds.circle(name='main_{}_ctl'.format(self), ch=False, radius=self.size, normal=(1, 0, 0))
        mainJoint = cmds.joint(name='main_{}_skn'.format(self))

        cmds.parent(mainCtrl, mainBufferGrp)

        cmds.xform(mainBufferGrp, matrix=list(self.handGuide.matrix))

        self.children.append(mainBufferGrp)
        self.interfaces.append(mainCtrl)

        self.inputs.append(mainBufferGrp)
        self.outputs.append(mainCtrl)

        # fingers
        guideArrays = (self.indexGuides, self.middleGuides, self.ringGuides, self.pinkyGuides, self.thumbGuides)
        names = ('index', 'middle', 'ring', 'pinky', 'thumb')

        for name, guideArray in zip(names, guideArrays):
            self.fingerChain(name, guideArray, mainCtrl, mainJoint)

        self.buildFolder()