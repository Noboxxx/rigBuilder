from maya import cmds
from .core import Component, GuideArray
from .utils import matrixConstraint
from .utils2 import controller


class FkChain(Component):

    def __init__(self, guides=None, **kwargs):
        super(FkChain, self).__init__(**kwargs)
        self.guides = GuideArray() if guides is None else GuideArray(guides)

    def build(self):
        latestJoint = None
        latestCtrl = None
        for index, guide in enumerate(self.guides):
            bfr, ctrl = controller(
                'part{}_{}_ctl'.format(index, self), color=self.color, size=self.size, matrix=guide.matrix,
                ctrlParent=latestCtrl)
            joint = cmds.joint(name='part{}_{}_skn'.format(index, self))
            cmds.setAttr('{}.segmentScaleCompensate'.format(joint), False)

            matrixConstraint((ctrl, ), joint)

            if index == 0:
                self.inputs.append(bfr)
                self.children.append(bfr)
                self.children.append(joint)
                self.interfaces.append(ctrl)
            else:
                cmds.parent(joint, latestJoint)
                cmds.parent(bfr, latestCtrl)

            latestCtrl = ctrl
            latestJoint = joint

            self.controllers.append(ctrl)
            self.influencers.append(joint)
            self.outputs.insert(0, ctrl)

        self.buildFolder()

    def mirror(self):
        super(FkChain, self).mirror()
        self.guides = self.guides.mirrored()
