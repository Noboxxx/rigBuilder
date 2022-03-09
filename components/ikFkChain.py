from rigBuilder.components.core import Component
from rigBuilder.components.core import GuideArray
from rigBuilder.components.utils2 import controller


class IkFkChain(Component):

    def __init__(self, guides=None, **kwargs):
        super(IkFkChain, self).__init__(**kwargs)
        self.guides = GuideArray() if guides is None else GuideArray(guides)

    def mirror(self):
        super(IkFkChain, self).mirror()
        self.guides = self.guides.mirrored()

    def build(self):
        rootBfr, rootCtrl = controller('root_{}_ctl'.format(self), size=self.size, color=self.color,
                                       matrix=self.guides[0].matrix, shape='cube')
        self.controllers.append(rootCtrl)
        self.inputs.append(rootBfr)
        self.interfaces.append(rootBfr)

        endBfr, endCtrl = controller('end_{}_ctl'.format(self), size=self.size, color=self.color,
                                     matrix=self.guides[-1].matrix, shape='cube')
        self.controllers.append(endCtrl)

        for index, guide in enumerate(self.guides[1:-1]):
            fkBfr, fkCtrl = controller('fk{}_{}_ctl'.format(index, self), size=self.size, color=self.color,
                                       matrix=guide.matrix)
            self.controllers.append(fkCtrl)

        self.buildFolder()
