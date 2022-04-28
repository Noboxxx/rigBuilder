from rigBuilder.components.core import Guide
from rigBuilder.components.limb import Limb
from maya import cmds


class Arm(Limb):
    aName = 'shoulder'
    bName = 'elbow'
    cName = 'wrist'

    abName = 'arm'
    bcName = 'forearm'

    def createGuides(self, name):
        self.aGuide = Guide.create('{}Shoulder'.format(name))
        self.bGuide = Guide.create('{}Elbow'.format(name))
        self.cGuide = Guide.create('{}Wrist'.format(name))
        self.uiGuide = Guide.create('{}Ui'.format(name))

        cmds.parent(self.cGuide, self.bGuide)
        cmds.parent(self.bGuide, self.aGuide)
        cmds.parent(self.uiGuide, self.aGuide)

        cmds.setAttr('{}.tz'.format(self.uiGuide), -10)

        cmds.setAttr('{}.rx'.format(self.aGuide), 90)
        cmds.setAttr('{}.ry'.format(self.aGuide), 5)

        cmds.setAttr('{}.tx'.format(self.bGuide), 10)
        cmds.setAttr('{}.rz'.format(self.bGuide), 10)

        cmds.setAttr('{}.tx'.format(self.cGuide), 10)
        cmds.setAttr('{}.rz'.format(self.cGuide), -5)

        cmds.select(self.aGuide)
