import os
from functools import partial

from PySide2 import QtWidgets, QtGui, QtCore
from .attributeWidgets import ScriptWidget, FileWidget, NodeWidget, ComponentBuilderWidget
from .utils import Signal, size
from ..files.core import JsonFile
from ..steps.buildComponents import BuildComponents
from ..steps.core import StepBuilder
from ..steps.customScript import CustomScript, Script
from ..steps.importMayaFile import ImportMayaFile, MayaFile
from ..steps.importSkinLayers import ImportSkinLayers, Mesh
from ..steps.newScene import NewScene
from ..ui.dataDictEditor import DataDictEditor, DataAttributeEditor, DataDictList

from ..ui.jsonFileWindow import JsonFileWindow


class WorkspaceWidget(QtWidgets.QWidget):

    def __init__(self):
        super(WorkspaceWidget, self).__init__()

        self.pathEdit = QtWidgets.QLineEdit(os.getcwd())
        self.pathEdit.setEnabled(False)

        openBtn = QtWidgets.QPushButton()
        openBtn.setIcon(QtGui.QIcon(':openLoadGeneric.png'))
        openBtn.clicked.connect(self.askOpen)
        openBtn.setFixedSize(size(20), size(20))

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.addWidget(QtWidgets.QLabel('workspace'))
        self.mainLayout.addWidget(self.pathEdit)
        self.mainLayout.addWidget(openBtn)

        self.setLayout(self.mainLayout)

    def askOpen(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, caption='Open Workspace')
        if not path:
            return
        if os.path.isdir(path):
            os.chdir(path)
        self.pathEdit.setText(os.path.normpath(path))


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

        elif isinstance(value, JsonFile):
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

        self.workspaceWidget = WorkspaceWidget()

        self.stepEditor = DataDictEditor(
            dataDictList=StepDictList(),
            dataAttributeEditor=StepAttributeEditor()
        )

        buildBtn = QtWidgets.QPushButton('Build')
        buildBtn.clicked.connect(self.build)

        layout = QtWidgets.QVBoxLayout()
        layout.setMargin(0)
        layout.addWidget(self.workspaceWidget)
        layout.addWidget(self.stepEditor)
        layout.addWidget(buildBtn)
        layout.setStretch(1, 1)

        self.mainLayout.addLayout(layout)

    def getData(self):  # type: () -> StepBuilder
        return StepBuilder(self.stepEditor.getDataDict())

    def build(self):
        self.getData().build()

    def refresh(self, data=None):  # type: (StepBuilder) -> None
        if not isinstance(data, StepBuilder):
            raise TypeError
        self.stepEditor.refresh(data.stepDict)


