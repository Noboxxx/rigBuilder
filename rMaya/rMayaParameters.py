class ParameterError(BaseException):
    pass


class BaseParameter(object):

    def __init__(self, *args, **kwargs):
        self.check(*args, **kwargs)

    @classmethod
    def check(cls, *args, **kwargs):
        pass

    def __mirror__(self):
        return None


class Side(BaseParameter):

    left = 'L'
    right = 'R'
    center = 'C'

    mirrorTable = {
        left: right,
        right: left,
        center: None
    }

    def __init__(self, side):
        super(Side, self).__init__(side)
        self.side = side

    def __str__(self):
        return self.side

    def __repr__(self):
        return self.side

    @classmethod
    def check(cls, side):
        if side not in cls.mirrorTable.keys():
            raise ParameterError('The given side \'{}\' is not part of {}'.format(side, cls.mirrorTable.keys()))

    def __mirror__(self):
        return self.__class__(self.mirrorTable[self.side])


class Name(BaseParameter):

    pattern = ''

    def __init__(self, name):
        super(Name, self).__init__(name)
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @classmethod
    def check(cls, name):
        if not isinstance(name, basestring):
            raise ParameterError(
                'The given name should be of type \'basestring\' not \'{}\''.format(
                    type(name).__name__
                )
            )


class Index(BaseParameter):
    pass


class Color(BaseParameter):
    pass


class Palette(BaseParameter):
    pass

