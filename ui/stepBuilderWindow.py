from functools import partial

from PySide2 import QtWidgets
from maya import cmds, mel
from rigBuilder.files.skinFile import SkinFile
from .attributeWidgets import ScriptWidget, FileWidget, NodeWidget, ComponentBuilderWidget, SkinFileWidget, \
    PythonFileWidget, ListAttributeWidget, GuidesFileWidget
from ..components.baseLegacy import Nodes
from ..files.core import JsonFile
from ..files.guidesFile import GuidesFile
from ..steps.buildComponents import BuildComponents, ComponentBuilderFile
from ..steps.core import StepBuilder
from ..steps.customScript import CustomScript, Script
from ..steps.customScriptFile import PythonFile, CustomScriptFile
from ..steps.importCorrectives import ImportCorrectives
from ..steps.importGuidesFile import ImportGuidesFile
from ..steps.importMayaFile import ImportMayaFile, MayaFile
from ..steps.importSkin import ImportSkin
from ..steps.newScene import NewScene
from ..steps.transferSkin import TransferSkin
from ..types import Node
from ..ui.dataDictEditor import DataDictEditor, DataAttributeEditor, DataDictList

from ..ui.jsonFileWindow import JsonFileWindow, AskToSave


class StepDictList(DataDictList):
    types = [
        CustomScript,
        CustomScriptFile,
        NewScene,
        ImportMayaFile,
        BuildComponents,
        ImportSkin,
        TransferSkin,
        ImportGuidesFile,
        ImportCorrectives,
    ]


class StepAttributeEditor(DataAttributeEditor):

    def __init__(self):
        super(StepAttributeEditor, self).__init__()

        self.typeWidgetMap = [
            (Script, ScriptWidget),
            (Node, NodeWidget),
            (SkinFile, SkinFileWidget),
            (PythonFile, PythonFileWidget),
            (ComponentBuilderFile, ComponentBuilderWidget),
            (GuidesFile, GuidesFileWidget),
            (JsonFile, FileWidget),
            (MayaFile, FileWidget),
            (Nodes, partial(ListAttributeWidget, NodeWidget))
        ] + self.typeWidgetMap


class StepBuilderWindow(JsonFileWindow):

    def __init__(self):
        super(StepBuilderWindow, self).__init__(title='Step Builder')

        self.stepEditor = DataDictEditor(
            dataDictList=StepDictList(),
            dataAttributeEditor=StepAttributeEditor()
        )

        buildBtn = QtWidgets.QPushButton('Build')
        buildBtn.clicked.connect(self.build)

        layout = QtWidgets.QVBoxLayout()
        layout.setMargin(0)
        layout.addWidget(self.stepEditor)
        layout.addWidget(buildBtn)
        layout.setStretch(1, 1)

        self.mainLayout.addLayout(layout)

    def getData(self):  # type: () -> StepBuilder
        return StepBuilder(self.stepEditor.getDataDict())

    def build(self):
        build = True
        if cmds.file(q=True, modified=True):
            result = AskToSave(parent=self, title='Warning: Scene not saved', text='Save scene before continuing?').exec_()
            if result == AskToSave.cancel:
                build = False
            elif result == AskToSave.save:
                mel.eval('SaveSceneAs')
                if cmds.file(q=True, modified=True):
                    build = False

        if not build:
            print('Build Canceled')
            return

        stepBuilder = self.getData()
        stepBuilder.build()

    def refresh(self, data=None):  # type: (StepBuilder) -> None
        data = StepBuilder() if data is None else data
        self.stepEditor.refresh(data.stepDict)


