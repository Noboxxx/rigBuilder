from rigBuilder.steps.core import Step
from maya import cmds, mel


class FinalizeRig(Step):

    def __init__(self, removeUnusedSkinInfluences=True, deleteUnusedNodes=True, hideJoints=True, deleteNgSkinToolsNodes=True, deleteUnknownNodes=True):
        super(FinalizeRig, self).__init__()

        self.removeUnusedSkinInfluences = bool(removeUnusedSkinInfluences)
        self.deleteUnusedNodes = bool(deleteUnusedNodes)
        self.hideJoints = bool(hideJoints)
        self.deleteNgSkinToolsNodes = bool(deleteNgSkinToolsNodes)
        self.deleteUnknownNodes = bool(deleteUnknownNodes)

    @staticmethod
    def removeUnusedInfluences(skinCls):
        allInfluences = cmds.skinCluster(skinCls, q=True, inf=True)
        weightedInfluences = cmds.skinCluster(skinCls, q=True, wi=True)
        unusedInfluences = [inf for inf in allInfluences if inf not in weightedInfluences]
        cmds.skinCluster(skinCls, e=True, removeInfluence=unusedInfluences)

    def build(self, workspace=''):
        # optimize skinClusters
        if self.removeUnusedSkinInfluences:
            for skinCluster in cmds.ls(type='skinCluster'):
                self.removeUnusedInfluences(skinCluster)

        # delete unused nodes
        if self.deleteUnusedNodes:
            mel.eval("MLdeleteUnused()")

        # hide joints
        if self.hideJoints:
            for joint in cmds.ls(type='joint'):
                cmds.setAttr('{}.drawStyle'.format(joint), 2)

        # delete ngSkin nodes

        # delete unknown nodes
        if self.deleteUnknownNodes:
            nodes = cmds.ls(type='unknown')
            if nodes:
                cmds.delete(nodes)
