def mirror(value):
    if hasattr(value, '__mirror__'):
        return value.__mirror__()
    return None


class Signal(object):

    def __init__(self):
        self.funcs = list()

    def emit(self, *args, **kwargs):
        for func in self.funcs:
            func(*args, **kwargs)

    def connect(self, func):
        self.funcs.append(func)

    def disconnect(self):
        self.funcs = list()


class RParameterHint(object):

    def __init__(self, types=None, defaultValue=None):
        self.types = types

        self.checkValue(defaultValue)
        self.defaultValue = defaultValue

    def checkValue(self, value):
        if self.types is None:
            return

        if not isinstance(value, self.types):
            raise TypeError(
                'Unexpected value type. Should have been {} not \'{}\''.format(self.types, type(value).__name__)
            )


class RDataStructure(object):

    @classmethod
    def _getParameterHints(cls):
        typeHints = dict()
        for key in dir(cls):
            value = getattr(cls, key)
            if isinstance(value, RParameterHint):
                typeHints[key] = value
        return typeHints

    @classmethod
    def _getConformedKwargs(cls, **kwargs):
        typeHints = cls._getParameterHints()
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

        self._fields = list()
        for key, value in kwargs.items():
            self.__setattr__(key, value)
            self._fields.append(key)

    def __iter__(self):
        return iter(self._asdict())

    def __eq__(self, other):
        if not isinstance(other, RDataStructure):
            return False

        otherKeys = other.keys()

        for key, value in self.items():
            if key not in otherKeys:
                return False

            if self.__getattribute__(key) != other.__getattribute__(key):
                return False
        return True

    def __mirror__(self):
        mirroredDict = dict()
        for key, value in self.items():
            mirroredValue = mirror(value)
            mirroredDict[key] = value if mirroredValue is None else mirroredValue

        return self.__class__(**mirroredDict)

    def _asdict(self):
        data = dict()
        for field in self._fields:
            value = self.__getattribute__(field)
            data[field] = value
        return data

    def items(self):
        return self._asdict().items()

    def keys(self):
        return self._asdict().keys()

    def values(self):
        return self._asdict().values()

    def copy(self):
        return self.__class__(**self._asdict())


class RBaseComponent(RDataStructure):

    def __init__(self, **kwargs):
        super(RBaseComponent, self).__init__(**kwargs)

        self.inputs = list()
        self.outputs = list()
        self.controllers = list()

    def create(self):
        self._initializeCreation()
        self._doCreation()
        self._finalizeCreation()

    def _initializeCreation(self):
        pass

    def _doCreation(self):
        pass

    def _finalizeCreation(self):
        pass


class RBaseObject(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return repr(self.name)

    @classmethod
    def create(cls, name=''):
        raise NotImplementedError


class RBaseRig(object):
    pass