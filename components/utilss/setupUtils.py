from __future__ import division
from maya import cmds
from maya.api import OpenMaya
from rigBuilder.components.utilss.mathUtils import blendMatrices


def jointChain(matrixA, matrixB, sections=4, name='joint#'):
    cmds.select(clear=True)

    joints = list()
    for i in range(sections):
        m = blendMatrices(matrixA, matrixB, blender=i / (sections - 1))
        j = cmds.joint(name=name)
        joints.append(j)
        cmds.xform(j, matrix=list(m), worldSpace=True)

    return joints


def ribbon(matrixA, matrixB, sections=4, width=1.0):
    points = list()
    for z in (width / 2 * -1, width / 2):
        for i in range(sections + 1):
            m = blendMatrices(matrixA, matrixB, i / sections)
            o = OpenMaya.MMatrix(
                (
                    1, 0, 0, 0,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    0, 0, z, 1,
                )
            )
            points.append(list(o * m)[12:15])

    kv = range(sections - 1)
    kv = [0, 0] + kv + [kv[-1], kv[-1]]
    srf = cmds.surface(
        du=1,
        dv=3,
        ku=(0, 1),
        kv=kv,
        p=points
    )

    pointInfoAttrs = (
        (0, 'normalizedTangentV'),
        (1, 'normalizedNormal'),
        (3, 'position'),
    )
    axes = ('X', 'Y', 'Z')
    trsAttrs = (
        'translate',
        'rotate',
        'scale',
        'shear',
    )

    for i in range(sections + 1):
        pointInfo = cmds.createNode('pointOnSurfaceInfo')
        cmds.connectAttr('{}.local'.format(srf), '{}.inputSurface'.format(pointInfo))
        cmds.setAttr('{}.turnOnPercentage'.format(pointInfo), True)
        cmds.setAttr('{}.parameterU'.format(pointInfo), .5)
        cmds.setAttr('{}.parameterV'.format(pointInfo), i / sections)

        sideVector = cmds.createNode('vectorProduct')
        cmds.setAttr('{}.operation'.format(sideVector), 2)
        cmds.connectAttr('{}.normalizedTangentV'.format(pointInfo), '{}.input1'.format(sideVector))
        cmds.connectAttr('{}.normalizedNormal'.format(pointInfo), '{}.input2'.format(sideVector))

        fourByFour = cmds.createNode('fourByFourMatrix')
        for x, attr in pointInfoAttrs:
            for y, axis in enumerate(axes):
                srcPlug = '{}.{}{}'.format(pointInfo, attr, axis)
                destPlug = '{}.in{}{}'.format(fourByFour, x, y)
                cmds.connectAttr(srcPlug, destPlug)

        for x, axis in enumerate(axes):
            srcPlug = '{}.output{}'.format(sideVector, axis)
            destPlug = '{}.in2{}'.format(fourByFour, x)
            cmds.connectAttr(srcPlug, destPlug)

        lct, = cmds.spaceLocator()
        cmds.xform(lct, matrix=cmds.getAttr('{}.output'.format(fourByFour)))

        decomposeMatrix = cmds.createNode('decomposeMatrix')
        cmds.connectAttr('{}.output'.format(fourByFour), '{}.inputMatrix'.format(decomposeMatrix))
        for attr in trsAttrs:
            cmds.connectAttr('{}.output{}'.format(decomposeMatrix, attr.title()), '{}.{}'.format(lct, attr))
