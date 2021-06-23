from maya import cmds, mel
import __init__


@__init__.clock
def new_scene():
    cmds.file(new=True, force=True)


@__init__.clock
def import_maya_file(path):
    print(path)

    try:
        cmds.file(path, i=True)
    except RuntimeError as e:
        print(e)


@__init__.clock
def delete_useless_nodes():
    # Delete unknown nodes
    unknown_nodes = cmds.ls(type='unknown') or list()
    cmds.delete(unknown_nodes)

    # Delete unused nodes
    mel.eval('MLdeleteUnused;')
