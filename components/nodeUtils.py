from maya import cmds


class RotateOrder(object):
    xyz = 0
    yzx = 1
    zxy = 2
    xzy = 3
    yxz = 4
    zyx = 5


def get(value, defaultValue):
    if value is None:
        return defaultValue
    return value


class Plug(object):

    def __init__(self, name):
        self.name = str(name)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return repr(self.name)

    def connectOut(self, destinationPlug, force=False):
        cmds.connectAttr(self, destinationPlug, force=force)

    def connectIn(self, sourcePlug, force=False):
        cmds.connectAttr(sourcePlug, self, force=force)

    def get(self):
        return cmds.getAttr(self)

    def set(self, value):
        try:
            cmds.setAttr(self, value)
            return
        except RuntimeError:
            pass

        try:
            cmds.setAttr(self, value, type='matrix')
            return
        except RuntimeError:
            pass

    def index(self, index):
        return Plug('{}[{}]'.format(self, index))

    def child(self, name):
        return Plug('{}.{}'.format(self, name))


class Node(object):

    mayaTypeStr = 'unknown'

    def __init__(self, name):
        self.name = str(name)

        self.message = Plug('{}.message'.format(self))

    def __repr__(self):
        return repr(self.name)

    def __str__(self):
        return str(self.name)

    @classmethod
    def create(cls, name=None):
        name = get(name, '{}#'.format(cls.mayaTypeStr))
        node = cmds.createNode(cls.mayaTypeStr, name=name)
        return cls(node)

    def addFloatAttr(self, longName, defaultValue=0.0, keyable=False, min=None, max=None):
        kwargs = {
            'longName': str(longName),
            'defaultValue': float(defaultValue),
            'keyable': bool(keyable)
        }

        if min is not None:
            kwargs['min'] = float(min)

        if max is not None:
            kwargs['max'] = float(max)

        cmds.addAttr(self, **kwargs)

        return Plug('{}.{}'.format(self, longName))


class MultiplyDivide(Node):
    
    mayaTypeStr = 'multiplyDivide'

    def __init__(self, name):
        super(MultiplyDivide, self).__init__(name)

        self.input1 = Plug('{}.input1'.format(self))
        self.input1X = Plug('{}.input1X'.format(self))
        self.input1Y = Plug('{}.input1Y'.format(self))
        self.input1Z = Plug('{}.input1Z'.format(self))

        self.input2 = Plug('{}.input2'.format(self))
        self.input2X = Plug('{}.input2X'.format(self))
        self.input2Y = Plug('{}.input2Y'.format(self))
        self.input2Z = Plug('{}.input2Z'.format(self))

        self.output = Plug('{}.output'.format(self))
        self.outputX = Plug('{}.outputX'.format(self))
        self.outputY = Plug('{}.outputY'.format(self))
        self.outputZ = Plug('{}.outputZ'.format(self))


class BlendColors(Node):

    mayaTypeStr = 'blendColors'

    def __init__(self, name):
        super(BlendColors, self).__init__(name)

        self.blender = Plug('{}.blender'.format(self))

        self.color1 = Plug('{}.color1'.format(self))
        self.color1R = Plug('{}.color1R'.format(self))
        self.color1G = Plug('{}.color1G'.format(self))
        self.color1B = Plug('{}.color1B'.format(self))

        self.color2 = Plug('{}.color2'.format(self))
        self.color2R = Plug('{}.color2R'.format(self))
        self.color2G = Plug('{}.color2G'.format(self))
        self.color2B = Plug('{}.color2B'.format(self))

        self.output = Plug('{}.output'.format(self))
        self.outputR = Plug('{}.outputR'.format(self))
        self.outputG = Plug('{}.outputG'.format(self))
        self.outputB = Plug('{}.outputB'.format(self))


class DecomposeMatrix(Node):

    mayaTypeStr = 'decomposeMatrix'

    def __init__(self, name):
        super(DecomposeMatrix, self).__init__(name)

        self.inputMatrix = Plug('{}.inputMatrix'.format(self))

        self.outputTranslate = Plug('{}.outputTranslate'.format(self))
        self.outputTranslateX = Plug('{}.outputTranslateX'.format(self))
        self.outputTranslateY = Plug('{}.outputTranslateY'.format(self))
        self.outputTranslateZ = Plug('{}.outputTranslateZ'.format(self))
        
        self.outputRotate = Plug('{}.outputRotate'.format(self))
        self.outputRotateX = Plug('{}.outputRotateX'.format(self))
        self.outputRotateY = Plug('{}.outputRotateY'.format(self))
        self.outputRotateZ = Plug('{}.outputRotateZ'.format(self))
        
        self.outputQuat = Plug('{}.outputQuat'.format(self))
        self.outputQuatX = Plug('{}.outputQuatX'.format(self))
        self.outputQuatY = Plug('{}.outputQuatY'.format(self))
        self.outputQuatZ = Plug('{}.outputQuatZ'.format(self))
        self.outputQuatW = Plug('{}.outputQuatW'.format(self))
        
        self.outputScale = Plug('{}.outputScale'.format(self))
        self.outputScaleX = Plug('{}.outputScaleX'.format(self))
        self.outputScaleY = Plug('{}.outputScaleY'.format(self))
        self.outputScaleZ = Plug('{}.outputScaleZ'.format(self))
        
        self.outputShear = Plug('{}.outputShear'.format(self))
        self.outputShearX = Plug('{}.outputShearX'.format(self))
        self.outputShearY = Plug('{}.outputShearY'.format(self))
        self.outputShearZ = Plug('{}.outputShearZ'.format(self))


class DistanceBetween(Node):

    mayaTypeStr = 'distanceBetween'

    def __init__(self, name):
        super(DistanceBetween, self).__init__(name)

        self.point1 = Plug('{}.point1'.format(self))
        self.point2 = Plug('{}.point2'.format(self))
        self.distance = Plug('{}.distance'.format(self))


class PlusMinusAverage(Node):

    mayaTypeStr = 'plusMinusAverage'

    def __init__(self, name):
        super(PlusMinusAverage, self).__init__(name)

        self.input1D = Plug('{}.input1D'.format(self))
        self.input2D = Plug('{}.input2D'.format(self))
        self.input3D = Plug('{}.input3D'.format(self))

        self.output1D = Plug('{}.output1D'.format(self))
        self.output2D = Plug('{}.output2D'.format(self))
        self.output3D = Plug('{}.output3D'.format(self))


class MultMatrix(Node):

    mayaTypeStr = 'multMatrix'

    def __init__(self, name):
        super(MultMatrix, self).__init__(name)

        self.matrixIn = Plug('{}.matrixIn'.format(name))
        self.matrixSum = Plug('{}.matrixSum'.format(name))


class QuatToEuler(Node):

    mayaTypeStr = 'quatToEuler'

    def __init__(self, name):
        super(QuatToEuler, self).__init__(name)

        self.inputQuat = Plug('{}.inputQuat'.format(self))
        self.inputQuatX = Plug('{}.inputQuatX'.format(self))
        self.inputQuatY = Plug('{}.inputQuatY'.format(self))
        self.inputQuatZ = Plug('{}.inputQuatZ'.format(self))
        self.inputQuatW = Plug('{}.inputQuatW'.format(self))

        self.inputRotateOrder = Plug('{}.inputRotateOrder'.format(self))

        self.outputRotate = Plug('{}.outputRotate'.format(self))
        self.outputRotateX = Plug('{}.outputRotateX'.format(self))
        self.outputRotateY = Plug('{}.outputRotateY'.format(self))
        self.outputRotateZ = Plug('{}.outputRotateZ'.format(self))


class ComposeMatrix(Node):

    mayaTypeStr = 'composeMatrix'

    def __init__(self, name):
        super(ComposeMatrix, self).__init__(name)

        self.inputTranslate = Plug('{}.inputTranslate'.format(self))
        self.inputTranslateX = Plug('{}.inputTranslateX'.format(self))
        self.inputTranslateY = Plug('{}.inputTranslateY'.format(self))
        self.inputTranslateZ = Plug('{}.inputTranslateZ'.format(self))
        
        self.inputRotate = Plug('{}.inputRotate'.format(self))
        self.inputRotateX = Plug('{}.inputRotateX'.format(self))
        self.inputRotateY = Plug('{}.inputRotateY'.format(self))
        self.inputRotateZ = Plug('{}.inputRotateZ'.format(self))
        
        self.inputQuat = Plug('{}.inputQuat'.format(self))
        self.inputQuatX = Plug('{}.inputQuatX'.format(self))
        self.inputQuatY = Plug('{}.inputQuatY'.format(self))
        self.inputQuatZ = Plug('{}.inputQuatZ'.format(self))
        
        self.inputScale = Plug('{}.inputScale'.format(self))
        self.inputScaleX = Plug('{}.inputScaleX'.format(self))
        self.inputScaleY = Plug('{}.inputScaleY'.format(self))
        self.inputScaleZ = Plug('{}.inputScaleZ'.format(self))
        
        self.inputShear = Plug('{}.inputShear'.format(self))
        self.inputShearX = Plug('{}.inputShearX'.format(self))
        self.inputShearY = Plug('{}.inputShearY'.format(self))
        self.inputShearZ = Plug('{}.inputShearZ'.format(self))

        self.useEulerRotation = Plug('{}.useEulerRotation'.format(self))

        self.inputRotateOrder = Plug('{}.inputRotateOrder'.format(self))

        self.outputMatrix = Plug('{}.outputMatrix'.format(self))


class Transform(Node):
    
    mayaTypeStr = 'transform'
    
    def __init__(self, name):
        super(Transform, self).__init__(name)
        
        self.translate = Plug('{}.translate'.format(self))
        self.translateX = Plug('{}.translateX'.format(self))
        self.translateY = Plug('{}.translateY'.format(self))
        self.translateZ = Plug('{}.translateZ'.format(self))

        self.rotate = Plug('{}.rotate'.format(self))
        self.rotateX = Plug('{}.rotateX'.format(self))
        self.rotateY = Plug('{}.rotateY'.format(self))
        self.rotateZ = Plug('{}.rotateZ'.format(self))

        self.scale = Plug('{}.scale'.format(self))
        self.scaleX = Plug('{}.scaleX'.format(self))
        self.scaleY = Plug('{}.scaleY'.format(self))
        self.scaleZ = Plug('{}.scaleZ'.format(self))

        self.shear = Plug('{}.shear'.format(self))

        self.visibility = Plug('{}.visibility'.format(self))

        self.worldMatrix = Plug('{}.worldMatrix'.format(self))
        self.worldInverseMatrix = Plug('{}.worldInverseMatrix'.format(self))
        self.parentInverseMatrix = Plug('{}.parentInverseMatrix'.format(self))


class Joint(Transform):

    def __init__(self, name):
        super(Joint, self).__init__(name)

        self.jointOrient = Plug('{}.jointOrient'.format(self))


class BlendMatrix(Node):

    mayaTypeStr = 'blendMatrix'

    matricesMatrixAttr = 'matrix'
    matricesOffsetAttr = 'offset'

    def __init__(self, name):
        super(BlendMatrix, self).__init__(name)

        self.blender = Plug('{}.blender'.format(self))
        self.resultMatrix = Plug('{}.resultMatrix'.format(self))
        self.matrices = Plug('{}.matrices'.format(self))
        
        self.parentInverseMatrix = Plug('{}.parentInverseMatrix'.format(self))

        self.jointOrient = Plug('{}.jointOrient'.format(self))

        self.translate = Plug('{}.translate'.format(self))
        self.translateX = Plug('{}.translateX'.format(self))
        self.translateY = Plug('{}.translateY'.format(self))
        self.translateZ = Plug('{}.translateZ'.format(self))
        
        self.rotate = Plug('{}.rotate'.format(self))
        self.rotateX = Plug('{}.rotateX'.format(self))
        self.rotateY = Plug('{}.rotateY'.format(self))
        self.rotateZ = Plug('{}.rotateZ'.format(self))
        
        self.scale = Plug('{}.scale'.format(self))
        self.scaleX = Plug('{}.scaleX'.format(self))
        self.scaleY = Plug('{}.scaleY'.format(self))
        self.scaleZ = Plug('{}.scaleZ'.format(self))
        
        self.shear = Plug('{}.shear'.format(self))
        self.shearX = Plug('{}.shearX'.format(self))
        self.shearY = Plug('{}.shearY'.format(self))
        self.shearZ = Plug('{}.shearZ'.format(self))

        self.quat = Plug('{}.quat'.format(self))
        self.quatX = Plug('{}.quatX'.format(self))
        self.quatY = Plug('{}.quatY'.format(self))
        self.quatZ = Plug('{}.quatZ'.format(self))
        self.quatW = Plug('{}.quatW'.format(self))
