from rigBuilder.steps.core import Step


class Script(str):

    def execute(self):
        exec self


class CustomScript(Step):

    def __init__(self, script=str(), **kwargs):
        super(CustomScript, self).__init__(**kwargs)
        self.script = Script(script)

    def build(self):
        self.script.execute()
