from maya import cmds, mel
import __init__


@__init__.log
def new_scene():
    cmds.file(new=True, force=True)


@__init__.log
def import_maya_file(path):
    try:
        cmds.file(path, i=True)
    except RuntimeError as e:
        print(e)


@__init__.log
def delete_useless_nodes():
    # Delete unknown nodes
    unknown_nodes = cmds.ls(type='unknown') or list()
    cmds.delete(unknown_nodes)

    # Delete unused nodes
    mel.eval('MLdeleteUnused;')


@__init__.log
def transfer_skin(source, targets):
    def get_skinned_joints(mesh):
        joints_ = list()
        skin_clusters = [n for n in cmds.listHistory(mesh) or list() if cmds.objectType(n, isAType='skinCluster')]
        for skin_cluster in skin_clusters:
            joints_ += cmds.skinCluster(skin_cluster, query=True, inf=True) or list()
        joints_ = list(set(joints_))
        joints_.sort()
        return joints_

    def get_skin_cluster(mesh):
        for node_ in cmds.listHistory(mesh) or list():
            if cmds.objectType(node_, isAType='skinCluster'):
                return node_
        return None

    attributes = (
        'skinningMethod', 'useComponents', 'deformUserNormals', 'dqsSupportNonRigid',
        'dqsScaleX', 'dqsScaleY', 'dqsScaleZ', 'normalizeWeights', 'weightDistribution',
        'maintainMaxInfluences', 'maxInfluences', 'envelope'
    )

    parent_skin_cluster = get_skin_cluster(source)

    data = list()
    for attr in attributes:
        data.append((attr, cmds.getAttr('{0}.{1}'.format(parent_skin_cluster, attr))))

    joints = get_skinned_joints(source)
    for target in targets:
        # Wipe out any previous skinCluster on dest mesh
        if True in [cmds.objectType(node, isAType='skinCluster') for node in cmds.listHistory(target) or list()]:
            cmds.skinCluster(target, e=True, unbind=True)

        # Skin dest mesh with joints' meshes
        new_skin_cluster, = cmds.skinCluster(target, joints)

        for attr, value in data:
            cmds.setAttr('{0}.{1}'.format(new_skin_cluster, attr), value)

        # Transfer the skin
        cmds.copySkinWeights(source, target, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation=('name', 'closestJoint'))