from rigBuilder.core import Data
import time


class Step(Data):

    def build(self):
        pass


class StepBuilder(Data):

    def __init__(self, stepDict=None, disabledSteps=None):
        # type: (dict[str: Step], List[str]) -> None
        super(StepBuilder, self).__init__()

        self.disabledSteps = disabledSteps if disabledSteps is not None else list()
        self.stepDict = stepDict if stepDict is not None else dict()

    def build(self):
        start = time.time()
        print('---> Build starts')
        for name, step in self.stepDict.items():
            if name in self.disabledSteps:
                continue
            step.build()
        print('---> Build stops [{} sec]'.format(time.time() - start))
