import os
from functools import partial
from PySide2 import QtWidgets, QtGui, QtCore
from rigBuilder.ui.utils import getMayaMainWindow, deleteSiblingWidgets, size
from ..files.core import JsonFile
from ..core import Data


class AskToSave(QtWidgets.QDialog):

    save = 1
    ignore = 0
    cancel = -1

    def __init__(self, title='Warning', text='Save before continuing?', parent=None):
        super(AskToSave, self).__init__(parent or getMayaMainWindow())

        self.result = self.cancel

        self.setWindowTitle(title)

        label = QtWidgets.QLabel(text)

        saveBtn = QtWidgets.QPushButton('Save')
        saveBtn.clicked.connect(partial(self.set, self.save))

        ignoreBtn = QtWidgets.QPushButton('Ignore')
        ignoreBtn.clicked.connect(partial(self.set, self.ignore))

        cancelBtn = QtWidgets.QPushButton('Cancel')
        cancelBtn.clicked.connect(partial(self.set, self.cancel))

        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(saveBtn)
        buttonLayout.addWidget(ignoreBtn)
        buttonLayout.addWidget(cancelBtn)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addWidget(label)
        mainLayout.addLayout(buttonLayout)

    def exec_(self):
        super(AskToSave, self).exec_()
        return self.result

    def set(self, value):
        self.result = value
        self.accept()


class Settings(Data):

    def __init__(self, recentFiles=None):
        super(Settings, self).__init__()
        if recentFiles is None:
            recentFiles = list()

        self.recentFiles = [os.path.normpath(path) for path in recentFiles]


class JsonFileWindow(QtWidgets.QMainWindow):

    def __init__(self, title=None, parent=None):
        super(JsonFileWindow, self).__init__(parent=getMayaMainWindow() if parent is None else parent)
        deleteSiblingWidgets(self)

        # file
        self._file = None

        # title
        self.title = str(title) if title is not None else self.__class__.__name__

        # settings
        self.recentFiles = list()

        # size
        self.setMinimumSize(size(600), size(500))

        # Menu
        newAction = QtWidgets.QAction('New', self)
        newAction.triggered.connect(self.askNew)
        newAction.setShortcut(QtGui.QKeySequence('ctrl+N'))

        openAction = QtWidgets.QAction('Open...', self)
        openAction.triggered.connect(self.askOpen)
        openAction.setShortcut(QtGui.QKeySequence('ctrl+O'))

        self.recentFilesMenu = QtWidgets.QMenu('Recent Files')

        saveAction = QtWidgets.QAction('Save', self)
        saveAction.triggered.connect(self.askSave)
        saveAction.setShortcut(QtGui.QKeySequence('ctrl+S'))

        saveAsAction = QtWidgets.QAction('Save As...', self)
        saveAsAction.triggered.connect(self.askSaveAs)
        saveAsAction.setShortcut(QtGui.QKeySequence('ctrl+shift+S'))

        incrementSaveAction = QtWidgets.QAction('Increment and Save', self)
        incrementSaveAction.setEnabled(False)
        incrementSaveAction.setShortcut(QtGui.QKeySequence('ctrl+alt+S'))

        fileMenu = QtWidgets.QMenu('File')
        fileMenu.addAction(newAction)
        fileMenu.addSeparator()
        fileMenu.addAction(openAction)
        fileMenu.addMenu(self.recentFilesMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addAction(incrementSaveAction)

        menuBar = QtWidgets.QMenuBar()
        menuBar.addMenu(fileMenu)

        self.setMenuBar(menuBar)

        # main Layout
        self.mainLayout = QtWidgets.QVBoxLayout()

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(self.mainLayout)

        self.setCentralWidget(centralWidget)

        # set file to None
        self.file = None

        self.loadSettings()

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, value):  # type: (JsonFile) -> None
        self._file = value

        # Update window title
        self.updateWindowTitle()

        # add to recent files
        if self._file is not None:
            path = os.path.normpath(self._file)

            if path not in self.recentFiles:
                self.recentFiles.append(path)

        # Update recent file in menu bar
        self.updateRecentFilesMenu()

    def updateRecentFilesMenu(self):
        self.recentFilesMenu.clear()
        for path in self.recentFiles:
            action = QtWidgets.QAction(path, self)
            action.triggered.connect(partial(self.askOpenRecent, path))
            self.recentFilesMenu.addAction(action)

    def askOpenRecent(self, path):
        result = QtWidgets.QMessageBox.question(
            self,
            "File Not Saved",
            "Continue anyways?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result == QtWidgets.QMessageBox.No:
            return

        self.open(path)

    def updateWindowTitle(self):
        pathRepr = 'untitled' if self._file is None else str(self._file)
        self.setWindowTitle('{} -> {}'.format(self.title, pathRepr))

    def incrementSave(self):
        pass

    def save(self, path, force=False):
        self.file = JsonFile(path)
        self.file.dump(self.getData(), force=force)
        print('{} -> File saved: {}'.format(self.title, self.file))

    def open(self, path):
        f = JsonFile(path)
        self.refresh(f.load())
        self.file = f
        print('{} -> File opened: {}'.format(self.title, self.file))
        print('{} -> File opened: {}'.format(self.title, self.file))

    def clear(self):
        self.file = None
        self.refresh()

    def refresh(self, data=None):  # type: (Data) -> None
        pass

    def askNew(self):
        result = QtWidgets.QMessageBox.question(
            self,
            "File Not Saved",
            "Continue anyways?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result == QtWidgets.QMessageBox.No:
            return

        self.clear()

    def askSave(self):
        if self.file is None:
            self.askSaveAs()
        else:
            self.save(self.file, force=True)

    def askSaveAs(self):
        caption = '{}: Save File'.format(self.title)
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption=caption, filter='Json File (*.json)')
        if not path:
            return
        self.save(path, force=True)

    def askOpen(self):
        result = QtWidgets.QMessageBox.question(
            self,
            "File Not Saved",
            "Continue anyways?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result == QtWidgets.QMessageBox.No:
            return

        caption = '{}: Open File'.format(self.title)
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption=caption, filter='Json File (*.json)')
        if not path:
            return
        self.open(path)
        self.saveSettings()

    def closeEvent(self, event):
        result = QtWidgets.QMessageBox.question(
            self,
            "File Not Saved",
            "Continue anyways?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result == QtWidgets.QMessageBox.No:
            event.ignore()
        else:
            self.saveSettings()

            event.accept()

    def saveSettings(self):
        path = os.path.join(os.path.expanduser('~'), '{}Settings.json'.format(self.__class__.__name__))

        settings = Settings(
            recentFiles=self.recentFiles,
        )

        f = JsonFile(path)
        f.dump(settings, force=True)

    def loadSettings(self):
        path = os.path.join(os.path.expanduser('~'), '{}Settings.json'.format(self.__class__.__name__))

        f = JsonFile(path)
        try:
            settings = f.load()
        except:
            settings = None

        if not isinstance(settings, Settings):
            return Settings()

        self.recentFiles = settings.recentFiles
        self.updateRecentFilesMenu()

    def getData(self):  # type: () -> Data
        return Data()


