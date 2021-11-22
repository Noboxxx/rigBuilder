from . import RCore, RObj


class BaseComponent(RCore.RBaseComponent):

    namePattern = '{name}_{side}_{index}'

    def __init__(self, **kwargs):
        super(BaseComponent, self).__init__(**kwargs)

        self.folder = None
        self.rootDags = list()

    @property
    def fullName(self):
        return self.namePattern.format(
            name=self.name,
            side=self.side,
            index=self.index,
        )

    def _initializeCreation(self):
        self.folder = RObj.Transform.create()

    def _finalizeCreation(self):
        self.folder.parent(*self.rootDags)


class OneCtrl(BaseComponent):
    def _doCreation(self):
        ctrlBuffer = RObj.Transform.create()
        ctrl = RObj.Controller.create()
        ctrlBuffer.parent(ctrl)

        self.rootDags.append(ctrlBuffer)
