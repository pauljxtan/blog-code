from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtWidgets import QFileSystemModel, QTreeView

import data

IMG_EXTS = ('gif', 'jpeg', 'jpg', 'png')

class FileTree(QTreeView):
    def __init__(self, init_root_path, callback_selection_changed):
        super().__init__()

        # Optimization: https://doc.qt.io/qt-5/qtreeview.html#uniformRowHeights-prop
        # (This helps a lot for large directories)
        self.setUniformRowHeights(True)

        model = FileTreeModel()

        # Disable selection of files not matching certain image extensions
        model.setNameFilters(['*.{}'.format(ext) for ext in IMG_EXTS])

        self.setModel(model)
        self.set_root_path(init_root_path)

        header = self.header()
        # Hide some columns (filesize, etc.) we don't care about
        header.hideSection(1)
        header.hideSection(2)
        header.hideSection(3)

        self.setColumnWidth(0, 300)

        # Connect the selection change event to the given callback
        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(callback_selection_changed)

    def set_root_path(self, path):
        self.model().setRootPath(path)
        self.setRootIndex(self.model().index(path))

    def selected_filepath(self):
        self.model().filePath(self._selected_index())

    def _selected_index(self):
        idx = self.selectionModel().currentIndex()
        # We want the index of the filename column even if another is selected
        if idx.column() != 0: return idx.siblingAtColumn(0)
        return idx

class FileTreeModel(QFileSystemModel):
    def __init__(self):
        super().__init__()

    # Override
    def columnCount(self, parent=QModelIndex()):
        return super().columnCount() + 1

    # Override
    def data(self, index, role):
        # Default columns
        if index.column() < self.columnCount() - 1:
            return super().data(index, role)
        # Tag count column
        if index.column() == self.columnCount() - 1 and role == Qt.DisplayRole:
            filename = self.fileName(index.siblingAtColumn(0))
            return len(data.get_file_tags(filename))

    # Override
    def headerData(self, section, orientation, role):
        # Default columns
        if section < self.columnCount() - 1:
            return super().headerData(section, orientation, role)
        # Tag count column
        if section == self.columnCount() - 1 and role == Qt.DisplayRole:
            return '# Tags'
