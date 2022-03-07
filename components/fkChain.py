from .core import Component, GuideArray
from .utils import jointChain, ctrlChain


class FkChain(Component):

    def __init__(self, guides=None, **kwargs):
        super(FkChain, self).__init__(**kwargs)
        self.guides = GuideArray() if guides is None else GuideArray(guides)

    def build(self):
        matrices = [g.matrix.normalized() for g in self.guides]

        skinJoints = jointChain(matrices, namePattern='part{index}_' + str(self) + '_skn')
        ctrls = ctrlChain(
            skinJoints,
            namePattern='fk{index}_' + str(self) + '_ctl',
            color=self.color,
            size=self.size
        )

        self.children.append(skinJoints[0])
        self.children.append(ctrls[0][0])
        self.inputs.append(ctrls[0][0])
        self.outputs.append(ctrls[-1][-1])
        self.influencers += skinJoints
        self.interfaces.append(ctrls[0][1])

        self.buildFolder()
