import os

from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import (QAction, QGridLayout, QHeaderView, QLabel, QLineEdit, QMenu,
                               QTableView, QWidget)

import data

class Tagging(QWidget):
    def __init__(self):
        super().__init__()

        self._selected_filepath = ''

        layout = QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel('Add tag:'))

        self._entry = QLineEdit()
        self._entry.returnPressed.connect(self._add_tag_to_selected_file)
        layout.addWidget(self._entry, 0, 1)

        self._tagtable = TagTable(self._remove_selected_file_tag)

        self._tagtable_model = QStandardItemModel()
        self._tagtable_model.setHorizontalHeaderLabels(['Tag', '# Files'])
        self._tagtable.setModel(self._tagtable_model)

        layout.addWidget(self._tagtable, 1, 0, 1, 2)

    def reload(self, filepath):
        self._selected_filepath = filepath

        filename = os.path.split(filepath)[-1]
        tags = data.get_file_tags(filename)

        self._tagtable_model.removeRows(0, self._tagtable_model.rowCount())
        for name, count in tags:
            self._tagtable_model.appendRow([QStandardItem(name), QStandardItem(str(count))])

        self._entry.clear()
        print('Loaded {} tags for {}'.format(len(tags), filename))

    def _remove_selected_file_tag(self):
        filename = os.path.split(self._selected_filepath)[-1]
        tagname = self._get_selected_tag()
        data.delete_filetag(filename, tagname)

        print('Removed tag {} from {}'.format(tagname, filename))
        self.reload(self._selected_filepath)

    def _get_selected_tag(self):
        idx = self._tagtable.selectionModel().currentIndex()
        if idx.column() != 0:
            # Get tagname even if another column is selected
            idx = idx.siblingAtColumn(0)
        return self._tagtable_model.itemFromIndex(idx).text()

    def _add_tag_to_selected_file(self):
        filename = os.path.split(self._selected_filepath)[-1]
        tagname = self._entry.text().strip().replace(' ', '_').lower()
        if tagname == '':
            print('Refusing to add empty tag')
            return
        if data.create_filetag(filename, tagname):
            self.reload(self._selected_filepath)
            print('Added tag {} to {}'.format(tagname, filename))
        else:
            print('{} already has tag {}'.format(filename, tagname))
        self._entry.clear()

class TagTable(QTableView):
    def __init__(self, callback_remove_tag):
        super().__init__()

        # Make it look a little nicer
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)

        self._remove_action = QAction('Remove tag from file')
        self._remove_action.triggered.connect(callback_remove_tag)

    # Override
    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction(self._remove_action)
        # The position of the right-click on the screen is passed to the removal callback
        menu.exec_(event.globalPos())
