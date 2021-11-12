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

    Those methods are made to be overwritten but not called from outside:
        - _initializeCreation()
        - _doCreation()
        - _finalizeCreation()

    getMirroredDict:
        This method should be reimplemented to always mirror all arguments (if it makes sense)
        passed to the __init__ method.
    """

    def __init__(self, name, side, index):
        self._name = None
        self._side = None
        self._index = None

        self.setName(name)
        self.setSide(side)
        self.setIndex(index)

        self._controllers = list()
        self._outputs = list()
        self._inputs = list()

    def __eq__(self, other):
        """
        Equality is based on types, names, sides and indices of two components.
        :param other: any
        :return: bool
        """
        if self.__class__ != other.__class__:
            return False

        if self.getName() != other.getName():
            return False

        if self.getSide() != other.getSide():
            return False

        if self.getIndex() != other.getIndex():
            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        """
        Return the formatted name of the component like so: <name>_<side>_<index>
        :return: str
        """
        return '{}_{}_{}'.format(self.getName(), self.getSide(), self.getIndex())

    def __dict__(self):
        """
        returns all arguments passed to the __init__ method.
        :return: dict
        """
        return dict(
            name=self.getName(),
            side=self.getSide(),
            index=self.getIndex(),
        )

    # Getters, Setters , Adders

    def getName(self):
        return self._name

    def setName(self, value):
        if not isinstance(value, basestring):
            raise ValueError('value should be \'basestring\' type not \'{}\''.format(type(value)))
        self._name = str(value)

    def getIndex(self):
        return self._index

    def setIndex(self, value):
        if not isinstance(value, int or long):
            raise ValueError('value should be \'int\' or \'long\' type not \'{}\''.format(type(value)))
        self._index = int(value)

    def getSide(self):
        return self._side

    def setSide(self, value):
        if not isinstance(value, basestring):
            raise ValueError('value should be \'basestring\' type not \'{}\''.format(type(value)))
        self._side = str(value)

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

    # Naming

    def composeObjectName(self, name):
        """
        compose an object name based on the component's name
        :param name: str
        :return: str
        """
        raise NotImplementedError
