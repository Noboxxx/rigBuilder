from rigBuilder.core import Data
import time


class Step(Data):

    def build(self):
        pass


class StepBuilder(Data):

    def __init__(self, stepDict=None):
        # type: (dict[str: Step]) -> None
        super(StepBuilder, self).__init__()

        self.stepDict = stepDict if stepDict is not None else dict()

    def build(self):
        start = time.time()
        print('---> Build starts')
        for step in self.stepDict.values():
            step.build()
        print('---> Build stops [{} sec]'.format(time.time() - start))
