def mirror(value):
    if hasattr(value, '__mirror__'):
        return value.__mirror__()
    return None


class ImmutableError(BaseException):

    def __init__(self):
        super(ImmutableError, self).__init__('Impossible due to immutability.')


class ImmutableData(object):
    """
    ImmutableData acts like a dict but is immutable. You can call a key like a field.

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
        self.attributes = list()
        for key, value in kwargs.items():
            self.__setattr__(key, value)
            self.attributes.append(key)

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
        for attr in self.attributes:
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


def test():
    data = ImmutableData(name='untitled', side='L', index=0)
    dataCopy = data.copy()
    print data == dataCopy
    print dict(data)
    for key, value in data.items():
        print key, value
