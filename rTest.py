import re


class Mirrorable(object):

    def __mirror__(self):
        return None


def mirror(obj):
    if hasattr(obj, '__mirror__'):
        return obj.__mirror__()
    return None


class RParameter(Mirrorable):

    def __init__(self, defaultValue=None):
        if defaultValue is None:
            self.value = defaultValue
        else:
            self.value = self.conform(defaultValue)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    def __ne__(self, other):
        return not self.__eq__(other)

    def setValue(self, value):
        print 'setValue', self.__class__.__name__, self.value, '->', value
        self.value = self.conform(value)

    @classmethod
    def conform(cls, value):
        return value


class RIndex(RParameter):

    @classmethod
    def conform(cls, value):
        value = int(value)
        if value < 0:
            raise ValueError('\'{}\' cannot be under 0'.format(value))
        return value


class RName(RParameter):

    pattern = r'^[a-zA-Z_][A-Z0-9a-z_]*$'

    @classmethod
    def conform(cls, value):
        value = str(value)
        if not re.match(cls.pattern, value):
            raise ValueError('\'{}\' doesnt fit the pattern \'{}\''.format(value, cls.pattern))
        return value


class RSide(RParameter):

    left = 'L'
    right = 'R'
    center = 'C'

    mirrorTable = {
        left: right,
        right: left,
        center: None,
    }

    def __mirror__(self):
        return self.__class__(self.mirrorTable[self.value])

    @classmethod
    def conform(cls, value):
        value = str(value)
        if value not in cls.mirrorTable.keys():
            raise ValueError('\'{}\' is not part of {}'.format(value, cls.mirrorTable.keys()))
        return value


class RComponent(Mirrorable):

    name = RName('untitled')
    side = RSide('L')
    index = RIndex(0)

    @classmethod
    def getParameters(cls):
        parameters = dict()
        for key, value in cls.__dict__.items():
            if isinstance(value, RParameter):
                parameters[key] = value
        return parameters

    def __init__(self, **kwargs):
        self.parameters = self.getParameters()

        # set parameters value
        for key, value in kwargs.items():
            if key not in self.parameters.keys():
                raise ValueError('Unexpected keyword argument -> {}'.format(key))

            parameter = self.parameters[key]
            parameter.setValue(value)

        # Check if all mandatory parameters are set
        for key, parameter in self.parameters.items():
            if parameter.value is None:
                raise ValueError('\'{}\' has not been set'.format(key))

    def __str__(self):
        return str(self.parameters)

    def __repr__(self):
        return str(self.parameters)

    def __iter__(self):
        return iter(self.parameters)

    def __getitem__(self, item):
        return self.parameters[item]

    def items(self):
        return self.parameters.items()

    def values(self):
        return self.parameters.values()

    def keys(self):
        return self.parameters.keys()

    def __mirror__(self):
        mirroredKwargs = dict()

        for key, parameter in self.items():
            mirroredValue = mirror(parameter)
            mirroredKwargs[key] = parameter.value if mirroredValue is None else mirroredValue

        return self.__class__(**mirroredKwargs)

    def create(self):
        pass


def test():
    component = RComponent(side=RSide('L'))
    print 'component', component
    mirroredComponent = mirror(component)
    print 'component', component
    print 'mirroredComponent', mirroredComponent
    # print mirroredComponent


