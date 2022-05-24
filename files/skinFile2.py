import math
import os
import xml
from xml.etree.ElementTree import Element

from maya import cmds
from rigBuilder.types import File
from xml.etree import ElementTree


class SkinFile2(File):
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

    @staticmethod
    def getSkinCluster(mesh):
        skinClusters = cmds.ls(cmds.listHistory(mesh), type='skinCluster')

        if skinClusters:
            return skinClusters[0]

        return None

    @staticmethod
    def meshesFromSelection(selection=None, skipIntermediate=True, descendants=True):
        meshes = cmds.ls(selection, type='mesh')

        if descendants:
            objects = cmds.ls(sl=True, type='transform') if selection is None else selection
            meshes += cmds.listRelatives(objects, type='mesh', allDescendents=True)

        if skipIntermediate:
            meshes = [m for m in meshes if not cmds.getAttr('{}.intermediateObject'.format(m))]

        return meshes

    @staticmethod
    def distance(pointA, pointB):
        result = 0
        for r in [(b - a) ** 2 for a, b in zip(pointA, pointB)]:
            result += r
        return abs(math.sqrt(result))

    @classmethod
    def getClosestJoint(cls, position):
        distance = -1
        joint = None
        for j in cmds.ls(type='joint'):
            p = cmds.xform(j, q=True, translation=True, worldSpace=True)
            d = cls.distance(position, p)
            if distance == -1 or d < distance:
                distance = d
                joint = j

        return joint

    def export(self, mesh=None):
        mesh = cmds.ls(sl=True)[0] if mesh is None else mesh
        deformer = self.getSkinCluster(mesh)
        cmds.deformerWeights(
            os.path.basename(self),
            path=os.path.dirname(self),
            ex=True,
            deformer=deformer,
            attribute=self.attributes,
        )
        tree = ElementTree.parse(self)
        # root = tree.getroot()

        for w in tree.findall('weights'):
            joint = w.get('source')
            if not cmds.objectType(joint or ''):
                continue
            tx, ty, tz = cmds.xform(joint, q=True, translation=True, worldSpace=True)
            w.set('tx', str(tx))
            w.set('ty', str(ty))
            w.set('tz', str(tz))

        # # blendWeights
        # bw = Element('blendWeights')
        # bw.set('deformer', deformer)
        # root.append(bw)
        #
        # blendWeights = cmds.getAttr('{}.blendWeights'.format(deformer))
        # for i, v in enumerate(blendWeights[0]):
        #     w = Element('weight')
        #     w.set('index', str(i))
        #     w.set('value', str(v))
        #     bw.append(w)

        tree.write(str(self))

    def import_(self, mesh=None, method='index'):
        mesh = cmds.ls(sl=True)[0] if mesh is None else mesh
        tree = ElementTree.parse(self)

        joints = list()
        for w in tree.findall('weights'):
            joint = w.get('source')
            if cmds.objExists(joint):
                joints.append(joint)
                continue

            tx = w.get('tx')
            ty = w.get('ty')
            tz = w.get('tz')
            if tx and ty and tz:
                joint = self.getClosestJoint((float(tx), float(ty), float(tz)))
                if joint is None:
                    raise RuntimeError('No closest joint found for {}.'.format(repr(joint)))
                joints.append(joint)
                continue

            raise RuntimeError('The joint {} is nowhere to be found.'.format(repr(joint)))

        skinCluster = self.getSkinCluster(mesh)
        if skinCluster:
            cmds.delete(skinCluster)

        skinCluster, = cmds.skinCluster(joints + [mesh])

        cmds.deformerWeights(
            os.path.basename(self),
            path=os.path.dirname(self),
            im=True,
            method=method,
            deformer=skinCluster,
            ignoreName=True,
            attribute=self.attributes,
        )

        for d in tree.findall('deformer'):
            for a in d.findall('attribute'):
                name = a.get('name')
                value = a.get('value')
                cmds.setAttr('{}.{}'.format(skinCluster, name), eval(value))
