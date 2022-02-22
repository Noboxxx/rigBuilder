from maya.api import OpenMaya


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class BlendMatrixNode(OpenMaya.MPxNode):
    name = 'blendMatrix'
    id = OpenMaya.MTypeId(0x870FE)
    classify = 'utility/general'

    blenderAttr = OpenMaya.MObject()
    parentInverseMatrixAttr = OpenMaya.MObject()

    matricesAttr = OpenMaya.MObject()
    matrixAttr = OpenMaya.MObject()
    offsetAttr = OpenMaya.MObject()

    resultMatrixAttr = OpenMaya.MObject()

    translateAttr = OpenMaya.MObject()
    rotateAttr = OpenMaya.MObject()
    scaleAttr = OpenMaya.MObject()
    shearAttr = OpenMaya.MObject()

    quatAttr = OpenMaya.MObject()
    quatXAttr = OpenMaya.MObject()
    quatYAttr = OpenMaya.MObject()
    quatZAttr = OpenMaya.MObject()
    quatWAttr = OpenMaya.MObject()

    jointOrientAttr = OpenMaya.MObject()
    
    @staticmethod
    def get(ls, index):
        listLength = len(ls)
        if index >= listLength:
            return ls[listLength - 1]
        return ls[index]

    @staticmethod
    def blend(a, b, blender):
        return a * (1 - blender) + b * blender

    def compute(self, plug, dataBlock):  # type: (OpenMaya.MPlug, OpenMaya.MDataBlock) -> None
        # Extract matrices and offsets
        matrices = list()
        matrixInDataHandle = dataBlock.inputArrayValue(self.matricesAttr)
        while not matrixInDataHandle.isDone():
            data = matrixInDataHandle.inputValue()  # type: OpenMaya.MDataHandle
            matrix = data.child(self.matrixAttr).asMatrix()
            offset = data.child(self.offsetAttr).asMatrix()
            matrices.append((matrix, offset))
            matrixInDataHandle.next()

        # Extract blender
        blender = dataBlock.inputValue(self.blenderAttr).asFloat()

        # Extract joint orient
        jointOrient = dataBlock.inputValue(self.jointOrientAttr).asDouble3()

        # Extract parentInverse Matrix
        parentInverseMatrix = dataBlock.inputValue(self.parentInverseMatrixAttr).asMatrix()

        #
        if not matrices:
            matrices.append((OpenMaya.MMatrix(), OpenMaya.MMatrix()))

        if blender < 0.0:
            blender = 0.0

        # Find matrices to blend together
        previousIndex = int(blender)
        previousMatrix, previousOffset = self.get(matrices, previousIndex)
        previousMatrixResult = previousOffset * previousMatrix * parentInverseMatrix

        nextIndex = previousIndex + 1
        nextMatrix, nextOffset = self.get(matrices, nextIndex)
        nextMatrixResult = nextOffset * nextMatrix * parentInverseMatrix

        # Blend Matrices
        localBlender = blender % 1.0

        previousTransformationMatrix = OpenMaya.MTransformationMatrix(previousMatrixResult)
        previousTranslation = previousTransformationMatrix.translation(OpenMaya.MSpace.kWorld)
        previousRotation = previousTransformationMatrix.rotation(asQuaternion=True)  # type: OpenMaya.MQuaternion
        previousScale = previousTransformationMatrix.scale(OpenMaya.MSpace.kWorld)
        previousShear = previousTransformationMatrix.shear(OpenMaya.MSpace.kWorld)

        nextTransformationMatrix = OpenMaya.MTransformationMatrix(nextMatrixResult)
        nextTranslation = nextTransformationMatrix.translation(OpenMaya.MSpace.kWorld)
        nextRotation = nextTransformationMatrix.rotation(asQuaternion=True)  # type: OpenMaya.MQuaternion
        nextScale = nextTransformationMatrix.scale(OpenMaya.MSpace.kWorld)
        nextShear = nextTransformationMatrix.shear(OpenMaya.MSpace.kWorld)

        resultTranslation = [self.blend(a, b, localBlender) for a, b in zip(previousTranslation, nextTranslation)]
        resultQuat = OpenMaya.MQuaternion.slerp(previousRotation, nextRotation, localBlender)
        resultScale = [self.blend(a, b, localBlender) for a, b in zip(previousScale, nextScale)]
        resultShear = [self.blend(a, b, localBlender) for a, b in zip(previousShear, nextShear)]

        # joint Orient compensate here
        inverseJointOrientQuat = OpenMaya.MEulerRotation(*jointOrient).asQuaternion().inverse()
        resultQuat = resultQuat * inverseJointOrientQuat

        # Result Transformation Matrix
        resultTransformationMatrix = OpenMaya.MTransformationMatrix()
        resultTransformationMatrix.setTranslation(OpenMaya.MVector(resultTranslation), OpenMaya.MSpace.kWorld)
        resultTransformationMatrix.setRotation(resultQuat)
        resultTransformationMatrix.setScale(resultScale, OpenMaya.MSpace.kWorld)
        resultTransformationMatrix.setShear(resultShear, OpenMaya.MSpace.kWorld)

        # Set result Matrix
        resultMatrixDataHandle = dataBlock.outputValue(self.resultMatrixAttr)  # type: OpenMaya.MDataHandle
        resultMatrixDataHandle.setMMatrix(resultTransformationMatrix.asMatrix())
        resultMatrixDataHandle.setClean()

        # Set result Transforms
        translateDataHandle = dataBlock.outputValue(self.translateAttr)  # type: OpenMaya.MDataHandle
        translateDataHandle.set3Double(*resultTranslation)
        translateDataHandle.setClean()

        rotateDataHandle = dataBlock.outputValue(self.rotateAttr)  # type: OpenMaya.MDataHandle
        rotateDataHandle.set3Double(*resultTransformationMatrix.rotation(asQuaternion=False))
        rotateDataHandle.setClean()

        scaleDataHandle = dataBlock.outputValue(self.scaleAttr)  # type: OpenMaya.MDataHandle
        scaleDataHandle.set3Double(*resultScale)
        scaleDataHandle.setClean()

        shearDataHandle = dataBlock.outputValue(self.shearAttr)  # type: OpenMaya.MDataHandle
        shearDataHandle.set3Double(*resultShear)
        shearDataHandle.setClean()

        quatAttributes = self.quatXAttr, self.quatYAttr, self.quatZAttr, self.quatWAttr
        for attr, value in zip(quatAttributes, resultQuat):
            quatDataHandle = dataBlock.outputValue(attr)  # type: OpenMaya.MDataHandle
            quatDataHandle.setDouble(value)
            quatDataHandle.setClean()

    @classmethod
    def create(cls):
        return cls()

    @classmethod
    def init(cls):
        numericAttributeFn = OpenMaya.MFnNumericAttribute()
        matrixAttributeFn = OpenMaya.MFnMatrixAttribute()
        compoundAttributeFn = OpenMaya.MFnCompoundAttribute()
        unitAttributeFn = OpenMaya.MFnUnitAttribute()

        # matrixIn
        cls.matrixAttr = matrixAttributeFn.create('matrix', 'm', OpenMaya.MFnMatrixAttribute.kDouble)
        cls.offsetAttr = matrixAttributeFn.create('offset', 'off', OpenMaya.MFnMatrixAttribute.kDouble)

        cls.matricesAttr = compoundAttributeFn.create('matrices', 'matrices')
        compoundAttributeFn.addChild(cls.matrixAttr)
        compoundAttributeFn.addChild(cls.offsetAttr)
        compoundAttributeFn.writable = True
        compoundAttributeFn.readable = False
        compoundAttributeFn.array = True
        compoundAttributeFn.keyable = False
        compoundAttributeFn.hidden = False

        cls.addAttribute(cls.matricesAttr)

        # outputTranslate
        translateXAttr = numericAttributeFn.create('translateX', 'tx', OpenMaya.MFnNumericData.kDouble)
        translateYAttr = numericAttributeFn.create('translateY', 'ty', OpenMaya.MFnNumericData.kDouble)
        translateZAttr = numericAttributeFn.create('translateZ', 'tz', OpenMaya.MFnNumericData.kDouble)

        cls.translateAttr = numericAttributeFn.create('translate', 't', translateXAttr, translateYAttr, translateZAttr)
        numericAttributeFn.writable = False
        numericAttributeFn.readable = True
        numericAttributeFn.keyable = False
        numericAttributeFn.hidden = False

        cls.addAttribute(cls.translateAttr)

        # outputRotate
        rotateXAttr = unitAttributeFn.create('rotateX', 'rx', unitAttributeFn.kAngle)
        rotateYAttr = unitAttributeFn.create('rotateY', 'ry', unitAttributeFn.kAngle)
        rotateZAttr = unitAttributeFn.create('rotateZ', 'rz', unitAttributeFn.kAngle)

        cls.rotateAttr = numericAttributeFn.create('rotate', 'r', rotateXAttr, rotateYAttr, rotateZAttr)
        numericAttributeFn.writable = False
        numericAttributeFn.readable = True
        numericAttributeFn.keyable = False
        numericAttributeFn.hidden = False

        cls.addAttribute(cls.rotateAttr)

        # outputScale
        scaleXAttr = numericAttributeFn.create('scaleX', 'sx', OpenMaya.MFnNumericData.kDouble)
        scaleYAttr = numericAttributeFn.create('scaleY', 'sy', OpenMaya.MFnNumericData.kDouble)
        scaleZAttr = numericAttributeFn.create('scaleZ', 'sz', OpenMaya.MFnNumericData.kDouble)

        cls.scaleAttr = numericAttributeFn.create('scale', 's', scaleXAttr, scaleYAttr, scaleZAttr)
        numericAttributeFn.writable = False
        numericAttributeFn.readable = True
        numericAttributeFn.keyable = False
        numericAttributeFn.hidden = False

        cls.addAttribute(cls.scaleAttr)

        # outputShear
        shearXAttr = numericAttributeFn.create('shearX', 'shearX', OpenMaya.MFnNumericData.kDouble)
        shearYAttr = numericAttributeFn.create('shearY', 'shearY', OpenMaya.MFnNumericData.kDouble)
        shearZAttr = numericAttributeFn.create('shearZ', 'shearZ', OpenMaya.MFnNumericData.kDouble)

        cls.shearAttr = numericAttributeFn.create('shear', 'shear', shearXAttr, shearYAttr, shearZAttr)
        numericAttributeFn.writable = False
        numericAttributeFn.readable = True
        numericAttributeFn.keyable = False
        numericAttributeFn.hidden = False

        cls.addAttribute(cls.shearAttr)

        # outputQuat
        cls.quatXAttr = numericAttributeFn.create('quatX', 'quatX', OpenMaya.MFnNumericData.kDouble)
        cls.quatYAttr = numericAttributeFn.create('quatY', 'quatY', OpenMaya.MFnNumericData.kDouble)
        cls.quatZAttr = numericAttributeFn.create('quatZ', 'quatZ', OpenMaya.MFnNumericData.kDouble)
        cls.quatWAttr = numericAttributeFn.create('quatW', 'quatW', OpenMaya.MFnNumericData.kDouble)

        cls.quatAttr = compoundAttributeFn.create('quat', 'quat')
        compoundAttributeFn.addChild(cls.quatXAttr)
        compoundAttributeFn.addChild(cls.quatYAttr)
        compoundAttributeFn.addChild(cls.quatZAttr)
        compoundAttributeFn.addChild(cls.quatWAttr)
        compoundAttributeFn.writable = False
        compoundAttributeFn.readable = True
        compoundAttributeFn.keyable = False
        compoundAttributeFn.hidden = False

        cls.addAttribute(cls.quatAttr)

        # blender input attr
        cls.blenderAttr = numericAttributeFn.create('blender', 'bl', OpenMaya.MFnNumericData.kFloat)
        numericAttributeFn.writable = True
        numericAttributeFn.readable = False
        numericAttributeFn.keyable = True

        cls.addAttribute(cls.blenderAttr)

        # inputParentInverseMatrixAttr
        cls.parentInverseMatrixAttr = matrixAttributeFn.create(
            'parentInverseMatrix', 'pim', OpenMaya.MFnMatrixAttribute.kDouble
        )
        matrixAttributeFn.writable = True
        matrixAttributeFn.readable = False
        matrixAttributeFn.array = False

        cls.addAttribute(cls.parentInverseMatrixAttr)

        # outMatrix
        cls.resultMatrixAttr = matrixAttributeFn.create('resultMatrix', 'rm', OpenMaya.MFnMatrixAttribute.kDouble)
        matrixAttributeFn.writable = False
        matrixAttributeFn.readable = True
        matrixAttributeFn.array = False

        cls.addAttribute(cls.resultMatrixAttr)

        # jointOrient
        jointOrientXAttr = unitAttributeFn.create('jointOrientX', 'jox', unitAttributeFn.kAngle)
        jointOrientYAttr = unitAttributeFn.create('jointOrientY', 'joy', unitAttributeFn.kAngle)
        jointOrientZAttr = unitAttributeFn.create('jointOrientZ', 'joz', unitAttributeFn.kAngle)

        cls.jointOrientAttr = numericAttributeFn.create(
            'jointOrient', 'jo',
            jointOrientXAttr, jointOrientYAttr, jointOrientZAttr
        )
        numericAttributeFn.writable = True
        numericAttributeFn.readable = False
        numericAttributeFn.keyable = True
        numericAttributeFn.hidden = False

        cls.addAttribute(cls.jointOrientAttr)

        # effects
        cls.attributeAffects(cls.matricesAttr, cls.resultMatrixAttr)
        cls.attributeAffects(cls.blenderAttr, cls.resultMatrixAttr)
        cls.attributeAffects(cls.parentInverseMatrixAttr, cls.resultMatrixAttr)
        cls.attributeAffects(cls.jointOrientAttr, cls.resultMatrixAttr)

        cls.attributeAffects(cls.matricesAttr, cls.translateAttr)
        cls.attributeAffects(cls.blenderAttr, cls.translateAttr)
        cls.attributeAffects(cls.parentInverseMatrixAttr, cls.translateAttr)
        cls.attributeAffects(cls.jointOrientAttr, cls.translateAttr)

        cls.attributeAffects(cls.matricesAttr, cls.rotateAttr)
        cls.attributeAffects(cls.blenderAttr, cls.rotateAttr)
        cls.attributeAffects(cls.parentInverseMatrixAttr, cls.rotateAttr)
        cls.attributeAffects(cls.jointOrientAttr, cls.rotateAttr)

        cls.attributeAffects(cls.matricesAttr, cls.quatAttr)
        cls.attributeAffects(cls.blenderAttr, cls.quatAttr)
        cls.attributeAffects(cls.parentInverseMatrixAttr, cls.quatAttr)
        cls.attributeAffects(cls.jointOrientAttr, cls.quatAttr)

        cls.attributeAffects(cls.matricesAttr, cls.scaleAttr)
        cls.attributeAffects(cls.blenderAttr, cls.scaleAttr)
        cls.attributeAffects(cls.parentInverseMatrixAttr, cls.scaleAttr)
        cls.attributeAffects(cls.jointOrientAttr, cls.scaleAttr)

        cls.attributeAffects(cls.matricesAttr, cls.shearAttr)
        cls.attributeAffects(cls.blenderAttr, cls.shearAttr)
        cls.attributeAffects(cls.parentInverseMatrixAttr, cls.shearAttr)
        cls.attributeAffects(cls.jointOrientAttr, cls.shearAttr)


def initializePlugin(plug):
    mplugin = OpenMaya.MFnPlugin(plug)
    mplugin.registerNode(
        BlendMatrixNode.name,
        BlendMatrixNode.id,
        BlendMatrixNode.create,
        BlendMatrixNode.init,
        OpenMaya.MPxNode.kDependNode,
        BlendMatrixNode.classify
    )


def uninitializePlugin(plug):
    mplugin = OpenMaya.MFnPlugin(plug)
    mplugin.deregisterNode(BlendMatrixNode.id)
