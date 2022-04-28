import math
import os


class Side(str):

    mirrorTable = {
        'L': 'R',
        'R': 'L',
        'C': 'C',
    }

    def __init__(self, side):  # type: (str) -> None
        if str(side) not in self.mirrorTable:
            raise ValueError('Unrecognized Side \'{}\'.'.format(side))
        super(Side, self).__init__(side)

    def mirrored(self):
        return self.__class__(self.mirrorTable[self])


class Color(list):

    @staticmethod
    def clampValue(minimum=0, value=0, maximum=255):
        return int(max(minimum, min(maximum, value)))

    def __init__(self, color):  # type: (List[int, int, int]) -> None
        color = [self.clampValue(c) for c in color]
        super(Color, self).__init__(color)

    def __add__(self, other):
        return self._operation(other, self.add)

    def __div__(self, other):
        return self._operation(other, self.div)

    def __mul__(self, other):
        return self._operation(other, self.mul)

    def __sub__(self, other):
        return self._operation(other, self.sub)

    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def sub(a, b):
        return a - b

    @staticmethod
    def div(a, b):
        return a / b

    @staticmethod
    def mul(a, b):
        return a * b

    def _operation(self, other, func):
        if isinstance(other, list):
            return Color([func(a, b) for a, b in zip(self, other)])
        elif isinstance(other, (int, float)):
            return Color([func(a, other) for a in self])
        raise TypeError('Cannot add \'{}\' to Color.'.format(type(self).__name__))

    @property
    def r(self):
        return self[0]

    @r.setter
    def r(self, v):
        self[0] = self.clampValue(v)

    @property
    def g(self):
        return self[0]

    @g.setter
    def g(self, v):
        self[0] = self.clampValue(v)

    @property
    def b(self):
        return self[0]

    @b.setter
    def b(self, v):
        self[0] = self.clampValue(v)

    def mirrored(self):
        # mirroredColor = list()
        # for v in self:
        #     distance = 127.5 - v
        #     r = distance * 2 + v
        #     mirroredColor.append(int(r))
        # return self.__class__(mirroredColor)
        return self.__class__((self[1], self[2], self[0]))


class UnsignedInt(int):

    def __init__(self, value):  # type: (int) -> None
        if value < 0:
            raise ValueError('Value should be positive.')
        super(UnsignedInt, self).__init__(value)


class UnsignedFloat(float):

    def __init__(self, value):  # type: (float) -> None
        if value < 0.0:
            raise ValueError('Value should be positive.')
        super(UnsignedFloat, self).__init__(value)


class Vector(list):

    def __init__(self, seq):
        seq = map(float, seq)

        super(Vector, self).__init__(seq)

        magnitude = self.magnitude()
        if magnitude <= 0.0:
            raise ValueError('magnitude is equal or less than 0.0 -> {}'.format(magnitude))

    def copy(self):
        return self.__class__(*self)

    def mirrored(self, mirrorAxis='x'):
        vectorCopy = self.copy()
        vectorCopy.mirror(mirrorAxis)
        return vectorCopy

    def mirror(self, mirrorAxis='x'):
        if mirrorAxis == 'x':
            self[0] *= -1
        elif mirrorAxis == 'y':
            self[1] *= -1
        elif mirrorAxis == 'z':
            self[2] *= -1
        else:
            raise ValueError('Unrecognized axis -> {}'.format(mirrorAxis))

    def magnitude(self):
        result = 0
        for scalar in self:
            result += scalar ** 2.0
        return math.sqrt(result)

    def normalized(self):
        vectorCopy = self.copy()
        vectorCopy.normalize()
        return vectorCopy

    def normalize(self):
        magnitude = self.magnitude()
        for index in range(len(self)):
            self[index] /= magnitude


class Matrix(list):

    def __init__(self, seq=None):
        seq = map(float, seq) if seq is not None else (
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        )
        super(Matrix, self).__init__(seq)

    def rows(self):
        return (
            (self[0], self[1], self[2], self[3]),
            (self[4], self[5], self[6], self[7]),
            (self[8], self[9], self[10], self[11]),
            (self[12], self[13], self[14], self[15]),
        )

    def columns(self):
        return (
            (self[0], self[4], self[8], self[12]),
            (self[1], self[5], self[9], self[13]),
            (self[2], self[6], self[10], self[14]),
            (self[3], self[7], self[11], self[15]),
        )

    def copy(self):
        return self.__class__(self)

    def mirrored(self, mirrorAxis='x'):
        matrixCopy = self.copy()
        matrixCopy.mirror(mirrorAxis)
        return matrixCopy

    def mirror(self, mirrorAxis='x', compensateNegativeScale=True):
        if mirrorAxis == 'x':
            self[0] *= -1
            self[4] *= -1
            self[8] *= -1
            self[12] *= -1

        elif mirrorAxis == 'y':
            self[1] *= -1
            self[5] *= -1
            self[9] *= -1
            self[13] *= -1

        elif mirrorAxis == 'z':
            self[2] *= -1
            self[6] *= -1
            self[10] *= -1
            self[14] *= -1

        else:
            raise ValueError('Unrecognized mirror axis -> {}'.format(mirrorAxis))

        if compensateNegativeScale:
            self[0] *= -1
            self[1] *= -1
            self[2] *= -1

            self[4] *= -1
            self[5] *= -1
            self[6] *= -1

            self[8] *= -1
            self[9] *= -1
            self[10] *= -1

    def normalize(self):
        vectorX = Vector((self[0], self[1], self[2]))
        vectorX.normalize()
        self[0] = vectorX[0]
        self[1] = vectorX[1]
        self[2] = vectorX[2]

        vectorY = Vector((self[4], self[5], self[6]))
        vectorY.normalize()
        self[4] = vectorY[0]
        self[5] = vectorY[1]
        self[6] = vectorY[2]

        vectorZ = Vector((self[8], self[9], self[10]))
        vectorZ.normalize()
        self[8] = vectorZ[0]
        self[9] = vectorZ[1]
        self[10] = vectorZ[2]

    def normalized(self):
        matrixCopy = self.copy()
        matrixCopy.normalize()
        return matrixCopy

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            newMatrix = list()
            for column in self.rows()[:3]:
                for row in other.columns()[:3]:
                    result = 0
                    for c, r in zip(column, row):
                        result += c * r
                    newMatrix.append(result)
                newMatrix.append(0.0)
            newMatrix.append(self[12] + other[12])
            newMatrix.append(self[13] + other[13])
            newMatrix.append(self[14] + other[14])
            newMatrix.append(1.0)
            return self.__class__(*newMatrix)
        raise TypeError(
            'cannot do \'{}\' * \'{}\''.format(
                str(self.__class__),
                str(type(other)),
            )
        )


class Path(str):

    def __new__(cls, path):
        path = os.path.normpath(path) if path else ''
        return super(Path, cls).__new__(cls, path)

    def split(self):  # type: () -> (Path, Path)
        dirName, baseName = os.path.split(self)
        return self.__class__(dirName), self.__class__(baseName)

    @classmethod
    def join(cls, *paths):  # type: (List[Path]) -> Path
        return cls('\\'.join([cls(p) for p in paths]))


class File(Path):

    def open(self):  # type: () -> str
        with open(str(self), 'r') as f:
            return f.read()

    def write(self, string, force=False):  # type: (str, bool) -> None
        if os.path.exists(self) and force is False:
            raise RuntimeError('The path already exists. Use -force to override it -> {}'.format(self))

        with open(str(self), 'w') as f:
            f.write(str(string))


class Node(str):
    pass
