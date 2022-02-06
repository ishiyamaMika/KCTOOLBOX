# -*- coding: utf8 -*-

import os
import sys
import glob
import re
import pprint
mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import *
import KcLibs.win.kc_qt as kc_qt
from KcLibs.win.kc_qt import QtWidgets, QtCore, QtGui, ConnectSignals
from KcTools.multi.KcResultDialog.form.main import KcResultDialog
import KcLibs.win.kc_explorer as kc_explorer
from logging import getLogger

class JobThread(QtCore.QThread):
    message_signal = QtCore.Signal(dict)
    done_signal = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(JobThread, self).__init__(parent)

    def setup(self, project, piece_data, data, order):
        self.project = project
        self.piece_data = piece_data
        self.data = data
        self.order = order

    def run(self):
        self.message_signal.emit("start")
        pass_data, results = self.project.puzzle_play(self.piece_data, 
                                                     self.data, 
                                                     {"signal": self.message_signal}, 
                                                     self.order)
        self.message_signal.emit("done")
        self.done_signal.emit(results)                                                     
    

class KcCopySequence(QtWidgets.QMainWindow):
    NAME = "KcCopySequence"
    VERSION = "1.0.1"
    def __init__(self, parent=None):
        super(KcCopySequence, self).__init__(parent)
        self.tool_directory = kc_env.get_tool_config("win", self.NAME)
        self.icon_directory = "{}/form/icon".format(self.tool_directory)

        self.project_name = "ZIZ"
        self.logger = getLogger("KcCopySequence")
        sh = logging.StreamHandler()
        self.logger.addHandler(sh)
        self.project = KcProject(logger=self.logger)
        self.connected = False

        self.scene_table_list = ["name"]
        self.scene_table_dict = {}

        self.shot_table_list = ["name"]
        self.shot_table_dict = {}

        self.element_table_list = ["check", "name"]
        self.element_table_dict = {"check": {"width": 25, "view": ""}}
        self.connect_signals = ConnectSignals()

        self.change_path_name = ["render", "_Sozai/3d"]

        self.on_check_icon = QtGui.QIcon("{}/check_on.png".format(self.icon_directory))
        self.off_check_icon = QtGui.QIcon("{}/check_off.png".format(self.icon_directory))

        self.th = JobThread(self)
        self.th.message_signal.connect(self.th_message_signal_slot)
        self.th.done_signal.connect(self.th_done_signal_slot)
    
    def th_message_signal_slot(self, message):
        self.ui.message_label.setText(message)

    def th_done_signal_slot(self, results):
        self.ui.message_label.setText("")
        x = KcResultDialog(self)

        x.header_table_dict = {
                              "icon": {
                                    "view": "", 
                                    "width": 25}
                              }

        x.set_ui()
        x.append_header_table(results)
        x.resize(1200, 600)
        x.exec_()

    def set_ui(self):
        ui_path = "{}/form/ui/main.ui".format(self.tool_directory)
        self.ui = kc_qt.load_ui(ui_path, self)

        if hasattr(self, "setCentralWidget"):
            self.setCentralWidget(self.ui)
        else:
            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(self.ui)
            self.setLayout(layout)         
        
        for each in ["scene", "shot", "element"]:
            kc_qt.set_table(getattr(self.ui, "{}_table".format(each)), 
                            getattr(self, "{}_table_list".format(each)), 
                            getattr(self, "{}_table_dict".format(each)))
    
        self.ui.project_combo.addItems(self.project.project_variations.keys())
        project = unicode(self.ui.project_combo.currentText())
        variations = self.project.project_variations[project]
        
        self.ui.variation_combo.clear()
        self.ui.variation_combo.addItems(variations)

        actions = [{"name": "render", "function": self.open_render_action_triggered}, 
                   {"name": "sozai", "function": self.open_sozai_action_triggered}]

        self.element_menu = kc_qt.context_menu(self.ui.element_table, actions, self.element_context_menu)

        self.connect_signals.add(self.ui.reload_btn.clicked, self.reload_btn_clicked)
        self.connect_signals.add(self.ui.execute_btn.clicked, self.execute_btn_clicked)
        self.connect_signals.add(self.ui.scene_table.itemSelectionChanged, self.scene_table_changed)
        self.connect_signals.add(self.ui.shot_table.itemSelectionChanged,self.shot_table_changed)
        self.connect_signals.add(self.ui.shot_table.cellChanged, self.shot_table_cell_changed)
        self.connect_signals.add(self.ui.project_combo.currentIndexChanged, self.project_combo_changed)
        self.connect_signals.add(self.ui.shot_table.itemDoubleClicked, self.shot_table_item_double_clicked)

        self.connect_signals.add(self.ui.element_table.horizontalHeader().sectionClicked, self.element_header_clicked)
        
        self.connect_signals.on()                             

    def element_header_clicked(self, index):
        if index == self.element_table_list.index("check"):
            for r in range(self.ui.element_table.rowCount()):
                check = self.ui.element_table.cellWidget(r, self.element_table_list.index("check"))
                if r == 0:
                    flg = check.is_active
                
                check.is_active = not flg
                self.set_icon(check)

    def open_render_action_triggered(self):

        rows = [l.row() for l in self.ui.element_table.selectedItems() if hasattr(l, "row")]
        row = rows[0]
        item = self.ui.element_table.item(row, self.element_table_list.index("name"))
        if os.path.lexists(item.current_path):
            kc_explorer.open(item.current_path)
   
    def open_sozai_action_triggered(self):
        rows = [l.row() for l in self.ui.element_table.selectedItems() if hasattr(l, "row")]
        row = rows[0]
        item = self.ui.element_table.item(row, self.element_table_list.index("name"))
        path = item.current_path.replace(*self.change_path_name)
        if os.path.exists(path):
            kc_explorer.open(path)
        else:
            QtWidgets.QMessageBox.warning(self, "info", u"フォルダがありません", QtWidgets.QMessageBox.Cancel)

    def element_context_menu(self, point):
        self.element_menu.exec_(self.sender().mapToGlobal(point))

    def reload_btn_clicked(self):
        self.connect_signals.off()
        def _cast(l, template, data):
            match = re.match(template.lower().replace("\\", "/"), l.lower().replace("\\", "/"))
            if match:
                match = match.groups()
                data.setdefault(match[0], {})
                data[match[0]].setdefault(match[1], {})
                keys = (match[2], match[3])
                data[match[0]][match[1]].setdefault(keys, []).append(l)
                # data[match[0]][match[1]][keys].setdefault(match[4], []).append(l)
            
        project = self.ui.project_combo.currentText()
        variation = self.ui.variation_combo.currentText()
        self.project.set(project, variation)
        self.project.set_tool_config("win", self.NAME)
        path = self.project.config["composite"]["default"]["paths"]["render"]
        path = self.project.path_generate(path, {}, force=True)
        keys = self.project.field_generator.get_field_keys(path)
        path_ = path
        template = path.replace("*", "(.*)")

        for key in keys:
            path_ = path_.replace(key, "*")
            template = template.replace(key, "(.*)")

        self.image_data = {}
        [_cast(l, template, self.image_data) for l in glob.glob(path_)]

        self.append_scene_table()
        self.scene_table_changed()

        self.connect_signals.on()
        
    def append_scene_table(self):
        scenes = self.image_data.keys()
        scenes.sort()

        first_items = []
        self.ui.scene_table.setRowCount(len(scenes))
        for r in range(len(scenes)):
            item = QtWidgets.QTableWidgetItem()
            item.setText(scenes[r])
            self.ui.scene_table.setItem(r, self.scene_table_list.index("name"), item)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            if r == 0:
                first_items.append(item)
        
        for item in first_items:
            item.setSelected(True)
    
    def set_icon(self, btn):
        if btn.is_active:
            btn.setIcon(self.on_check_icon)
        else:
            btn.setIcon(self.off_check_icon)


    def execute_btn_clicked(self):
        orders = self.project.tool_config["puzzle"]["orders"]
        main = []
        for r in range(self.ui.element_table.rowCount()):
            check = self.ui.element_table.cellWidget(r, self.element_table_list.index("check")) 
            if not check.is_active:
                continue

            item = self.ui.element_table.item(r, self.element_table_list.index("name"))
            data = {"source_directory": item.current_path}
            data["destination_directory"] = item.current_path.replace(*self.change_path_name)
            main.append(data)

        name = "copySequence"
        self.th.setup(self.project, self.project.tool_config["puzzle"][name], {"main": main}, orders.get(name, orders["default"]))
        self.th.start()

    def scene_table_changed(self):
        scenes = [l.text() for l in self.ui.scene_table.selectedItems()\
                  if l.column() == self.scene_table_list.index("name")]
        
        self.ui.shot_table.clearContents()
        self.ui.shot_table.setRowCount(0)
        self.append_shot_table(scenes)
    
    def append_shot_table(self, scenes):
        if not isinstance(scenes, list):
            scenes = [scenes]
        
        for scene in scenes:
            shots = self.image_data[scene].keys()
            shots.sort()
            for shot in shots:
                r = self.ui.shot_table.rowCount()
                self.ui.shot_table.setRowCount(r+1)

                item = QtWidgets.QTableWidgetItem()
                item.setText(shot)
                item.keys = (scene, shot)
                item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
                self.ui.shot_table.setItem(r, self.shot_table_list.index("name"), item)
    

    def append_element_table(self, scene, shot, add_scene_name=False):
        keys = self.image_data[scene][shot].keys()
        keys.sort()

        for key in keys:
            r = self.ui.element_table.rowCount()
            self.ui.element_table.setRowCount(r+1)
            name = "/".join(key)
            item = QtWidgets.QTableWidgetItem()
            self.ui.element_table.setItem(r, 
                                          self.element_table_list.index("name"), 
                                          item)
            item.setText(name)
            path = self.image_data[scene][shot][key][0]
            item.current_path = os.path.dirname(path)

            check = QtWidgets.QPushButton()
            check.is_active = True
            check.setFlat(True)

            check.row = item.row

            self.set_icon(check)

            self.ui.element_table.setCellWidget(r, 
                                                self.element_table_list.index("check"), 
                                                check)

            check.clicked.connect(self.element_btn_clicked)

    def element_btn_clicked(self):
        active = not self.sender().is_active
        row = self.sender().row()

        rows = [l.row() for l in self.ui.element_table.selectedItems() if l.column() == self.element_table_list.index("name")]
        if not row in rows:
            rows = [row]
        
        for row in rows:
            check = self.ui.element_table.cellWidget(row, self.element_table_list.index("check"))
            check.is_active = active
            self.set_icon(check)


    def shot_table_changed(self):
        self.ui.element_table.clearContents()
        self.ui.element_table.setRowCount(0)
        keys = [l.keys for l in self.ui.shot_table.selectedItems() if hasattr(l, "keys")]
        for key in keys:
            self.append_element_table(scene=key[0], 
                                      shot=key[1],
                                      add_scene_name=len(keys) > 1)

    def project_combo_changed(self):
        pass

    def shot_table_item_double_clicked(self):
        pass

    def shot_table_cell_changed(self):
        pass

def start_app():
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Plastique"))
    QtWidgets.QApplication.setPalette(QtWidgets.QApplication.style().standardPalette())
    x = KcCopySequence()
    x.set_ui()
    x.show()
    x.resize(x.width(), 600)
    app.exec_()

if __name__ in ["__builtin__", "__main__"]:
    start_app()

