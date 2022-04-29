from rigBuilder.core import Data
import time

from rigBuilder.types import Path


class Step(Data):

    def build(self, workspace=''):
        pass


class StepBuilder(Data):

    def __init__(self, stepDict=None, disabledSteps=None, workspace=''):
        # type: (dict[str: Step], List[str], str) -> None
        super(StepBuilder, self).__init__()

        self.workspace = Path(workspace)
        self.disabledSteps = disabledSteps if disabledSteps is not None else list()
        self.stepDict = stepDict if stepDict is not None else dict()

    def build(self):
        start = time.time()
        print('---> Build starts')
        for name, step in self.stepDict.items():
            if name in self.disabledSteps:
                continue
            step.build(workspace=self.workspace)
        print('---> Build stops [{} sec]'.format(time.time() - start))
