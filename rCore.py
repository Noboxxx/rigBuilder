class RInput(object):

    def __init__(self, obj):
        self.obj = obj
        self.destinations = list()

    def connect(self, out):
        raise NotImplementedError


class ROutput(object):

    def __init__(self, obj):
        self.obj = obj
        self.source = None

    def connect(self, inp):
        raise NotImplementedError


class RController(object):

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError


class RComponent(object):
    """
    This class is made to harmonize component's creation and facilitate:
        - mirroring
        - connect components together (inputs, outputs)
        - access to controllers

    The creation methods are made to be overwritten but not called from outside:
        - _initializeCreation()
        - _doCreation()
        - _finalizeCreation()

    This class can be iterated over to have access to its parameters.

    parameters = {str: (func or None, func or None)}:
        parameters contains keys that will be allowed to be passed to the __init__ method as kwargs.
        Each key contains a tuple containing:
            - a defaultValue in case the kwarg is not set. If the defaultValue is None then the kwarg is mandatory.
            - a checkValue function or None if no need to check the value.
            - a mirrorValue function or None if the value does not need to be checked.

        checkValue(value) will be called in the __init__ method to unsure that the given value is valid. If it's not,
        the function should raise a ValueError.

        mirrorValue(value) will be called in asmirroreddict() to mirror the given value and return it.

        Example:
            >>> def mirrorValueExample(value):
            >>>     # do something to the value to mirror it
            >>>     return value
            >>>
            >>> def checkValueExample(value):
            >>>     if not value:  # check something to check if the value is valid
            >>>         raise ValueError
            >>>
            >>> defaultValue = 0.0
            >>>
            >>> parameters = {'kwarg': (defaultValue, checkValueExample, mirrorValueExample)}
    """

    parameters = dict()

    def __init__(self, **kwargs):

        self._parameters = list()

        for key, value in kwargs.items():

            if key not in self.parameters:
                raise KeyError('\'{}\' is not a valid key'.format(key))

            _, validator, _ = self.parameters[key]
            if validator is not None:
                validator(value)

            self.__setattr__(key, value)
            self._parameters.append(key)

        for key, (defaultValue, _, _) in self.parameters.items():
            if key in self._parameters:
                continue

            if defaultValue is None:
                raise ValueError('The key \'{}\' is mandatory'.format(key))
            else:
                self.__setattr__(key, defaultValue)
                self._parameters.append(key)

        self._controllers = list()
        self._outputs = list()
        self._inputs = list()

    def __eq__(self, other):
        """
        Equality is based on objects' types and parameters.
        :param other: any
        :return: bool
        """
        if self.__class__ != other.__class__:
            return False

        if self.asdict() != other.asdict():
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    # dict like

    def __iter__(self):
        """
        Iter over component's parameters.
        :return:
        """
        return iter(self.asdict().items())

    def __getitem__(self, item):
        return self.asdict()[item]

    def asdict(self):
        """
        returns all parameters.
        :return: dict
        """
        data = dict()
        for key in self._parameters:
            value = self.__getattribute__(key)
            data[key] = value
        return data

    def keys(self):
        return self.asdict().keys()

    def values(self):
        return self.asdict().values()

    def items(self):
        return self.asdict().items()

    def getControllers(self):
        return self._controllers

    def addController(self, value):
        if not isinstance(value, RController):
            raise ValueError('value should be \'Controller\' type not \'{}\''.format(type(value)))
        self._controllers = value

    def getOutputs(self):
        return self._outputs

    def addOutput(self, value):
        if not isinstance(value, ROutput):
            raise ValueError('value should be \'Output\' type not \'{}\''.format(type(value)))
        self._outputs = value

    def getInputs(self):
        return self._inputs

    def addInput(self, value):
        if not isinstance(value, RInput):
            raise ValueError('value should be \'Input\' type not \'{}\''.format(type(value)))
        self._inputs = value

    # Mirror

    def getMirror(self):
        """
        returns a mirrored copy of itself or None if arguments are invalid.
        :return: BaseRigComponent or None
        """
        mirroredKwargs = self.asmirroreddict()
        try:
            return self.__class__(**mirroredKwargs)
        except ValueError:
            return None

    def asmirroreddict(self):
        """
        returns all parameters mirrored.
        :return: dict
        """
        mirroredData = dict()
        for key, value in self.asdict().items():
            _, _, mirrorFunc = self.parameters[key]
            if mirrorFunc is not None:
                mirroredData[key] = mirrorFunc(value)
            else:
                mirroredData[key] = value
        return mirroredData

    # Creation

    def create(self):
        """
        creates the component.
        First it calls '_initializeCreation' then '_doCreation' and finally '_finalizeCreation'.
        :return:
        """
        self._initializeCreation()
        self._doCreation()
        self._finalizeCreation()

    def _initializeCreation(self):
        """
        is called before '_doCreation' when calling 'create'.
        This method is meant to initialize somethings before creating the component's content.
        :return:
        """
        pass

    def _doCreation(self):
        """
        is called between '_initializeCreation' and '_finalizeCreation' when calling 'create'.
        This method is meant to create the content of the component.
        :return:
        """
        raise NotImplementedError

    def _finalizeCreation(self):
        """
        is called after '_doCreation' when calling 'create'.
        This method is meant to finalize component's creation.
        :return:
        """
        pass
