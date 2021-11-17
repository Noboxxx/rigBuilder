def mirror(value):
    if hasattr(value, '__mirror__'):
        return value.__mirror__()
    return None


class ImmutableError(BaseException):

    def __init__(self):
        super(ImmutableError, self).__init__('Impossible due to immutability.')


class ImmutableData(object):
    """
    ImmutableData acts like a dict but is immutable.
    You can call a key like a field.

    Example:
        >>> data = ImmutableData(firstName='firstName', lastName='lastName')
        >>> print data.firstName  # print firstName in a field manner
        >>> print data['firstName'] # print firstName in a dict manner

    Flaws:
        - auto-completion on dynamic fields doesnt work.
    """

    @staticmethod
    def raiseImmutableError(*_):
        raise ImmutableError

    def __init__(self, **kwargs):

        # create fields
        self.dataFields = list()
        for key, value in kwargs.items():
            self.__setattr__(key, value)
            self.dataFields.append(key)

        # Make class immutable
        self.__delattr__ = self.raiseImmutableError
        self.__setattr__ = self.raiseImmutableError

    def __iter__(self):
        return iter(self._asdict())

    def __eq__(self, other):
        if not isinstance(other, ImmutableData):
            return False

        otherKeys = other.keys()

        for key, value in self.items():
            if key not in otherKeys:
                return False

            if self.__getattribute__(key) != other.__getattribute__(key):
                return False
        return True

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def _asdict(self):
        data = dict()
        for attr in self.dataFields:
            value = self.__getattribute__(attr)
            data[attr] = value
        return data

    def items(self):
        return self._asdict().items()

    def keys(self):
        return self._asdict().keys()

    def values(self):
        return self._asdict().values()

    def copy(self):
        return self.__class__(**self._asdict())


class ParameterHint(object):

    def __init__(self, types=None, defaultValue=None):
        self.types = types

        self.checkValue(defaultValue)
        self.defaultValue = defaultValue

    def checkValue(self, value):
        if self.types is None:
            return

        if not isinstance(value, self.types):
            typesStr = ' or '.join(['\'{}\''.format(type_.__name__) for type_ in self.types])
            raise TypeError('Unexpected value type. Should have been {} not \'{}\''.format(typesStr, type(value).__name__))


class BaseComponent(ImmutableData):

    @classmethod
    def _getTypeHints(cls):
        typeHints = dict()
        for key in dir(cls):
            value = getattr(cls, key)
            if isinstance(value, ParameterHint):
                typeHints[key] = value
        return typeHints

    @classmethod
    def _getConformedKwargs(cls, **kwargs):
        typeHints = cls._getTypeHints()
        newKwargs = dict()

        for key, typeHint in typeHints.items():
            if key not in kwargs.keys():
                if typeHint.defaultValue is None:
                    raise KeyError('Mandatory key missing -> {}'.format(key))
                else:
                    newKwargs[key] = typeHint.defaultValue
            else:
                value = kwargs[key]
                typeHint.checkValue(value)
                newKwargs[key] = value
        return newKwargs

    def __init__(self, **kwargs):
        kwargs = self._getConformedKwargs(**kwargs)
        super(BaseComponent, self).__init__(**kwargs)

    def __mirror__(self):
        mirroredDict = dict()
        for key, value in self.items():
            mirroredValue = mirror(value)
            mirroredDict[key] = value if mirroredValue is None else mirroredValue

        return self.__class__(**mirroredDict)

    def create(self):
        raise NotImplementedError


class TestComponent(BaseComponent):
    name = ParameterHint(basestring, defaultValue='untitled')
    side = ParameterHint(basestring, defaultValue='C')
    index = ParameterHint((long, int), defaultValue=0)


class SimpleComponent(TestComponent):
    matrix = ParameterHint(int, defaultValue=0)


def test():
    data = SimpleComponent()
    print '--- dict like ---'
    for key, value in data.items():
        print key, value
    print '--- fields ---'
    print data.name
    print data.side
