from rigBuilder.components.baseLegacy import Nodes
from rigBuilder.steps.core import Step
from rigBuilder.types import Node
from maya import cmds


class TransferSkin(Step):

    attributes = (
        'skinningMethod',
        'useComponents',
        'envelope',
        'deformUserNormals',
        'dqsSupportNonRigid',
        'dqsScaleX',
        'dqsScaleY',
        'dqsScaleZ',
        'maintainMaxInfluences',
        'maxInfluences',
        'weightDistribution',
        'normalizeWeights',
    )

    def __init__(self, sourceMesh='', destinationMeshes=None, hideSource=False, **kwargs):
        super(TransferSkin, self).__init__(**kwargs)
        self.sourceMesh = Node(sourceMesh)
        self.destinationMeshes = Nodes(destinationMeshes)
        self.hideSource = bool(hideSource)

    def build(self, workspace=''):
        joints = cmds.skinCluster(self.sourceMesh, q=True, influence=True)
        sourceSkinCluster = cmds.ls(cmds.listHistory(self.sourceMesh), type='skinCluster')[0]

        settings = {attr: cmds.getAttr('{}.{}'.format(sourceSkinCluster, attr)) for attr in self.attributes}

        for mesh in cmds.listRelatives(self.destinationMeshes, allDescendents=True, type='mesh'):
            if cmds.getAttr('{}.intermediateObject'.format(mesh)):
                continue
            skinCluster, = cmds.skinCluster(mesh, joints)
            cmds.select(self.sourceMesh, mesh)
            cmds.copySkinWeights(
                noMirror=True,
                surfaceAssociation='closestPoint',
                influenceAssociation=('name', 'closestJoint')
            )

            for attr, value in settings.items():
                cmds.setAttr('{}.{}'.format(skinCluster, attr), value)

        if self.hideSource:
            cmds.setAttr('{}.v'.format(self.sourceMesh), False)
