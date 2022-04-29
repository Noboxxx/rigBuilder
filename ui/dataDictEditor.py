from collections import OrderedDict
from functools import partial

from imath import clamp

from PySide2 import QtWidgets
from .utils import size, Signal
from ..core import Data
import re
from .attributeWidgets import BoolWidget, StringWidget, DefaultWidget, FloatWidget, IntWidget


class RenamerDialog(QtWidgets.QDialog):

    def __init__(self, name=''):
        super(RenamerDialog, self).__init__()

        self.setWindowTitle('Rename')

        self.validated = False

        self.line = QtWidgets.QLineEdit()
        self.line.setText(name)
        self.line.selectAll()
        self.line.returnPressed.connect(self.validate)

        applyBtn = QtWidgets.QPushButton('Apply')
        applyBtn.clicked.connect(self.validate)

        mainLayout = QtWidgets.QHBoxLayout(self)
        mainLayout.addWidget(QtWidgets.QLabel('New Name'))
        mainLayout.addWidget(self.line)
        mainLayout.addWidget(applyBtn)

    def exec_(self):
        super(RenamerDialog, self).exec_()
        return self.line.text() if self.validated else ''

    def validate(self):
        self.validated = True
        self.close()


class DataAttributeEditor(QtWidgets.QTreeWidget):

    def __init__(self):
        super(DataAttributeEditor, self).__init__()

        self.typeWidgetMap = [
            (bool, BoolWidget),
            (basestring, StringWidget),
            (float, FloatWidget),
            (int, IntWidget),
        ]

        self.setHeaderLabels(('name', 'value', 'type'))
        self.setColumnWidth(1, size(200))

        self.attributeValueChanged = Signal()

    def refresh(self, data=None):  # type: (Data) -> None
        self.clear()

        data = Data() if data is None else data

        for k, v in data.items():
            self.addAttribute(k, v)

    def addAttribute(self, key, value, parent=None, shortAttr=None):
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, str(shortAttr) if shortAttr is not None else str(key))
        item.setText(2, value.__class__.__name__)

        if parent is None:
            self.addTopLevelItem(item)
        else:
            parent.addChild(item)

        widget = self.getAttributeWidget(key, value)

        layout = QtWidgets.QVBoxLayout()
        layout.setMargin(size(6))
        layout.addWidget(widget)

        itemWidget = QtWidgets.QWidget(self)
        itemWidget.setLayout(layout)

        self.setItemWidget(item, 1, itemWidget)

        item.setExpanded(True)

    def getAttributeWidget(self, key, value):
        for t, w in self.typeWidgetMap:
            if isinstance(value, t):
                widget = w()
                widget.setValue(value)
                widget.valueChanged.connect(partial(self.attributeValueChanged.emit, key, type(value)))
                return widget

        widget = DefaultWidget()
        widget.setValue(value)
        return widget


class DataDictList(QtWidgets.QTreeWidget):

    types = list()

    def __init__(self):
        super(DataDictList, self).__init__()
        self.setHeaderLabels(('key', 'type', ''))
        # self.setColumnWidth(1, size(50))
        self.setColumnWidth(2, size(25))

        self.currentDataChanged = Signal()
        self.currentItemChanged.connect(self.emitCurrentDataChanged)
        self.setSelectionMode(self.ExtendedSelection)
        self.itemDoubleClicked.connect(self.renameSelectedItem)

    def setAttributeValue(self, key, t, value):
        # print key, t, value
        item = self.currentItem()

        if isinstance(value, dict):
            value = t(**value)
        else:
            value = t(value)

        try:
            cmd = 'item.d.{} = value'.format(key)
            exec cmd
        except:
            print('Pas content')

    def emitCurrentDataChanged(self, item):
        self.currentDataChanged.emit(item.d if item is not None else None)

    def refresh(self, dataDict, disabledKeys=None):  # type: (dict[str: Data], List[str]) -> None
        print 'refresh', dataDict, disabledKeys
        self.clear()

        if dataDict is None:
            return

        disabledKeys = disabledKeys if disabledKeys is not None else list()

        for key, data in dataDict.items():
            self.addItem(key, data, enabled=key not in disabledKeys)

    def getDataDict(self):  # type: () -> OrderedDict[str: Data]
        iterator = QtWidgets.QTreeWidgetItemIterator(self)

        dataDict = OrderedDict()
        while True:
            item = iterator.value()
            if item is None:
                break
            dataDict[item.text(0)] = item.d
            iterator.next()

        return dataDict

    def getDisabledKeys(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self)

        disabledKeys = list()
        while True:
            item = iterator.value()
            if item is None:
                break
            checkbox = self.itemWidget(item, 2)  # type: QtWidgets.QCheckBox
            if not checkbox.isChecked():
                disabledKeys.append(item.text(0))
            iterator.next()

        return disabledKeys

    def removeSelectedItems(self):
        result = QtWidgets.QMessageBox.question(
            self,
            "Undoable operation",
            "Continue anyways?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result == QtWidgets.QMessageBox.No:
            return

        for item in self.selectedItems():
            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)

    def moveSelectedSelectedItem(self, step):
        selectedItem = self.selectedItems()[0]

        index = self.indexOfTopLevelItem(selectedItem)
        item = self.takeTopLevelItem(index)

        newIndex = int(clamp(index + step, 0, self.topLevelItemCount()))

        self.insertTopLevelItem(newIndex, item)
        self.setItemSelected(item, True)
        self.setCurrentItem(item)

    def addItem(self, key, data, enabled=True):  # type: (str, Data, bool) -> None
        print 'addItem', key, data, enabled
        if key in self.getDataDict().keys():
            pattern = re.compile(r'(^[A-Za-z0-9_]*[A-Za-z_]+)(\d*$)')
            matches = pattern.findall(key)

            if not matches:
                raise ValueError('Key \'{}\' is not valid'.format(key))

            name, index = matches[0]
            index = int(index) if index.isdigit() else 0
            index += 1
            return self.addItem('{}{}'.format(name, index), data)

        checkbox = QtWidgets.QCheckBox(self)
        checkbox.setChecked(enabled)

        item = QtWidgets.QTreeWidgetItem(
            (key, data.__class__.__name__)
        )
        item.d = data
        self.addTopLevelItem(item)
        self.setItemWidget(item, 2, checkbox)

    def renameSelectedItem(self):
        selectedItem = self.selectedItems()[0]
        name = selectedItem.text(0)

        ui = RenamerDialog(name)
        newName = ui.exec_()

        if newName:
            selectedItem.setText(0, newName)

    def duplicateSelectedItem(self):
        selectedItem = self.selectedItems()[0]
        self.addItem(selectedItem.text(0), selectedItem.d.copy())

    def populateContextMenu(self):
        addMenu = QtWidgets.QMenu('Add')
        for t in self.types:
            addAction = QtWidgets.QAction(t.__name__, self)
            addAction.triggered.connect(partial(self.addItem, 'untitled', t()))
            addMenu.addAction(addAction)

        selectedItems = self.selectedItems()

        removeAction = QtWidgets.QAction('Remove', self)
        removeAction.triggered.connect(self.removeSelectedItems)
        if not selectedItems:
            removeAction.setEnabled(False)

        duplicateAction = QtWidgets.QAction('Duplicate', self)
        duplicateAction.triggered.connect(self.duplicateSelectedItem)
        if not len(selectedItems) == 1:
            duplicateAction.setEnabled(False)

        moveUpAction = QtWidgets.QAction('Move Up', self)
        moveUpAction.triggered.connect(partial(self.moveSelectedSelectedItem, -1))
        if not len(selectedItems) == 1:
            moveUpAction.setEnabled(False)

        moveDownAction = QtWidgets.QAction('Move Down', self)
        moveDownAction.triggered.connect(partial(self.moveSelectedSelectedItem, 1))
        if not len(selectedItems) == 1:
            moveDownAction.setEnabled(False)

        renameAction = QtWidgets.QAction('Rename', self)
        renameAction.triggered.connect(self.renameSelectedItem)
        if not len(selectedItems) == 1:
            renameAction.setEnabled(False)

        menu = QtWidgets.QMenu()
        menu.addMenu(addMenu)
        menu.addAction(duplicateAction)
        menu.addSeparator()
        menu.addAction(renameAction)
        menu.addSeparator()
        menu.addAction(moveUpAction)
        menu.addAction(moveDownAction)
        menu.addSeparator()
        menu.addAction(removeAction)

        return menu

    def contextMenuEvent(self, event):

        menu = self.populateContextMenu()
        menu.exec_(self.viewport().mapToGlobal(event.pos()))


class DataDictEditor(QtWidgets.QWidget):

    def __init__(self, dataDictList, dataAttributeEditor):  # type: (DataDictList, DataAttributeEditor) -> None
        super(DataDictEditor, self).__init__()

        self.dataDictList = dataDictList
        self.dataAttributeEditor = dataAttributeEditor

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.dataDictList)
        splitter.addWidget(self.dataAttributeEditor)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setMargin(0)
        mainLayout.addWidget(splitter)

        self.setLayout(mainLayout)

        self.dataDictList.currentDataChanged.connect(self.dataAttributeEditor.refresh)
        self.dataAttributeEditor.attributeValueChanged.connect(self.dataDictList.setAttributeValue)

    def refresh(self, dataDict, disabledKeys=None):  # type: (dict[str: Data], list) -> None
        self.dataDictList.refresh(dataDict, disabledKeys=disabledKeys)

    def getDataDict(self):  # type: () -> OrderedDict[str: Data]
        return self.dataDictList.getDataDict()

    def getDisabledKeys(self):
        return self.dataDictList.getDisabledKeys()
