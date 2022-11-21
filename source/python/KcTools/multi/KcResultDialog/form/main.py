# -*- coding: utf8 -*-

import os
import sys

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
import KcLibs.win.kc_qt as kc_qt
from KcLibs.win.kc_qt import QtWidgets, QtCore, QtGui


class KcResultDialog(QtWidgets.QDialog):
    NAME = "KcResultDialog"
    VER = 1.0    
    def __init__(self, parent=None):
        super(KcResultDialog, self).__init__(parent)
        self.header_table_list = ["icon", "header"]
        self.header_table_dict = {
                                    "icon": {"view": "", "width": 20}
                                 }

        self.tool_directory = kc_env.get_tool_config("multi", self.NAME)
        self.icon_directory = "{}/form/icon".format(self.tool_directory)

        print(os.path.exists("{}/circle-regular.png".format(self.icon_directory)))

        print("{}/circle-regular.png".format(self.icon_directory))
        self.o_icon = QtGui.QPixmap("{}/circle-regular.png".format(self.icon_directory))
        self.o_icon.scaled(QtCore.QSize(24, 24),  QtCore.Qt.KeepAspectRatio)
        
        self.x_icon = QtGui.QPixmap("{}/times-light.png".format(self.icon_directory))
        self.x_icon.scaled(QtCore.QSize(24, 24),  QtCore.Qt.KeepAspectRatio)

        self.other_icon = QtGui.QPixmap("{}/lightbulb-light.png".format(self.icon_directory))
        self.other_icon.scaled(QtCore.QSize(24, 24),  QtCore.Qt.KeepAspectRatio)

        self.ignore_skip_code = True

    def set_ui(self):
        vlayout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QHBoxLayout()
        vlayout.addLayout(layout)

        self.header_table = QtWidgets.QTableWidget()

        self.header_table.horizontalHeader().setStretchLastSection(True)
        self.header_table.verticalHeader().setVisible(False)
        self.detail = QtWidgets.QPlainTextEdit()
        self.detail.setReadOnly(True)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        layout.addWidget(self.splitter)
        self.splitter.addWidget(self.header_table)
        self.splitter.addWidget(self.detail)

        self.header_table.setAlternatingRowColors(True)
        self.header_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.header_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.header_table.setShowGrid(False)


        self.header_table.itemSelectionChanged.connect(self.header_table_changed)

        btn = QtWidgets.QPushButton()
        btn.clicked.connect(self.close)
        btn.setText("close")
        vlayout.addWidget(btn)
        self.setLayout(vlayout)
        kc_qt.set_table(self.header_table, self.header_table_list, self.header_table_dict)

    def header_table_changed(self):
        selected_items = [l for l in self.header_table.selectedItems() if l.column() == self.header_table_list.index("header")]
        if len(selected_items) == 0:
            return

        self.detail.clear()
        if hasattr(selected_items[0], "detail_text"):
            self.detail.setPlainText(selected_items[0].detail_text)

    def append_header_table(self, results):
        for result in results:
            if self.ignore_skip_code:
                if result[0] == 2:
                    continue
            r = self.header_table.rowCount()
            self.header_table.setRowCount(r+1)
            icon = self.o_icon
            if result[0] == -2:
                self.header_table.setRowHeight(r, 2)
                for c in range(self.header_table.columnCount()):
                    item = QtWidgets.QTableWidgetItem()
                    item.setBackground(QtGui.QColor(15, 15, 15))
                    self.header_table.setItem(r, c, item)
                continue

            elif result[1].startswith("[error]"):
                icon = self.x_icon

            elif result[0] == -1:
                icon = self.other_icon

            icon_widget = QtWidgets.QLabel()
            icon_widget.setPixmap(icon)
            icon_widget.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)

            self.header_table.setCellWidget(r, self.header_table_list.index("icon"), icon_widget)

            item = QtWidgets.QTableWidgetItem()
            item.setText(result[1])
            self.header_table.setItem(r, self.header_table_list.index("header"), item)
            item.detail_text = result[2]

            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)





            


if __name__ == "__builtin__":
    kc_qt.start_app(KcResultDialog, name="KcResultDialog", x=1100, y=500)
