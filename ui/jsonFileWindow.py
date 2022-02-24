
from PySide2 import QtWidgets, QtGui
from RBuild.ui.utils import getMayaMainWindow, deleteSiblingWidgets, size
from ..files.core import JsonFile
from ..core import Data


class JsonFileWindow(QtWidgets.QMainWindow):

    def __init__(self, title=None, parent=None):
        super(JsonFileWindow, self).__init__(parent=getMayaMainWindow() if parent is None else parent)
        deleteSiblingWidgets(self)

        self.title = str(title) if title is not None else self.__class__.__name__
        self.file = None

        self.updateWindowTitle()

        self.setMinimumSize(size(600), size(500))

        # Menu
        newAction = QtWidgets.QAction('New', self)
        newAction.triggered.connect(self.askNew)
        newAction.setShortcut(QtGui.QKeySequence('ctrl+N'))

        openAction = QtWidgets.QAction('Open...', self)
        openAction.triggered.connect(self.askOpen)
        openAction.setShortcut(QtGui.QKeySequence('ctrl+O'))

        recentFilesMenu = QtWidgets.QMenu('Recent Files')
        recentFilesMenu.setEnabled(False)

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
        fileMenu.addMenu(recentFilesMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addAction(incrementSaveAction)

        menuBar = QtWidgets.QMenuBar()
        menuBar.addMenu(fileMenu)

        self.setMenuBar(menuBar)

        self.mainLayout = QtWidgets.QVBoxLayout()

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(self.mainLayout)

        self.setCentralWidget(centralWidget)

    def incrementSave(self):
        pass

    def save(self, path, force=False):
        self.file = JsonFile(path)
        self.file.dump(self.getData(), force=force)
        self.updateWindowTitle()
        print('{} -> File saved: {}'.format(self.title, self.file))

    def open(self, path):
        f = JsonFile(path)
        try:
            self.refresh(f.load())
            self.file = f
            self.updateWindowTitle()
            print('{} -> File opened: {}'.format(self.title, self.file))
        except TypeError:
            print('{} -> File could not be opened: {}'.format(self.title, f))

    def clear(self):
        self.file = None
        self.updateWindowTitle()
        self.refresh()

    def refresh(self, data=None):  # type: (Data) -> None
        pass

    def updateWindowTitle(self):
        path = 'untitled' if self.file is None else str(self.file)
        title = '{}: {}'.format(self.title, path)
        self.setWindowTitle(title)

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
            event.accept()

    def getData(self):  # type: () -> Data
        return Data()


