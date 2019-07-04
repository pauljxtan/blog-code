from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QScrollArea,
                               QSplitter)

from file_tree import FileTree
from image_display import ImageDisplay
from tagging import Tagging

class MainWindow(QMainWindow):
    def __init__(self, init_root_path):
        super().__init__()

        self.setWindowTitle('Qt image tagger example')

        self._root_path = init_root_path
        self._make_menubar(init_root_path)

        splitter, self._filetree, self._tagging, self._image = self._widgets()
        self.setCentralWidget(splitter)

    def _make_menubar(self, init_root_path):
        menubar = self.menuBar()

        def _on_change_dir_clicked():
            path = QFileDialog.getExistingDirectory(self, 'Change image directory', init_root_path)
            if path:
                self._root_path = path
                self._filetree.set_root_path(path)

        change_root_action = QAction('Change image directory', self)
        change_root_action.triggered.connect(_on_change_dir_clicked)
        menubar.addAction(change_root_action)

        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(QApplication.quit)
        menubar.addAction(quit_action)

    def _widgets(self):
        splitter = QSplitter()

        # -- Left
        left_splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(left_splitter)

        # Top left
        filetree = FileTree(self._root_path, self._on_filetree_selection_changed)
        left_splitter.addWidget(filetree)

        # Bottom left
        tagging = Tagging()
        left_splitter.addWidget(tagging)

        # -- Right
        image = ImageDisplay()
        # Wrap it in a resizable scroll area
        area = QScrollArea()
        area.setWidget(image)
        area.setWidgetResizable(True)
        area.setAlignment(Qt.AlignCenter)
        splitter.addWidget(area)

        # A slight hack to split width equally
        splitter.setSizes([100000, 100000])

        return splitter, filetree, tagging, image

    def _on_filetree_selection_changed(self, new_selection, _old_selection):
        indices = new_selection.indexes()

        filepath = self._filetree.model().filePath(indices[0])
        if filepath:
            self._image.set(filepath)
            self._tagging.reload(filepath)
