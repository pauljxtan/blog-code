#!/bin/env python3

import logging
import os
import sys

from PySide2.QtWidgets import QApplication

import data
from main_window import MainWindow

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # Create the tables if not existing
    data.db.create_tables([data.Tag, data.File, data.FileTag])

    app = QApplication(sys.argv)
    MainWindow('.').show()
    sys.exit(app.exec_())
