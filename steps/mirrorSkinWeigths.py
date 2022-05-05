from maya import cmds
from rigBuilder.steps.core import Step
from rigBuilder.types import Node, Choice


class Plan2D(Choice):
    choices = (
        'XY',
        'YZ',
        'XZ',
    )


class SurfaceAssociation(Choice):
    choices = (
        'closestPoint',
        'rayCast',
        'closestComponent',
    )


class InfluenceAssociation(Choice):
    choices = (
        'closestJoint',
        'oneToOne',
        'label',
    )


class InfluenceAssociations(list):

    def __init__(self, seq=tuple()):
        super(InfluenceAssociations, self).__init__([InfluenceAssociation(i) for i in seq])


class MirrorSkinWeights(Step):

    @staticmethod
    def getSkinCluster(obj):
        skinClusters = cmds.ls(cmds.listHistory(obj), type='skinCluster')

        if skinClusters:
            return skinClusters[0]

        return None

    def __init__(
            self,
            source='',
            destination='',
            mirrorAcross=Plan2D.default(),
            positiveToNegative=True,
            surfaceAssociation=SurfaceAssociation.default(),
            influenceAssociations=None,
            normalize=True,
    ):
        super(MirrorSkinWeights, self).__init__()

        self.source = Node(source)
        self.destination = Node(destination)

        self.mirrorAcross = Plan2D(mirrorAcross)
        self.positiveToNegative = bool(positiveToNegative)
        self.surfaceAssociation = SurfaceAssociation(surfaceAssociation)
        self.influenceAssociations = InfluenceAssociations() if influenceAssociations is None else InfluenceAssociations(influenceAssociations)
        self.normalize = bool(normalize)

    def build(self, workspace=''):
        if not cmds.objExists(self.source):
            raise RuntimeError('The source object {} is nowhere to be found.'.format(self.source))

        if not cmds.objExists(self.destination):
            raise RuntimeError('The destination object {} is nowhere to be found.'.format(self.destination))

        sourceDeformer = self.getSkinCluster(self.source)
        destinationDeformer = self.getSkinCluster(self.destination)

        if not sourceDeformer and not destinationDeformer:
            raise RuntimeError('The source object {} and the destination object {} should be skinned.'.format(self.source, self.destination))

        cmds.copySkinWeights(
            sourceDeformer=sourceDeformer,
            destinationDeformer=destinationDeformer,
            mirrorMode=self.mirrorAcross,
            surfaceAssociation=self.surfaceAssociation,
            influenceAssociation=self.influenceAssociations,
            normalize=self.normalize,
        )

