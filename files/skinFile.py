import math

from maya import cmds
from rigBuilder.files.core import JsonFile


class SkinFile(JsonFile):

    def export(self, meshes=None, force=False):

        meshes = meshes if meshes is not None else cmds.listRelatives(
            cmds.ls(sl=True, type='transform'), type='mesh', allDescendents=True
        )

        data = dict()
        for mesh in meshes:
            for skinCluster in cmds.listHistory(mesh):
                if not cmds.objectType(skinCluster, isAType='skinCluster') or skinCluster in data:
                    continue

                targets = cmds.skinCluster(skinCluster, q=True, geometry=True)

                weights = list()
                for vertexIndex in cmds.getAttr('{}.weightList'.format(skinCluster), multiIndices=True):
                    infIndices = cmds.getAttr('{}.weightList[{}].weights'.format(skinCluster, vertexIndex), multiIndices=True)
                    infWeights = cmds.getAttr('{}.weightList[{}].weights'.format(skinCluster, vertexIndex))[0]
                    weights.append(zip(infIndices, infWeights))

                influences = list()
                for influence in cmds.skinCluster(skinCluster, q=True, influence=True):
                    influences.append((influence, cmds.xform(influence, q=True, translation=True, worldSpace=True)))

                data[skinCluster] = {
                    'influences': influences,
                    'weights': weights,
                    'targets': targets,

                    'skinningMethod': cmds.getAttr('{}.skinningMethod'.format(skinCluster)),
                    'useComponents': cmds.getAttr('{}.useComponents'.format(skinCluster)),
                    'envelope': cmds.getAttr('{}.envelope'.format(skinCluster)),
                    'deformUserNormals': cmds.getAttr('{}.deformUserNormals'.format(skinCluster)),
                    'dqsSupportNonRigid': cmds.getAttr('{}.dqsSupportNonRigid'.format(skinCluster)),
                    'dqsScaleX': cmds.getAttr('{}.dqsScaleX'.format(skinCluster)),
                    'dqsScaleY': cmds.getAttr('{}.dqsScaleY'.format(skinCluster)),
                    'dqsScaleZ': cmds.getAttr('{}.dqsScaleZ'.format(skinCluster)),
                    'maintainMaxInfluences': cmds.getAttr('{}.maintainMaxInfluences'.format(skinCluster)),
                    'maxInfluences': cmds.getAttr('{}.maxInfluences'.format(skinCluster)),
                    'weightDistribution': cmds.getAttr('{}.weightDistribution'.format(skinCluster)),
                    'normalizeWeights': cmds.getAttr('{}.normalizeWeights'.format(skinCluster)),
                }

        self.dump(data, force=force)

    @staticmethod
    def distance(pointA, pointB):
        result = 0
        for r in [(b - a) ** 2 for a, b in zip(pointA, pointB)]:
            result += r
        return abs(math.sqrt(result))

    @staticmethod
    def getClosestJoint(position):
        distance = -1
        joint = None
        for j in cmds.ls(type='joint'):
            p = cmds.xform(j, q=True, translation=True, worldSpace=True)
            d = SkinFile.distance(position, p)
            if distance == -1 or d < distance:
                distance = d
                joint = j

        return joint

    def import_(self):

        data = self.load()
        for skinClusterName, info in data.items():

            influences = list()
            for influenceName, position in info.pop('influences'):
                if cmds.objExists(influenceName):
                    influences.append(influenceName)
                else:
                    closestJoint = self.getClosestJoint(position)
                    influences.append(closestJoint)

            targets = info.pop('targets')
            skinCluster, = cmds.skinCluster(
                influences + targets,
                name=skinClusterName,
            )

            for vertexIndex, weights in enumerate(info.pop('weights')):
                cmds.skinPercent(
                    skinCluster,
                    '{}.vtx[{}]'.format(targets[0], vertexIndex),
                    transformValue=[(influences[i], w) for i, w in weights],
                )

            for k, v in info.items():
                cmds.setAttr('{}.{}'.format(skinCluster, k, v))
