class Input(object):

    def __init__(self, obj):
        self.obj = obj
        self.destinations = list()

    def connect(self, out):
        raise NotImplementedError


class Output(object):

    def __init__(self, obj):
        self.obj = obj
        self.source = None

    def connect(self, inp):
        raise NotImplementedError


class Controller(object):

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError


class Component(object):
    """
    This class is made to harmonize component's creation and facilitate:
        - mirroring
        - connect components together (inputs, outputs)
        - access to controllers

    The creation methods are made to be overwritten but not called from outside:
        - _initializeCreation()
        - _doCreation()
        - _finalizeCreation()

    This class can be iterated over to have access to its parameters (name, side, index,...).

    asdict() -> dict:
        This method should be return every arguments that have been passed to the __init__ mathod.

    asmirroreddict() -> dict:
        This method should mirror values that make sense to be mirrored from asdict().

    __init__:
        if a given argument's value is not valid, a ValueError should be raised.
    """

    def __init__(self, name, side, index):
        if not isinstance(name, basestring):
            raise ValueError('name should be \'basestring\' type not \'{}\''.format(type(name)))

        if not isinstance(index, int or long):
            raise ValueError('index should be \'int\' or \'long\' type not \'{}\''.format(type(index)))

        if not isinstance(side, basestring):
            raise ValueError('side should be \'basestring\' type not \'{}\''.format(type(side)))

        self._name = name
        self._side = side
        self._index = index

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
        returns all parameters that define the component.
        :return: dict
        """
        return dict(
            name=self.getName(),
            side=self.getSide(),
            index=self.getIndex(),
        )

    def keys(self):
        return self.asdict().keys()

    def values(self):
        return self.asdict().values()

    def items(self):
        return self.asdict().items()

    # Getters, Setters , Adders

    def getName(self):
        return self._name

    def getIndex(self):
        return self._index

    def getSide(self):
        return self._side

    def getControllers(self):
        return self._controllers

    def addController(self, value):
        if not isinstance(value, Controller):
            raise ValueError('value should be \'Controller\' type not \'{}\''.format(type(value)))
        self._controllers = value

    def getOutputs(self):
        return self._outputs

    def addOutput(self, value):
        if not isinstance(value, Output):
            raise ValueError('value should be \'Output\' type not \'{}\''.format(type(value)))
        self._outputs = value

    def getInputs(self):
        return self._inputs

    def addInput(self, value):
        if not isinstance(value, Input):
            raise ValueError('value should be \'Input\' type not \'{}\''.format(type(value)))
        self._inputs = value

    # Mirror

    def getMirror(self):
        """
        returns a mirrored copy of itself or None if arguments are invalid.
        :return: BaseRigComponent or None
        """
        mirroredKwargs = self.getMirroredDict()
        try:
            return self.__class__(**mirroredKwargs)
        except ValueError:
            return None

    def getMirroredDict(self):
        """
        returns all arguments passed to the __init__ method but mirrored.
        :return: dict
        """
        raise NotImplementedError

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
