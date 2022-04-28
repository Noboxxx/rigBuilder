from maya.api import OpenMaya


def blendValue(a, b, blender):  # type: (float, float, float) -> float
    return a * (1 - blender) + b * blender


def blendMatrices(a, b, blender):  # type: (list, list, float) -> OpenMaya.MMatrix
    a = OpenMaya.MTransformationMatrix(OpenMaya.MMatrix(list(a)))
    b = OpenMaya.MTransformationMatrix(OpenMaya.MMatrix(list(b)))

    t = [blendValue(x, y, blender) for x, y in zip(a.translation(OpenMaya.MSpace.kWorld), b.translation(OpenMaya.MSpace.kWorld))]
    q = OpenMaya.MQuaternion.slerp(a.rotation(asQuaternion=True), b.rotation(asQuaternion=True), blender)
    s = [blendValue(x, y, blender) for x, y in zip(a.scale(OpenMaya.MSpace.kWorld), b.scale(OpenMaya.MSpace.kWorld))]
    sh = [blendValue(x, y, blender) for x, y in zip(a.shear(OpenMaya.MSpace.kWorld), b.shear(OpenMaya.MSpace.kWorld))]

    r = OpenMaya.MTransformationMatrix()
    r.setTranslation(OpenMaya.MVector(t), OpenMaya.MSpace.kWorld)
    r.setRotation(q)
    r.setScale(s, OpenMaya.MSpace.kWorld)
    r.setShear(sh, OpenMaya.MSpace.kWorld)

    return r.asMatrix()
