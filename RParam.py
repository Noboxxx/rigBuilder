import re


class ParameterError(BaseException):
    pass


class BaseParameter(object):

    def __init__(self, value):
        self.check(value)
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if other.value != self.value:
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __mirror__(self):
        return None

    @classmethod
    def check(cls, value):
        raise NotImplementedError

    @classmethod
    def isOne(cls, value):
        try:
            cls.check(value)
            return True
        except ParameterError:
            return False


class Side(BaseParameter):  # should be enum

    left = 'L'
    right = 'R'
    center = 'C'

    mirrorTable = {
        left: right,
        right: left,
        center: None
    }

    @classmethod
    def check(cls, value):
        if value not in cls.mirrorTable.keys():
            raise ParameterError(
                'The given side \'{}\' is not part of {}'.format(value, cls.mirrorTable.keys())
            )

    def __mirror__(self):
        return self.__class__(self.mirrorTable[self.value])


class Name(BaseParameter):

    pattern = r'^[a-zA-Z_]+[A-Za-z0-9_]*$'

    def __add__(self, other):
        if isinstance(other, Name):
            return self.__class__('{}_{}'.format(self.value, other.value))
        raise TypeError(
            'unsupported operand type(s) for +: \'{}\' and \'{}\''.format(self.__class__.__name__, type(other).__name__)
        )

    @classmethod
    def check(cls, value):
        if not isinstance(value, basestring):
            raise ParameterError(
                'The given name should be of type \'basestring\' not \'{}\''.format(type(value).__name__)
            )
        print
        if not re.match(cls.pattern, value):
            raise ParameterError(
                'The given name \'{}\' doesnt fit the name pattern: \'{}\''.format(value, cls.pattern)
            )


class Index(BaseParameter):
    @classmethod
    def check(cls, value):
        if not isinstance(value, int):
            raise ParameterError(
                'The given index should be of type \'int\' not \'{}\''.format(type(value).__name__)
            )
        if value < 0:
            raise ParameterError(
                'Valid index starts at 0 -> {}'.format(value)
            )


class Axis(BaseParameter):  # should be enum

    x = 'x'
    y = 'y'
    z = 'z'

    axis = (x, y, z)

    @classmethod
    def check(cls, value):
        if value not in cls.axis:
            raise ParameterError(
                'The given axis \'{}\' is not part of {}'.format(value, cls.axis)
            )


class Vector3(BaseParameter):
    
    def __init__(self, *value):
        super(Vector3, self).__init__(value)

    def __iter__(self):
        return iter(self.value)

    @property
    def x(self):
        return self.value[0]

    @property
    def y(self):
        return self.value[1]

    @property
    def z(self):
        return self.value[2]

    @classmethod
    def check(cls, value):
        if len(value) != 3:
            raise ParameterError(
                'The given values should be an iterable of size 3 -> {}'.format(value)
            )
        types = [type(v) for v in value]

        if types != [float, float, float]:
            raise ParameterError(
                'The given values should be of type (float, float, float) -> {}'.format(types)
            )


