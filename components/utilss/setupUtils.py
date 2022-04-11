from __future__ import division
from maya import cmds
from maya.api import OpenMaya
from rigBuilder.components.utilss.mathUtils import blendMatrices


def jointChain(matrixA, matrixB, nJoints=4, name='joint<i>', freezeRotate=True):
    cmds.select(clear=True)

    joints = list()
    for i in range(nJoints):
        m = blendMatrices(matrixA, matrixB, blender=i / (nJoints - 1))
        j = cmds.joint(name=name.replace('<i>', str(i)))
        joints.append(j)
        cmds.xform(j, matrix=list(m), worldSpace=True)

    if freezeRotate:
        cmds.makeIdentity(joints[0], rotate=True, apply=True)

    return joints


def ribbon(matrixA, matrixB, nEdges=5, nOutputs=5, width=1.0):
    # matrices
    curvePoints = list()
    for z in (width / 2 * -1, width / 2):
        points = list()
        for i in range(nEdges):
            m = blendMatrices(matrixA, matrixB, i / (nEdges - 1))
            o = OpenMaya.MMatrix((1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, z, 1))
            points.append(list(o * m)[12:15])
        curvePoints.append(points)

    # surface
    curves = [cmds.curve(ep=cp) for cp in curvePoints]
    srf, = cmds.loft(*curves, ch=False, name='ribbon#')
    cmds.delete(curves)

    # outputs generation
    outputMatrixPlugs = list()
    for i in range(nOutputs):
        pointInfo = cmds.createNode('pointOnSurfaceInfo')
        cmds.connectAttr('{}.local'.format(srf), '{}.inputSurface'.format(pointInfo))
        cmds.setAttr('{}.turnOnPercentage'.format(pointInfo), True)
        cmds.setAttr('{}.parameterU'.format(pointInfo), .5)
        cmds.setAttr('{}.parameterV'.format(pointInfo), i / (nOutputs - 1))

        sideVector = cmds.createNode('vectorProduct')
        cmds.setAttr('{}.operation'.format(sideVector), 2)
        cmds.connectAttr('{}.normalizedTangentV'.format(pointInfo), '{}.input1'.format(sideVector))
        cmds.connectAttr('{}.normalizedNormal'.format(pointInfo), '{}.input2'.format(sideVector))

        fourByFour = cmds.createNode('fourByFourMatrix', name='ribbonOutput#')
        for x, attr in ((0, 'normalizedTangentV'), (1, 'normalizedNormal'), (3, 'position')):
            for y, axis in enumerate(('X', 'Y', 'Z')):
                srcPlug = '{}.{}{}'.format(pointInfo, attr, axis)
                destPlug = '{}.in{}{}'.format(fourByFour, x, y)
                cmds.connectAttr(srcPlug, destPlug)

        for x, axis in enumerate(('X', 'Y', 'Z')):
            srcPlug = '{}.output{}'.format(sideVector, axis)
            destPlug = '{}.in2{}'.format(fourByFour, x)
            cmds.connectAttr(srcPlug, destPlug)

        outputMatrixPlugs.append('{}.output'.format(fourByFour))

    return srf, outputMatrixPlugs
