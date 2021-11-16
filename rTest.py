import re
from maya import cmds


def mirror(obj):
    if hasattr(obj, '__mirror__'):
        return obj.__mirror__()
    raise AttributeError('No __mirror__ method found for this type -> {}'.format((type(obj))))


class RParameterValueError(ValueError):
    pass


class Mirrorable(object):

    def __mirror__(self):
        return None


class RParameter(Mirrorable):

    _value = None

    def __init__(self, value=None):
        if value is not None:
            self.setValue(value)

    def __str__(self):
        return str(self.getValue())

    def __repr__(self):
        return str(self.getValue())

    def setValue(self, value):
        self._checkValue(value)
        self._value = value

    def getValue(self):
        return self._value

    @classmethod
    def _checkValue(cls, value):
        raise NotImplementedError

    def copy(self):
        return self.__class__(self.getValue())


class RIndex(RParameter):

    @classmethod
    def _checkValue(cls, value):
        if not isinstance(value, (int, long)):
            raise RParameterValueError('The given value should be of type int or long -> {}'.format(type(value)))
        if value < 0:
            raise RParameterValueError('The given value should be positive -> {}'.format(value))


class RName(RParameter):

    pattern = r'^[a-zA-Z_][A-Z0-9a-z_]*$'

    @classmethod
    def _checkValue(cls, value):
        if not isinstance(value, basestring):
            raise RParameterValueError('The given value is not of type basestring -> {}'.format(type(value)))
        if not re.match(cls.pattern, value):
            raise RParameterValueError('The given value doesnt fit the patter \'{}\' -> {}'.format(cls.pattern, value))
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
        return self.__class__(self.mirrorTable[self.getValue()])

    @classmethod
    def _checkValue(cls, value):
        if not isinstance(value, basestring):
            raise RParameterValueError('The given value is not of type basestring -> {}'.format(type(value)))
        if value not in cls.mirrorTable.keys():
            raise RParameterValueError('The given value is not part of {} -> {}'.format(cls.mirrorTable.keys(), value))
        return value


class RComponent(Mirrorable):

    @classmethod
    def getParameters(cls):
        parameters = dict()
        for key, parameter in cls.__dict__.items():
            if isinstance(parameter, RParameter):
                parameters[key] = parameter.copy()
        return parameters

    def checkKwargs(self, **kwargs):
        # set parameters value
        for key, value in kwargs.items():
            if key not in self.parameters.keys():
                raise KeyError('Unexpected keyword argument -> {}'.format(key))

            parameter = self.parameters[key]
            parameter.setValue(value)

            self.__setattr__(key, parameter)

        # Check if all mandatory parameters are set
        for key, parameter in self.parameters.items():
            if parameter.getValue() is None:
                raise KeyError('\'{}\' keyword argument is mandatory'.format(key))

    def __init__(self, **kwargs):
        self.parameters = self.getParameters()
        # self._controllers = list()
        # self._inputs = list()
        # self._outputs = list()
        self._folder = None

        self.checkKwargs(**kwargs)

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
            mirroredParameter = mirror(parameter)

            if mirroredParameter is None:
                mirroredKwargs[key] = parameter.getValue()
            else:
                mirroredKwargs[key] = mirroredParameter.getValue()

        return self.__class__(**mirroredKwargs)

    def getFolder(self):
        return self._folder

    def setFolder(self, folder):
        self._folder = folder

    def create(self):
        if self.getFolder() is not None:
            raise RuntimeError('Component already created -> {}'.format(self))
        self._initializeCreation()
        self._doCreation()
        self._finalizeCreation()

    def _initializeCreation(self):
        pass

    def _doCreation(self):
        raise NotImplementedError

    def _finalizeCreation(self):
        pass


class RFolder(object):

    def __init__(self, name):
        self.name = name

    @classmethod
    def create(cls, name):
        name = cmds.group(empty=True, name=folderName)
        return cls(name)


class RMyComponent(RComponent):
    name = RName('untitled')
    side = RSide('L')
    index = RIndex(0)

    RFolderClass = RFolder

    def _initializeCreation(self):
        folderName = '{}_{}_{}_cmpnt'.format(self.name, self.side, self.index)
        if cmds.objExists(folderName):
            raise RuntimeError('A folder named like this already exists -> {}'.format(folderName))
        folder = self.RFolderClass.create(folderName)
        self.setFolder(folder)

    def _doCreation(self):
        print self.name

    def _finalizeCreation(self):
        print self._folder


def test():
    component = RMyComponent(side='L')
    mirroredComponent = mirror(component)
    # print 'component', component
    # print 'mirroredComponent', mirroredComponent
    component.create()
    mirroredComponent.create()
