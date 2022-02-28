from functools import partial

from PySide2 import QtWidgets
from .attributeWidgets import ScriptWidget, FileWidget, NodeWidget, ComponentBuilderWidget
from ..files.core import JsonFile
from ..steps.buildComponents import BuildComponents, ComponentBuilderFile
from ..steps.core import StepBuilder
from ..steps.customScript import CustomScript, Script
from ..steps.importMayaFile import ImportMayaFile, MayaFile
from ..steps.importSkinLayers import ImportSkinLayers, Mesh
from ..steps.newScene import NewScene
from ..ui.dataDictEditor import DataDictEditor, DataAttributeEditor, DataDictList

from ..ui.jsonFileWindow import JsonFileWindow


class StepDictList(DataDictList):
    types = (
        CustomScript,
        NewScene,
        ImportMayaFile,
        ImportSkinLayers,
        BuildComponents,
    )


class StepAttributeEditor(DataAttributeEditor):

    def getAttributeWidget(self, key, value):

        t = type(value)

        if isinstance(value, Script):
            widget = ScriptWidget()
            widget.setText(value)
            widget.textChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return widget

        elif isinstance(value, Mesh):
            widget = NodeWidget()
            widget.setNode(value)
            widget.nodeChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return widget

        elif isinstance(value, ComponentBuilderFile):
            widget = ComponentBuilderWidget('Json File (*.json)')
            widget.setPath(value)
            widget.pathChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return widget

        elif isinstance(value, JsonFile):
            widget = FileWidget('Json File (*.json)')
            widget.setPath(value)
            widget.pathChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return widget

        elif isinstance(value, MayaFile):
            widget = FileWidget('Maya File (*.ma *.mb)')
            widget.setPath(value)
            widget.pathChanged.connect(partial(self.attributeValueChanged.emit, key, t))
            return widget

        return super(StepAttributeEditor, self).getAttributeWidget(key, value)


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
        stepBuilder = self.getData()
        stepBuilder.build()

    def refresh(self, data=None):  # type: (StepBuilder) -> None
        data = StepBuilder() if data is None else data
        self.stepEditor.refresh(data.stepDict)


