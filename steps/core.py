from rigBuilder.core import Data


class Step(Data):
    pass


class StepBuilder(Data):

    def __init__(self, stepDict=None):
        # type: (dict[str: Step]) -> None
        super(StepBuilder, self).__init__()

        self.stepDict = stepDict if stepDict is not None else dict()

    def build(self):
        for step in self.stepDict.values():
            step.build()
