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
                targetWeights = cmds.blendShape(bs, q=True, weight=True)
                targetNames = cmds.listAttr('{}.weight'.format(bs), multi=True)

                targetPoints = list()
                groupIndices = cmds.getAttr('{}.inputTarget[0].inputTargetGroup'.format(bs), multiIndices=True)
                for groupIndex in groupIndices:
                    pattern = '{}.inputTarget[0].inputTargetGroup[{}].inputTargetItem[6000].inputPointsTarget'
                    p = cmds.getAttr(pattern.format(bs, groupIndex))
                    targetPoints.append((groupIndex, p))
                targetPoints.append(targetPoints)

                data[bs] = {
                    'targets': zip(targetNames, targetWeights, targetPoints),
                    'geometries': cmds.blendShape(bs, q=True, geometry=True)
                }

        self.dump(data, force=force)
