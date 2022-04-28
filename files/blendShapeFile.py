from maya import OpenMayaAnim, OpenMaya
from maya import cmds
from rigBuilder.files.core import JsonFile


class BlendShapeFile(JsonFile):

    def getSelectedMeshes(self):
        meshes = cmds.listRelatives(cmds.ls(sl=True, type='transform'), type='mesh', allDescendents=True) or list()
        return [m for m in meshes if not cmds.getAttr('{}.intermediateObject'.format(m))]

    def export(self, meshes=None, force=False):
        data = dict()

        meshes = meshes if meshes is not None else self.getSelectedMeshes()

        for mesh in meshes:
            for bs in cmds.ls(cmds.listHistory(mesh) or list(), type='blendShape'):
                geometries = cmds.blendShape(bs, q=True, geometry=True)

                if not geometries:
                    continue

                targetWeights = cmds.blendShape(bs, q=True, weight=True)
                targetNames = cmds.listAttr('{}.weight'.format(bs), multi=True)

                targetPoints = list()
                targetComponents = list()
                groupIndices = cmds.getAttr('{}.inputTarget[0].inputTargetGroup'.format(bs), multiIndices=True)
                for groupIndex in groupIndices:
                    pointsPattern = '{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[6000].inputPointsTarget'
                    p = cmds.getAttr(pointsPattern.format(bs, groupIndex))
                    targetPoints.append(p)

                    componentsPattern = '{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[6000].inputComponentsTarget'
                    c = cmds.getAttr(componentsPattern.format(bs, groupIndex))
                    targetComponents.append(c)

                targets = {n: {'points': p, 'weight': w, 'components': c} for n, p, w, c in zip(
                    targetNames, targetPoints, targetWeights, targetComponents)}

                data[bs] = {
                    'targets': targets,
                    'geometry': geometries[0]
                }

        self.dump(data, force=force)

    def import_(self):
        data = self.load()

        for blendShape, bsInfo in data.items():
            geometry = bsInfo['geometry']

            if geometry:
                bs, = cmds.blendShape(geometry, name=blendShape, automatic=True)
            else:
                bs = cmds.createNode('blendShape')

            for index, (targetName, targetInfo) in enumerate(bsInfo['targets'].items()):
                target, = cmds.duplicate(geometry, name=targetName)
                cmds.blendShape(
                    bs,
                    e=True,
                    tc=True,
                    t=(geometry, index, target, 1),
                    w=(index, targetInfo['weight'])
                )
                cmds.delete(target)

                componentsPattern = '{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[6000].inputComponentsTarget'
                cmds.setAttr(
                    componentsPattern.format(bs, index),
                    len(targetInfo['components']),
                    *targetInfo['components'],
                    type='componentList'
                )

                pointsPattern = '{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[6000].inputPointsTarget'
                cmds.setAttr(
                    pointsPattern.format(bs, index),
                    len(targetInfo['points']),
                    *targetInfo['points'],
                    type='pointArray'
                )
