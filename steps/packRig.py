from maya import cmds
from rigBuilder.components.baseLegacy import BaseLegacy
from rigBuilder.components.utils import matrixConstraint
from rigBuilder.steps.importSkinLayers import Node
from rigBuilder.steps.core import Step
from rigBuilder.types import UnsignedFloat


class Nodes(list):

    def __init__(self, seq=None):
        super(Nodes, self).__init__(list() if seq is None else [Node(i) for i in seq])


class PackRig(Step):

    def __init__(self, children=None, rigChildren=None, geometryChildren=None, size=1.0, cleanScene=False):
        super(PackRig, self).__init__()
        self.children = Nodes(('geometry',)) if children is None else Nodes(children)
        self.rigChildren = Nodes(('setup',)) if rigChildren is None else Nodes(rigChildren)
        self.geometryChildren = Nodes() if geometryChildren is None else Nodes(geometryChildren)
        self.cleanScene = bool(cleanScene)
        self.size = UnsignedFloat(size)

    def build(self):
        assetGroup = cmds.group(empty=True, name='rig_group')
        rigGroup = cmds.group(empty=True, name='rig')
        geometryGroup = cmds.group(empty=True, name='geometry')

        if self.children:
            cmds.parent(self.children, assetGroup)
        if self.rigChildren:
            cmds.parent(self.rigChildren, rigGroup)
        if self.geometryChildren:
            cmds.parent(self.geometryChildren, geometryGroup)

        cmds.parent(geometryGroup, rigGroup, assetGroup)

        # Create base component
        base = BaseLegacy(name='base', size=self.size)
        base.build()

        cmds.parent(str(base), rigGroup)

        if cmds.objExists('ControlSet'):
            base.buildControlSet()

        # matrixConstraint / connect vis on rigChildren
        for child in self.rigChildren:
            matrixConstraint((base.outputs[0],), child)
            cmds.connectAttr('{}.ctrl1'.format(base.interfaces[0]), '{}.v'.format(child))

        # connect mesh vis
        cmds.connectAttr('{}.Mesh'.format(base.interfaces[0]), '{}.v'.format(geometryGroup))
        for mesh in cmds.listRelatives(geometryGroup, allDescendents=True, type='mesh') or list():
            cmds.connectAttr('{}.smooth'.format(base.interfaces[0]), '{}.smoothLevel'.format(mesh))

        # clean scene
        if self.cleanScene:
            rootDags = cmds.ls(assemblies=True)
            for d in rootDags:
                if d == assetGroup:
                    continue
                try:
                    cmds.delete(d)
                except:
                    pass
