# -*- coding: utf8 -*-

import os
import sys
import copy
import traceback
import time
import datetime
import importlib
import shutil
import glob
import re
import pprint

from logging import getLogger

logger = getLogger("kcToolBox")


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
import KcLibs.win.kc_qt as kc_qt
import KcLibs.win.kc_explorer as kc_explorer
import KcLibs.win.kc_file_io as kc_win_file_io


from KcLibs.win.kc_qt import QtWidgets, QtCore, QtGui

from KcLibs.core.KcProject import *

kc_file_io = importlib.import_module("KcLibs.{}.kc_file_io".format(kc_env.mode))

if kc_env.mode == "mobu":
    import KcLibs.mobu.kc_model as kc_model
    import KcLibs.mobu.kc_transport_time as kc_transport_time
    import KcLibs.mobu.kc_camera as kc_camera

import traceback
kc_env.append_sys_paths()
from Sticky.Sticky import FieldValueGenerator
from KcTools.multi.KcResultDialog.form.main import KcResultDialog


class CamSelecter(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CamSelecter, self).__init__(parent)
    
    def set_ui(self, cams):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        self.select_check = QtWidgets.QCheckBox("Select")
        self.select_check.setChecked(True)
        layout.addWidget(self.select_check)

        for cam in cams:
            btn = QtWidgets.QPushButton(cam["name"])
            btn.camera_info = cam
            btn.clicked.connect(self.cam_btn_clicked)
            layout.addWidget(btn)
            btn.setMinimumWidth(200)
            if cam.get("is_project_asset"):
                btn.setStyleSheet("background-color: rgb(100, 100, 200); color: white;")
        
        switcher_btn = QtWidgets.QPushButton("switcher")
        switcher_btn.clicked.connect(self.cam_btn_clicked)
        switcher_btn.setStyleSheet("background-color: rgb(200, 200, 100); color: black;")
        switcher_btn.camera_info = {"name": "switcher"}

        close_btn = QtWidgets.QPushButton("close")
        layout.addWidget(switcher_btn)
        layout.addWidget(close_btn)
        close_btn.clicked.connect(self.close)
        self.setLayout(layout)
        self.setWindowTitle("cam selecter")
    
    def cam_btn_clicked(self):
        cam_info = self.sender().camera_info
        if "namespace" in cam_info and cam_info["namespace"]:
            name = "{}:{}".format(cam_info["namespace"], cam_info["name"])
        else:
            name = cam_info["name"]
        kc_camera.change_cam(name, select=self.select_check.isChecked())

class GroupDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(GroupDialog, self).__init__(parent)
    
    def set_ui(self, shot_name, groups):
        layout = QtWidgets.QVBoxLayout()
        self.widgets = {}
        layout.addWidget(QtWidgets.QLabel("create file & backburner option"))
        layout.addWidget(QtWidgets.QLabel(shot_name))
        for group in groups:
            hlayout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(group)
            job_create = QtWidgets.QCheckBox()

            sdw_suspended = QtWidgets.QCheckBox()
            sdw_suspended.setText("sdw suspended")

            sdw_create = QtWidgets.QCheckBox()
            sdw_create.setText("create sdw file && job")
            sdw_create.setCheckState(QtCore.Qt.Checked)
            sdw_create.sdw_suspended = sdw_suspended

            job_create.sdw_suspended = sdw_suspended
            job_create.sdw_create = sdw_create
            job_create.setText("create file && job")
            job_create.setCheckState(QtCore.Qt.Checked)

            hlayout.addWidget(label)
            hlayout.addWidget(job_create)
            hlayout.addWidget(sdw_create)
            hlayout.addWidget(sdw_suspended)

            self.widgets[group] = {
                                   "sdw_create": sdw_create,
                                   "job_create": job_create,
                                   "sdw_suspended": sdw_suspended
                                  }

            job_create.clicked.connect(self.job_create_clicked)
            sdw_create.clicked.connect(self.sdw_create_clicked)
            layout.addLayout(hlayout)

        btn = QtWidgets.QPushButton()
        layout.addWidget(btn)

        btn.clicked.connect(self.btn_clicked)
        btn.setText("OK")
        self.setLayout(layout)
    
    def sdw_create_clicked(self):
        self.sender().sdw_suspended.setEnabled(self.sender().checkState() == QtCore.Qt.Checked)

    def job_create_clicked(self):
        self.sender().sdw_create.setEnabled(self.sender().checkState() == QtCore.Qt.Checked)
        self.sender().sdw_suspended.setEnabled(self.sender().checkState() == QtCore.Qt.Checked)
    
    def btn_clicked(self):
        self.close()

class AssetDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AssetDialog, self).__init__(parent)


    def set_ui(self, asset_type, namespace, path, project):
        self.asset_type = asset_type
        self.project = project
        self.namespace = namespace
        self.path = path
        
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setText(namespace)
        
        # self.check_box = QtWidgets.QCheckBox()
        # self.check_box.setText(u"自動でナンバリング")
        # self.check_box.setCheckState(QtCore.Qt.Checked)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(QtWidgets.QLabel(u"追加数"))

        self.number_spin = QtWidgets.QSpinBox()
        self.number_spin.setMinimum(1)
        self.number_spin.setMaximum(999)

        hlayout.addWidget(self.number_spin)

        merge_btn = QtWidgets.QPushButton()
        merge_btn.setText("merge")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.line_edit)
        # layout.addWidget(self.check_box)

        layout.addLayout(hlayout)

        layout.addWidget(merge_btn)

        merge_btn.clicked.connect(self.merge_btn_clicked)

        self.setLayout(layout)

    def merge_btn_clicked(self):
        namespace_ = str(self.line_edit.text())
        results = []
        for i in range(self.number_spin.value()):
            # kc_file_io.file_merge(str(self.path), namespace=namespace_)
            context, result = self.project.puzzle_play(self.project.config["puzzle"]["mobu_merge_asset"], 
                                                       {"main": {
                                                           "namespace": namespace_, 
                                                           "asset_type": self.asset_type, 
                                                           "asset_path": self.path}
                                                       })
            results.extend(result)
        if sum([l[0] for l in results]) == 0:
            QtWidgets.QMessageBox.information(self, "info", u"追加しました", QtWidgets.QMessageBox.Ok)
            self.close()

class GetConfigs(QtCore.QThread):
    each_signal = QtCore.Signal(dict, dict, str)
    def __init__(self, parent=None):
        super(GetConfigs, self).__init__(parent)
        self.mutex = QtCore.QMutex()

    def setup(self, root_directory, filter_):
        self.root_directory = root_directory
        self.filter = filter_
        self.end = False

    def stop(self):
        with QtCore.QMutexLocker(self.mutex):
            self.end = True

    def run(self):
        for each in os.listdir(self.root_directory):
            if not each.endswith(".json"):
                continue

            if self.end:
                return 

            if self.filter:
                if not self.filter in each:
                    continue

            path = "{}/{}".format(self.root_directory, each)
            try:
                js = kc_win_file_io.load_json(path)
                info, data = js["info"], js["data"]
                self.each_signal.emit(info, data, path)
                time.sleep(0.05)
            except:
                print(traceback.format_exc())
                print(path, "---failed")

class RecordDialog(QtWidgets.QDialog):
    record = QtCore.Signal(dict, str, list, bool)
    def __init__(self, parent=None):
        super(RecordDialog, self).__init__(parent)
        self.widgets = {}
        self.cmd = KcSceneManagerCmd()

    def set_ui(self, project, fields, padding, path, default={}, save_as_mode=False, relative_items=[], frame_check_state=False, cam_check_state=False):
        self.save_as_mode = save_as_mode
        self.project = project
        self.path = path
        self.padding = padding
        layout = QtWidgets.QVBoxLayout()
        add_fields = [] # ["start", "end"]

        time_dict = kc_transport_time.get_scene_time()
        if not "start" in default:
            default["start"] = str(time_dict["loop_start"])
        if not "end" in default:
            default["end"] = str(time_dict["loop_stop"])

        if not "fps" in default:
            default["fps"] = str(time_dict["fps"])

        for each in fields + add_fields:
            if not save_as_mode:
                if each in ["<take>", "<version>", "<user>", "<progress>"]:
                    continue
            if each == "start":
                line = QtWidgets.QFrame()
                line.setGeometry(QtCore.QRect(320, 150, 118, 3))
                line.setFrameShape(QtWidgets.QFrame.HLine)
                line.setFrameShadow(QtWidgets.QFrame.Sunken)
                layout.addWidget(line)

            hlayout = QtWidgets.QHBoxLayout()

            if each in padding and padding[each] != -1:
                label_text = u"{} ({}桁)".format(each, padding[each])
            else:
                label_text = each
            label = QtWidgets.QLabel(label_text)
            label.setMinimumWidth(100)
            label.setMaximumWidth(100)

            line = QtWidgets.QLineEdit()
            line.setFrame(False)

            if each in default:
                line.setText(default[each])

            hlayout.addWidget(label)
            hlayout.addWidget(line)

            layout.addLayout(hlayout)
            
            line.setObjectName(each)
            self.widgets[each] = line

            line.setAlignment(QtCore.Qt.AlignCenter)

        """
        camera_combo = QtWidgets.QComboBox()
        cameras = [l["namespace"] for l in self.project.get_cameras()]
        camera_combo.addItems(cameras)
        layout.addWidget(camera_combo)
        """

        self.time_check = QtWidgets.QCheckBox()
        self.time_check.setText(u"start, end, fpsの更新")

        if not save_as_mode:
            self.time_check.setVisible(False)

        if frame_check_state:
            self.time_check.setCheckState(QtCore.Qt.Checked)
        else:
            self.time_check.setCheckState(QtCore.Qt.Unchecked)

        layout.addWidget(self.time_check)


        self.cam_check = QtWidgets.QCheckBox()
        if not save_as_mode:
            self.cam_check.setVisible(False)

        self.cam_check.setText(u"camera追加")
        if cam_check_state:
            self.cam_check.setCheckState(QtCore.Qt.Checked)
        else:
            self.cam_check.setCheckState(QtCore.Qt.Unchecked)

        layout.addWidget(self.cam_check)


        # layout.addWidget(line)
        self.relative_checkboxes = []
        if len(relative_items) > 0:
            group = QtWidgets.QGroupBox()
            group.setTitle(u"関連カット")
            vlayout = QtWidgets.QVBoxLayout()

            for relative in relative_items:
                check_box = QtWidgets.QCheckBox(relative.text())
                vlayout.addWidget(check_box)
                check_box.setCheckState(QtCore.Qt.Checked)
                check_box.shot_item = relative
                self.relative_checkboxes.append(check_box)

            group.setLayout(vlayout)
            layout.addWidget(group)

        btn = QtWidgets.QPushButton()
        btn.setText(u"登録/更新")
        layout.addWidget(btn)
        btn.clicked.connect(self.btn_clicked)
        self.setLayout(layout)


    def btn_clicked(self):
        data = {}
        error = []
        for name, widget in self.widgets.items():
            value = widget.text()
            data[name] = value
            if name in self.padding and self.padding[name] != -1:
                if value == "":
                    error.append(u"{}が空欄です".format(name))
                elif value.isdigit():
                    if len(value) != self.padding[name]:
                        error.append(u"paddingが一致しません: {} => {}桁".format(value, self.padding[name]))
                else:
                    temp_ = ""
                    trigger = False
                    for v in value:
                        if v.isdigit():
                            temp_ += v
                            trigger = True

                        else:
                            if trigger:
                                break

                    if len(temp_) != self.padding[name]:
                        error.append(u"paddingが一致しません: {} => {}桁".format(temp_, self.padding[name]))                    

        if "<progress>" in data:
            if data["<progress>"] == "":
                error.append(u"作業内容(progress)が空欄です")

        if self.time_check.checkState() == QtCore.Qt.Checked:
            if kc_env.mode == "mobu":
                scene_time = kc_transport_time.get_scene_time()
                data["start"] = scene_time["zoom_start"]
                data["end"] = scene_time["zoom_stop"]
                data["fps"] = scene_time["fps"]

        if len(error) > 0:
            QtWidgets.QMessageBox.warning(self, "info", u"\n".join(error), QtWidgets.QMessageBox.Cancel)
        else:
            relatives = []
            for check_box in self.relative_checkboxes:
                if check_box.checkState() == QtCore.Qt.Checked:
                    relatives.append(check_box.shot_item)

            self.record.emit(data, self.path, relatives, self.cam_check.checkState()==QtCore.Qt.Checked)
            self.close()

class KcSceneManager(kc_qt.ROOT_WIDGET):
    NAME = "KcSceneManager"
    VERSION = "2.0.7"

    def __init__(self, parent=None):
        super(KcSceneManager, self).__init__(parent)
        self.logger = kc_env.get_logger(self.NAME)
        self.tool_directory = kc_env.get_tool_config("multi", self.NAME)
        self.icon_directory = "{}/form/icon".format(self.tool_directory)
        self.project_name = "ZIZ"
        self.project = KcProject(logger=self.logger)
        self.preset_value_widgets = {}
        self.project_name = ""
        self.variation_name = ""
        self.cmd = KcSceneManagerCmd()

        self.reload_tree_flag = False

        self.connected = False

        self.scene_table_list = ["name"]
        self.scene_table_dict = {}

        self.shot_table_list = ["check", "master", "name", "start", "end", "fps", "user", "time"]
        self.shot_table_dict = {"check": {"width": 20, "view": ""}, 
                                "master": {"width": 20, "view": ""}, 
                                "name": {"width": 150},
                                "start": {"width": 45, "view": "start"}, 
                                "end": {"width": 45, "view": "end"}, 
                                "fps": {"width": 45, "view": "fps"}, 
                                "user": {"width": 100}}

        self.asset_table_list = ["check", "name", "group"]
        self.asset_table_dict = {"check": {"width": 20, "view": ""}, 
                                 "name": {"width": 180}, 
                                 "group": {"view": "group"}}

        self.record_table_list = ["name"]
        self.record_table_dict = {}

        self.exist_asset_table_list = ["category", "namespace", "path"]
        self.exist_asset_table_dict = {"category": {"width": 50}, 
                                       "namespace": {"width": 175}}

        self.user = kc_env.get_user()

        self.on_check_icon = QtGui.QIcon("{}/check_on.png".format(self.icon_directory))
        self.off_check_icon = QtGui.QIcon("{}/check_off.png".format(self.icon_directory))

        self.tree_icon = QtGui.QIcon("{}/database-duotone.png.png".format(self.icon_directory))
        self.blank_icon = QtGui.QIcon("")

        self.cam_selecter_icon = QtGui.QIcon("{}/camera-movie-duotone.png".format(self.icon_directory))

        self.current_shot_item = False
        self.project_files = []

        self.category_assets = {}
        self.exist_asset_table_categories = {}

        self.o_icon = QtGui.QPixmap("{}/box-full-solid.png".format(self.icon_directory))
        self.o_icon.scaled(QtCore.QSize(24, 24),  QtCore.Qt.KeepAspectRatio)

        self.ignore = []

        self.colors = {
                        "enabled": QtGui.QColor(220, 220, 220),
                        "disabled": QtGui.QColor(100, 100, 100)
                      }

        self.asset_table_state = {
            "scene": {"color": QtGui.QColor(200, 200, 255), "tooltip": u"シーンに存在しますが設定ファイルに登録されていません", "state": False},
            "config": {"color": QtGui.QColor(255, 100, 100), "tooltip": u"設定ファイルにしか存在しません", "state": True},
            "both": {"color": self.colors["enabled"], "tooltip": u"設定ファイルに登録されています", "state": True}
            }

    def context_menu(self):
        menu = QtWidgets.QMenu()
        delete_action = QtWidgets.QAction(u"削除", self)

        menu.addAction(delete_action)

        return menu

    def set_ui(self):
        ui_path = "{}/form/ui/main.ui".format(self.tool_directory)
        self.ui = kc_qt.load_ui(ui_path, self)
        if kc_env.mode == "win":
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.ui)
            self.setLayout(layout)
            self.show()

        # self.resize(1000, 1000)

        self.set_table(self.ui.scene_table)
        self.set_table(self.ui.shot_table)
        self.set_table(self.ui.asset_table)
        self.set_table(self.ui.record_table)
        self.set_table(self.ui.exist_asset_table)
        self.connect_signals(True)


        self.ui.directory_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.directory_tree.customContextMenuRequested.connect(self.directory_tree_request)

        self.ui.cam_selecter_btn.setIcon(self.cam_selecter_icon)
        self.ui.cam_selecter_btn.setIconSize(QtCore.QSize(32, 32))

        
        self.tree_menu = QtWidgets.QMenu(self)
        add_shot_action = QtWidgets.QAction(u"登録/更新", self)
        add_shot_action.triggered.connect(self.add_shot_action_triggered)

        update_shot_frames_action = QtWidgets.QAction(u"zoomエリアでフレーム更新", self)


        open_file_action = QtWidgets.QAction(u"開く", self)

        self.tree_menu.addAction(open_file_action)
        self.tree_menu.addAction(add_shot_action)

        open_file_action.triggered.connect(self.open_file_action_triggered)
        self.ui.split_check.setVisible(False)
        self.ui.render_check.setVisible(False)

        self.ui.shot_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.shot_table.customContextMenuRequested.connect(self.shot_table_request)

        self.shot_table_menu = QtWidgets.QMenu(self)

        self.shot_table_menu.addSeparator().setText("file")

        open_file_menu = QtWidgets.QMenu(u"開く", self)
        edit_file_open_action = QtWidgets.QAction(u"edit", self)
        self.master_file_open_action = QtWidgets.QAction(u"master", self)

        save_as_action = QtWidgets.QAction(u"別名保存", self)

        explorer_menu = QtWidgets.QMenu(u"エクスプローラ", self)

        config_explorer_action = QtWidgets.QAction(u"設定ファイル", self)
        edit_explorer_action = QtWidgets.QAction(u"edit", self)
        self.master_explorer_action = QtWidgets.QAction(u"master", self)
        explorer_menu.addAction(edit_explorer_action)
        explorer_menu.addAction(self.master_explorer_action)
        explorer_menu.addAction(config_explorer_action)

        self.shot_table_menu.addMenu(open_file_menu)
        open_file_menu.addAction(edit_file_open_action)
        open_file_menu.addAction(self.master_file_open_action)
        self.shot_table_menu.addMenu(explorer_menu)

        self.shot_table_menu.addAction(save_as_action)
        edit_file_open_action.triggered.connect(self.open_action_triggered)
        self.master_file_open_action.triggered.connect(self.master_file_open_action_triggered)
        save_as_action.triggered.connect(self.save_as_action_triggered)


        self.asset_menu = QtWidgets.QMenu(self)
        self.delete_from_config_action = QtWidgets.QAction(u"設定ファイルから削除", self)

        self.asset_menu.addAction(self.delete_from_config_action)

        self.delete_from_config_action.triggered.connect(self.delete_from_config_action_triggered)

        self.ui.asset_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.asset_table.customContextMenuRequested.connect(self.asset_table_request)

        self.shot_table_menu.addSeparator().setText("config")
        delete_action = QtWidgets.QAction(u"設定削除", self)

        self.shot_table_menu.addAction(add_shot_action)
        config_explorer_action.triggered.connect(self.config_explorer_action_triggered)

        self.shot_table_menu.addAction(update_shot_frames_action)
        update_shot_frames_action.triggered.connect(self.update_shot_frames_action_triggered)




        edit_explorer_action.triggered.connect(self.edit_explorer_action_triggered)
        self.master_explorer_action.triggered.connect(self.master_explorer_action_triggered)

        self.shot_table_menu.addAction(delete_action)

        delete_action.triggered.connect(self.delete_action_triggered)



        self.ui.project_combo.addItems(self.project.project_variations.keys())
        project = self.ui.project_combo.currentText()
        variations = self.project.project_variations[project]
        self.ui.variation_combo.clear()
        self.ui.variation_combo.addItems(variations)


        self.exist_asset_table_menu = QtWidgets.QMenu(self)
        asset_open_action = QtWidgets.QAction(u"開く", self)
        asset_merge_action = QtWidgets.QAction(u"マージ", self)
        asset_explorer_action = QtWidgets.QAction(u"エクスプローラ", self)
        self.exist_asset_table_menu.addAction(asset_open_action)
        self.exist_asset_table_menu.addAction(asset_merge_action)
        self.exist_asset_table_menu.addAction(asset_explorer_action)

        self.exist_asset_table_menu.addSeparator().setText("config")
        config_menu = QtWidgets.QMenu(u"選択", self)
        self.exist_asset_table_menu.addMenu(config_menu)
        for each in ["plot", "export"]:
            asset_config_action = QtWidgets.QAction(each, self)
            asset_config_action.triggered.connect(getattr(self, "asset_config_{}_triggered".format(each)))
            config_menu.addAction(asset_config_action)

        asset_open_action.triggered.connect(self.open_exist_asset_action_triggered)
        asset_merge_action.triggered.connect(self.merge_exist_asset_action_triggered)
        asset_explorer_action.triggered.connect(self.config_explorer_action_triggered)

        self.ui.exist_asset_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.exist_asset_table.customContextMenuRequested.connect(self.exist_asset_table_request)

        self.ui.splitter.setSizes([100, 350, 200])
        self.ui.directory_splitter.setSizes([100, 400])

        self.asset_menu.addSeparator().setText("comp")
        comp_groups_action = QtWidgets.QAction(u"アセットをgroup化", self)

        select_model_action = QtWidgets.QAction(u"シーンのmodelを選択", self)
        select_from_scene_action = QtWidgets.QAction(u"シーンから行を選択", self)

        self.asset_menu.addAction(comp_groups_action)
        comp_groups_action.triggered.connect(self.comp_groups_action_triggered)

        self.asset_menu.addAction(select_model_action)
        self.asset_menu.addAction(select_from_scene_action)

        select_model_action.triggered.connect(self.select_model_action_triggered)
        select_from_scene_action.triggered.connect(self.select_from_scene_action_triggered)

        self.ui.render_scale_combo.addItems(["1/2", "1", "1/4"])
    
    def select_model_action_triggered(self):
        namespaces = [each.text() for each in self.ui.asset_table.selectedItems() \
                      if each.column() == self.asset_table_list.index("name")]

        kc_model.select_geo_from_namespaces(namespaces)

    def select_from_scene_action_triggered(self):
        namespaces = kc_model.get_selected_namespaces()
        for r in range(self.ui.asset_table.rowCount()):
            item = self.ui.asset_table.item(r, self.asset_table_list.index("name"))
            for c in range(self.ui.asset_table.columnCount()):
                item_ = self.ui.asset_table.item(r, c)
                if item_:
                    item_.setSelected(item.text() in namespaces)

    def comp_groups_action_triggered(self):
        if not self.current_shot_item:
            return
        
        rows = [l.row() for l in self.ui.asset_table.selectedItems() if hasattr(l, "row")]
        
        text, ok = QtWidgets.QInputDialog.getText(self, "info", u"group name")
        if not ok:
            return
        
        for row in rows:
            group_item = self.ui.asset_table.item(row, self.asset_table_list.index("group"))
            group_item.setText(text)

            key_item = self.ui.asset_table.item(row, self.asset_table_list.index("name"))
            key_item.row_data.setdefault("comp", {})
            key_item.row_data["comp"]["group_name"] = text

        kc_env.save_config(self.current_shot_item.config_path, self.NAME, "shot_config", self.current_shot_item.row_data)


    def asset_config_plot_triggered(self):
        self.select_config_models("plot")

    def asset_config_export_triggered(self):
        self.select_config_models("export")

    def select_config_models(self, config_type):
        selected_items = [l for l in self.ui.exist_asset_table.selectedItems() if l.column() == self.exist_asset_table_list.index("namespace")]
        if len(selected_items) == 0:
            return
        asset_path = selected_items[0].asset_path
        namespace = selected_items[0].text()

        path = self.cmd.get_config_path(asset_path, namespace, config_type)
        if path:
            self.cmd.select_from_config(path)

    def is_same(self, a, b):
        if not a or not b:
            return False

        if os.path.normpath(a).lower().replace("\\", "/") == os.path.normpath(b).lower().replace("\\", "/"):
            return True
        return False

    def get_same_file_records(self, path):
        items = []
        for r in range(self.ui.shot_table.rowCount()):
            item = self.ui.shot_table.item(r, self.shot_table_list.index("name"))
            path_ = item.row_data["paths"][kc_env.mode]["edit"]
            if self.is_same(path, path_):
                items.append(item)

        return items

    def add_shot_action_triggered(self):
        default = {}
        if self.ui.tab_widget.currentIndex() == 0:
            items = [l for l in self.ui.shot_table.selectedItems() if l.column() == self.shot_table_list.index("name")]

            if len(items) > 0:
                item = items[0]
                path = items[0].row_data["paths"][kc_env.mode]["edit"]
                default = copy.deepcopy(item.row_data)
            else:
                path = self.cmd.get_current_path()
                fields = self.project.field_generator.get_field_value(self.project.config["shot"][kc_env.mode]["paths"]["edit"], path)
                if fields:
                    default["fields"] = fields
                else:
                    default["fields"] = {}

            default["fields"].setdefault("<project>", self.project.name)
            default_data = {}
            for k, v in default["fields"].items():
                if k.startswith("<"):
                    default_data[k] = v
                elif isinstance(v, list):
                    continue
                elif isinstance(v, dict):
                    continue

                default_data["<{}>".format(k)] = v

            default_data.setdefault("<user>", kc_env.get_user())
            self.open_record_dialog(path, False, default=default_data, check_state=True)

        else:
            items = self.ui.directory_tree.selectedItems()
            if len(items) != 1:
                return

            item = items[0]
            fields = self.project.field_generator.get_field_value(self.project.config["shot"][kc_env.mode]["paths"]["edit"], item.full_path)
            if fields:
                default["fields"] = fields
            else:
                default["fields"] = {}

            default["fields"].setdefault("<project>", self.project.name)
            default_data = {}
            for k, v in default["fields"].items():
                if k.startswith("<"):
                    default_data[k] = v
                elif isinstance(v, list):
                    continue
                elif isinstance(v, dict):
                    continue

                default_data["<{}>".format(k)] = v

            self.open_record_dialog(item.full_path, False, default=default_data)

    def record_btn_clicked(self):
        current_path = self.cmd.get_current_path()
        self.open_record_dialog(current_path, False)

    def save_as_action_triggered(self):
        current_path = self.cmd.get_current_path()
        app = kc_env.mode
        self.project.field_generator.get_field_keys(current_path)

        default = self.project.field_generator.get_field_value(self.project.config["shot"][app]["paths"]["edit"], current_path)

        if not default:
            default = {}

        if "<version>" in default:
            if default["<version>"].isdigit():
                version = int(default["<version>"]) + 1
                padding = "{{:0{}d}}".format(self.project.config["general"]["padding"]["<version>"])
                default["<version>"] = padding.format(version)
        else:
            default = self.project.tool_config["default_shot_name"]
            default["<user>"] = kc_env.get_user()

        self.open_record_dialog(current_path, True, default)

    def open_record_dialog(self, path, save_as_mode=False, default={}, check_state=False):
        relative_items = self.get_same_file_records(path)
        dialog = RecordDialog(self)
        """
        app = "mobu"
        current_path = self.cmd.get_current_path()
        """
        app = kc_env.mode

        fields = self.project.field_generator.get_field_keys(os.path.basename(self.project.config["shot"][app]["paths"]["edit"]))
        if save_as_mode:
            path = False

        dialog.set_ui(self.project,
                      fields,
                      self.project.config["general"]["padding"],
                      path,
                      default,
                      save_as_mode=save_as_mode,
                      relative_items=relative_items,
                      frame_check_state=check_state,
                      cam_check_state=check_state)

        if save_as_mode:
            dialog.record.connect(self.record_save_as_dialog_slot)
        else:
            dialog.record.connect(self.record_update_dialog_slot)

        dialog.show()

    def record_update_dialog_slot(self, data, path, relative_items, cam_check):
        if cam_check:
            self.append_camera(data)
        self.update_record_from_dialog(data, path)
        self.update_relative_record_path(relative_items, path)
        QtWidgets.QMessageBox.information(self, "info", u"変更しました", QtWidgets.QMessageBox.Ok)

    def append_camera(self, data):

        namespace = self.project.path_generate(self.project.config["asset"]["namespaces"]["camera"], data)
        cam_path = self.project.get_latest_camera_path()
        if not cam_path:
            return

        cameras = self.project.get_cameras()
        if True in [l["namespace"] == namespace for l in cameras]:
            return

        kc_file_io.file_merge(str(cam_path), namespace=namespace)

    def update_relative_record_path(self, relative_items, path, save_as=False):
        for relative_item in relative_items:
            data = {}
            name = relative_item.text()
            data["paths"] = {}
            data["paths"][kc_env.mode] = {}
            data["paths"][kc_env.mode]["edit"] = path
            self.update_record(name, save_as, **data)

    def record_save_as_dialog_slot(self, data, path, relative_items, cam_check):
        if cam_check:
            self.append_camera(data)

        save_path = self.update_record_from_dialog(data, path)

        if os.path.exists(save_path):
            mes = QtWidgets.QMessageBox.information(self, "info", u"ファイルが存在します。上書きしますか？", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if mes == QtWidgets.QMessageBox.No:
                return
        self.update_relative_record_path(relative_items, save_path, save_as=True)
        self.cmd.file_save(save_path)
        QtWidgets.QMessageBox.information(self, "info", u"保存しました", QtWidgets.QMessageBox.Ok)
        if self.current_scene_item:
            self.reload(self.current_scene_item.text())
        else:
            self.reload()

    def update_record_from_dialog(self, data, path):
        if not path:
            data["<root_directory>"] = self.project.config["general"]["root_directory"]
            edit_path = self.project.config["shot"][kc_env.mode]["paths"]["edit"]
            path = self.project.path_generate(edit_path, data)

            master_path_template = self.project.config["shot"][kc_env.mode]["paths"]["master"]
            master_path = self.project.path_generate(master_path_template, data)

        name = self.project.field_generator.generate(self.project.config["shot"]["name_pattern"], data)
        fields = self.project.field_generator.get_field_value(self.project.config["shot"][kc_env.mode]["paths"]["edit"], path)
        if not fields:
            fields = {}
        fields["project"] = self.project_name
        fields["<root_directory>"] = self.project.config["general"]["root_directory"]
        fields["<user>"] = kc_env.get_user()
        fields["<project_variation>"] = self.project.variation
        fields_ = {}
        for k, v in fields.items():
            match = re.match(r"<(.+)>", k)
            if match:
                fields_[match.group(1)] = v
            else:
                fields_[k] = v

        update_data = {
                "paths": {
                          kc_env.mode: {"edit": path, "master": master_path}
                          },
                "fields": fields_
        }
        if "fps" in data:
            update_data["frame"] = {}
            update_data["frame"]["fps"] = int(data["fps"])
            update_data["frame"]["start"] = data["start"]
            update_data["frame"]["end"] = data["end"]

        info, data, path_ = self.update_record(name, False, **update_data)

        current_file_path = self.cmd.get_current_path()
        for r in range(self.ui.shot_table.rowCount()):
            item = self.ui.shot_table.item(r, self.shot_table_list.index("name"))
            if not item:
                continue
            if item.text() == name:
                # 同じ名前のshotがあったら追加しない
                return path

        self.append_shot_table(info, data, path_, current_file_path)

        return path
    
    def config_view_filter(self):
        for k, v in self.project.tool_config.get("view", {}).items():
            print(k, v)
            getattr(self.ui, k).setVisible(v)

    def record_dialog_slot(self, data, path):
        name = self.project.field_generator.generate(self.project.config["shot"]["name_pattern"], data)
        sequence_name = self.get_sequence(name)
        if not sequence_name:
            sequence_name = "others"

        json_path = "{}/{}/{}.json".format(self.project.tool_config["directory"], sequence_name, name)
        # info = kc_env.get_info(name="KcSceneManager")

        js_info, js_data = self.project.read(json_path)

        if os.path.exists(json_path):
            js_data["paths"][kc_env.mode] = path
            # kc_win_file_io.dump_json(json_path, {"info": info, "data": js_data})
        else:
            js_data.setdefault("paths", {})
            js_data["paths"][kc_env.mode] = path
            js_data["start"] = 0
            js_data["end"] = 0
            js_data["fps"] = 0
            js_data.update(data)
            # kc_win_file_io.dump_json(json_path, {"info": info, "data": js_data})

        kc_env.save_config(json_path, self.NAME, "shot_config", js_data)

    def get_sequence(self, name):
        fields = self.project.field_generator.get_field_value(self.project.config["shot"]["name_pattern"], name)

        sequence_settings = self.project.config["shot"]["sequence_name_settings"]
        sequence_name = self.project.path_generate(sequence_settings["template"], fields)

        if not sequence_name:
            print("name pattern is not match: {} {}".format(self.project.config["shot"]["name_pattern"], name))
            return False

        if "prefix" in sequence_settings:
            sequence_name = sequence_settings["prefix"] + sequence_name
        if "suffix" in sequence_settings:
            sequence_name += sequence_settings["suffix"]

        return sequence_name

    def update_record(self, name, save_as, **kwargs):
        sequence = self.get_sequence(name)

        json_path = "{}/{}/{}.json".format(self.project.tool_config["directory"], sequence, name)

        # info = kc_env.get_info(name="KcSceneManager")

        schema = self.project.tool_config["schema"]["shot"]
        js_info = {}
        if os.path.exists(json_path):
            js_info, js_data = self.project.sticky.read(json_path)
        else:
            js_data = {}

        js_data_ = self.project.sticky.values_override(schema, js_data)
        data_ = self.project.sticky.values_override(js_data_, kwargs)

        # kc_win_file_io.dump_json(json_path, {"info": info, "data": data_})
        user = kc_env.get_user()
        if save_as:
            user = kc_env.get_user()
        else:
            if "user" in js_info:
                user = js_info["user"]

        flg, info, data_ = kc_env.save_config(json_path, self.NAME, "shot_config", data_, user=user)

        return info, data_, json_path

    def directory_tree_request(self, point):
        self.tree_menu.exec_(self.sender().mapToGlobal(point))

    def asset_table_request(self, point):
        selected_items = [l for l in self.ui.asset_table.selectedItems() if l.column() == self.asset_table_list.index("name")]
        if len(selected_items) == 0:
            return 

        item = selected_items[0]
        if item.row_data["type"] in ["config", "both"]:
            self.delete_from_config_action.setVisible(True)
        else:
            self.delete_from_config_action.setVisible(False)

        self.asset_menu.exec_(self.sender().mapToGlobal(point))        

    def delete_from_config_action_triggered(self):
        rows = [l.row() for l in self.ui.asset_table.selectedItems() if l.column() == self.asset_table_list.index("name")]
        if len(rows) == 0:
            return 

        res = QtWidgets.QMessageBox.information(self, "info", u"設定ファイルから削除しますか?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if res == QtWidgets.QMessageBox.No:
            return

        item = self.current_shot_item
        info, data = self.project.sticky.read(item.config_path)
        config_assets = data.get("assets", [])

        pop_index = []

        for row in rows:
            item_ = self.ui.asset_table.item(row, self.asset_table_list.index("name"))
            namespace = item_.text()

            for i, asset in enumerate(config_assets):
                if namespace == asset["namespace"]:
                    pop_index.append(i)
                    self.ui.asset_table.setRowHidden(row, True)

        pop_index = list(set(pop_index))
        pop_index.sort(reverse=True)
        for i in pop_index:
            config_assets.pop(i)

        self.current_shot_item.row_data = data

        kc_env.save_config(item.config_path, self.NAME, "shot_config", item.row_data)

    def shot_table_request(self, point):
        selected_items = [l for l in self.ui.shot_table.selectedItems() if l.column() == self.shot_table_list.index("name")]
        if len(selected_items) == 0:
            path = False
            
        else:
            path = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["master"], selected_items[0].row_data["fields"])
        
        if path and os.path.lexists(path):
            self.master_file_open_action.setVisible(True)
            self.master_explorer_action.setVisible(True)
        else:
            self.master_file_open_action.setVisible(False)
            self.master_explorer_action.setVisible(False)

        self.shot_table_menu.exec_(self.sender().mapToGlobal(point))

    def exist_asset_table_request(self, point):
        self.exist_asset_table_menu.exec_(self.sender().mapToGlobal(point))

    def connect_signals(self, flg):
        if flg and not self.connected:
            self.ui.scene_table.itemSelectionChanged.connect(self.scene_table_changed)
            self.ui.shot_table.itemSelectionChanged.connect(self.shot_table_changed)
            self.ui.shot_table.cellChanged.connect(self.shot_table_cell_changed)

            self.ui.user_check.clicked.connect(self.user_check_clicked)
            self.ui.create_master_btn.clicked.connect(self.create_master_btn_clicked)
            self.ui.tab_widget.tabBarClicked.connect(self.tab_widget_clicked)
            self.ui.record_table.itemSelectionChanged.connect(self.record_table_item_selection_changed)
            self.ui.directory_tree.clicked.connect(self.directory_tree_clicked)
            self.ui.reload_btn.clicked.connect(self.reload_btn_clicked)

            self.ui.project_combo.currentIndexChanged.connect(self.project_combo_changed)

            self.ui.render_btn.clicked.connect(self.render_btn_clicked)

            self.ui.shot_table.itemDoubleClicked.connect(self.shot_table_item_double_clicked)
            self.ui.master_check.clicked.connect(self.master_check_clicked)
            self.ui.split_check.clicked.connect(self.split_check_clicked)


            self.ui.cam_selecter_btn.clicked.connect(self.cam_selecter_btn_clicked)


            self.connected = True

        elif not flg and self.connected:
            self.ui.scene_table.itemSelectionChanged.disconnect(self.scene_table_changed)
            self.ui.shot_table.itemSelectionChanged.disconnect(self.shot_table_changed)

            self.ui.user_check.clicked.disconnect(self.user_check_clicked)
            self.ui.create_master_btn.clicked.disconnect(self.create_master_btn_clicked)
            self.ui.tab_widget.tabBarClicked.disconnect(self.tab_widget_clicked)
            self.ui.record_table.itemSelectionChanged.disconnect(self.record_table_item_selection_changed)
            self.ui.directory_tree.clicked.disconnect(self.directory_tree_clicked)
            self.ui.reload_btn.clicked.disconnect(self.reload_btn_clicked)
            self.ui.shot_table.cellChanged.disconnect(self.shot_table_cell_changed)

            self.ui.project_combo.currentIndexChanged.disconnect(self.project_combo_changed)
            self.ui.render_btn.clicked.disconnect(self.render_btn_clicked)

            self.ui.shot_table.itemDoubleClicked.disconnect(self.shot_table_item_double_clicked)

            self.ui.master_check.clicked.disconnect(self.master_check_clicked)
            self.ui.split_check.clicked.disconnect(self.split_check_clicked)

            self.ui.cam_selecter_btn.clicked.disconnect(self.cam_selecter_btn_clicked)

            self.connected = False
    
    def cam_selecter_btn_clicked(self):
        self.cam_selecter = CamSelecter(self)
        cameras_ = self.project.get_cameras()
        cameras = sorted(cameras_, key=lambda x: x["name"])
        self.cam_selecter.set_ui(cameras)
        self.cam_selecter.show()

    def split_check_clicked(self):
        self.ui.render_check.setCheckState(self.sender().checkState())

    def master_check_clicked(self):
        if self.sender().checkState() == QtCore.Qt.Checked:
            if self.project.tool_config.get("convert_to") is None:
                self.ui.create_master_btn.setText(u"export")
            else:
                self.ui.create_master_btn.setText(u"convert")
            self.ui.render_btn.setText(u"master render")
            self.ui.render_btn.setVisible(False)
            self.ui.split_check.setVisible(True)
            self.ui.render_check.setVisible(True)
            self.ui.render_scale_combo.setVisible(False)
        else:
            self.ui.create_master_btn.setText(u"create master")
            self.ui.render_btn.setText(u"edit render")
            self.ui.render_btn.setVisible(True)
            self.ui.split_check.setVisible(False)
            self.ui.render_check.setVisible(False)
            self.ui.render_scale_combo.setVisible(True)
        self.config_view_filter()

    def shot_table_item_double_clicked(self, item):
        if not hasattr(item, "column"):
            return

        name_item = self.ui.shot_table.item(item.row(), self.shot_table_list.index("name"))
        if name_item.is_file_opened:
            namespace = self.project.path_generate(self.project.config["asset"]["namespaces"]["camera"], name_item.row_data["fields"])
            frame = name_item.row_data["frame"]
            self.project.change_camera(namespace, **frame)

    def project_combo_changed(self):
        self.project_name = self.ui.project_combo.currentText()
        variations = self.project.project_variations[self.project_name]
        self.ui.variation_combo.clear()
        self.ui.variation_combo.addItems(variations)

    def shot_table_cell_changed(self, r, c):
        item = self.ui.shot_table.item(r, self.shot_table_list.index("name"))

        if c == self.shot_table_list.index("start"):
            try:
                item.row_data["frame"]["start"] = int(self.ui.shot_table.item(r, c).text())
            except:
                import traceback
                print(traceback.format_exc())
                return
        elif c == self.shot_table_list.index("end"):
            try:
                item.row_data["frame"]["end"] = int(self.ui.shot_table.item(r, c).text())
            except:
                import traceback
                print(traceback.format_exc())                
                return

        elif c == self.shot_table_list.index("fps"):
            try:
                item.row_data["frame"]["fps"] = int(self.ui.shot_table.item(r, c).text())
            except:
                import traceback
                print(traceback.format_exc())                
                return

        # kc_win_file_io.dump_json(item.config_path, data)
        kc_env.save_config(item.config_path, self.NAME, "shot_config", item.row_data)

    def reload_btn_clicked(self):
        self.reload_tree_flag = False
        self.project_name = self.ui.project_combo.currentText()
        self.variation_name = self.ui.variation_combo.currentText()
        selected_items = self.ui.scene_table.selectedItems()
        name = False
        if len(selected_items) > 0:
            name = selected_items[0].text()
        self.reload(name)

        if name:
            self.list_shot_table(name)

        self.reload_directory_tree()

    def directory_tree_clicked(self, index):
        tree_item = self.ui.directory_tree.itemFromIndex(index)

        if not hasattr(tree_item, "records"):
            return

        self.connect_signals(False)
        for item in self.ui.record_table.selectedItems():
            item.setSelected(False)

        for item in tree_item.records:
            item.setSelected(True)

        self.connect_signals(True)

    def record_table_item_selection_changed(self):
        for item in self.ui.directory_tree.selectedItems():
            item.setSelected(False)

        record_selection = self.ui.record_table.selectedItems()
        for each in record_selection:
            for item in each.file_items:
                item.setSelected(True)

    def append_exist_asset_table(self, data, scene_assets):
        if isinstance(data, list):
            for d in data:
                self.append_exist_asset_table(d, scene_assets)
        else:
            r = self.ui.exist_asset_table.rowCount()
            self.ui.exist_asset_table.setRowCount(r+1)

            for k, v in data.items():
                name = k.replace("<", "").replace(">", "")
                if not name in self.exist_asset_table_list:
                    continue

                item = QtWidgets.QTableWidgetItem()
                if v:
                    item.setText(v)

                self.ui.exist_asset_table.setItem(r, self.exist_asset_table_list.index(name), item)
                item.row_data = data
                item.asset_path = data["<path>"]

                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

            namespace_item = self.ui.exist_asset_table.item(r, self.exist_asset_table_list.index("namespace"))
            namespace = namespace_item.text()
            color = [220, 220, 220]
            for asset in scene_assets:
                if namespace == asset["true_namespace"]:
                    color = [220, 220, 220]
                else:
                    color = [150, 150, 150]

            for c in range(self.ui.exist_asset_table.columnCount()):
                item = self.ui.exist_asset_table.item(r, c)
                if not item:
                    continue

                item.setForeground(QtGui.QColor(*color))

    def open_file_action_triggered(self):
        items = [l for l in self.ui.directory_tree.selectedItems()]
        if len(items) == 0:
            return 

        path = str(items[0].full_path)
 
        if path.lower().endswith(".fbx"):
            mes = QtWidgets.QMessageBox.information(self, "info", u"開きますか？", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if mes == QtWidgets.QMessageBox.Yes:
                self.cmd.file_open(path)

    def append_record_table(self, data):
        r = self.ui.record_table.rowCount()
        self.ui.record_table.setRowCount(r+1)

        item = QtWidgets.QTableWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        item.file_items = []
        item.setText(data)
        self.ui.record_table.setItem(r, self.record_table_list.index("name"), item)
        return item

    def get_exist_asset_table_categories_state(self):
        states = {}
        for i in range(self.ui.category_check_layout.count()):
            child = self.ui.category_check_layout.itemAt(i)
            if isinstance(child.widget(), QtWidgets.QCheckBox):
                states[child.widget().category_name] = child.widget().checkState() == QtCore.Qt.Checked

        return states

    def tab_widget_clicked(self, index):
        def _is_same(a, b):
            if a.lower().replace("\\", "/") == b.lower().replace("\\", "/"):
                return True
            return False
        if not self.project:
            return

        if index == 0:
            return
        elif index == 1:
            if not self.reload_tree_flag:
                self.create_tree(self.project.tool_config["shot_directory"])
            self.reload_directory_tree()
        else:
            states = self.get_exist_asset_table_categories_state()

            for i in range(self.ui.category_check_layout.count())[::-1]:
                self.ui.category_check_layout.takeAt(i)

            scene_Assets = self.project.get_assets()
            try:
                self.get_category_assets()
            except BaseException:
                import traceback
                print(traceback.format_exc())
                return
            self.ui.exist_asset_table.clearContents()
            self.ui.exist_asset_table.setRowCount(0)

            for each in self.project.config["asset"]["category"]:
                if each not in self.category_assets:
                    continue

                check = QtWidgets.QCheckBox()
                check.setText(each)
                self.ui.category_check_layout.addWidget(check)
                check.category_name = each

                if each in states:
                    if states[each]:
                        check.setCheckState(QtCore.Qt.Checked)
                    else:
                        check.setCheckState(QtCore.Qt.Unchecked)
                else:
                    check.setCheckState(QtCore.Qt.Checked)

                check.clicked.connect(self.exist_asset_table_filter)

                assets = self.category_assets[each]
                for name, assets_ in assets.items():
                    self.append_exist_asset_table(assets_[-1], scene_Assets)

            spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.ui.category_check_layout.addSpacerItem(spacer)

            self.exist_asset_table_filter()

    def exist_asset_table_filter(self):
        states = self.get_exist_asset_table_categories_state()
        for r in range(self.ui.exist_asset_table.rowCount()):
            item = self.ui.exist_asset_table.item(r, self.exist_asset_table_list.index("category"))
            if not item:
                continue

            category = item.text()
            self.ui.exist_asset_table.setRowHidden(r, not states[category])

    def reload_directory_tree(self):
        true_color = (220, 220, 220)
        false_color = (140, 140, 140)
        self.current_shot_item = False
        self.current_scene_item = False
        self.ui.record_table.clearContents()
        self.ui.record_table.setRowCount(0)
        paths = {}
        for r in range(self.ui.shot_table.rowCount()):
            item = self.ui.shot_table.item(r, self.shot_table_list.index("name"))
            path = item.row_data["paths"][kc_env.mode]["edit"]
            if path == "":
                continue

            if not path:
                continue

            path = os.path.normpath(path).lower().replace("\\", "/")

            record_item = self.append_record_table(item.text())
            paths.setdefault(path, []).append(record_item)

        it = QtWidgets.QTreeWidgetItemIterator(self.ui.directory_tree)

        items = []
        names = {}

        while not it.value() is None:
            if hasattr(it.value(), "full_path"):
                full_path = os.path.normpath(it.value().full_path).lower().replace("\\", "/")
                if full_path in paths:
                    for item in paths[full_path]:
                        item.file_items.append(it.value())

                    items.append(it.value())
                    it.value().setForeground(0, self.colors["enabled"])
                    it.value().records = paths[full_path]

                else:
                    it.value().current_records = []
                    it.value().setForeground(0, self.colors["disabled"])
                    it.value().records = []
                
            it += 1

        for item in items:
            parent = item.parent()
            while parent:
                parent.setExpanded(True)
                parent.setForeground(0, self.colors["enabled"])
                parent = parent.parent()

    def reload(self, selection_name=""):
        self.ui.scene_table.clearContents()
        self.ui.scene_table.setRowCount(0)

        self.ui.shot_table.clearContents()
        self.ui.shot_table.setRowCount(0)
        self.ui.asset_table.clearContents()
        self.ui.asset_table.setRowCount(0)

        self.project.set(self.project_name, self.variation_name)
        self.project.set_tool_config("multi", self.NAME)

        show_columns = self.project.tool_config.get("columns", {}).get("asset_table", [])
        if len(show_columns) != 0:
            print(show_columns)
            for c, name in enumerate(self.asset_table_list):
                if name in show_columns:
                    continue
                else:
                    self.ui.asset_table.hideColumn(c)





        # info, self.project_config = self.project.sticky.read("{}/config.json".format(self.project.tool_config["directory"]))

        if not os.path.lexists(self.project.tool_config["directory"]):
            os.makedirs(self.project.tool_config["directory"])

        scenes = [l for l in os.listdir(self.project.tool_config["directory"]) if os.path.isdir("{}/{}".format(self.project.tool_config["directory"], l))]
        scenes.sort()
        scenes = [u"all"] + scenes


        # self.project_files = [l for l in os.listdir(self.project.tool_config["directory"]) if l != "config.json" and os.path.isfile("{}/{}".format(self.project.tool_config["directory"], l))]

        # scenes = list(set([_split(l) for l in self.project_files]))
        # scenes.sort()

        # scenes = [u"all"] + scenes

        self.append_scene_table(scenes, selection_name)
        

    def edit_explorer_action_triggered(self):
        if not self.current_shot_item:
            return
        
        path = self.current_shot_item.row_data["paths"][kc_env.mode].get("edit")
        if not path is None:
            kc_explorer.open(path)

    def master_explorer_action_triggered(self):
        if not self.current_shot_item:
            return
        path = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["master"], self.current_shot_item.row_data["fields"])
        if path:
            if os.path.exists(path):
                kc_explorer.open(path)

    def update_shot_frames_action_triggered(self):
        if not self.current_shot_item.is_file_opened:
            return

        time_dict = kc_transport_time.get_scene_time()
        self.current_shot_item.row_data["frame"]["start"] = int(time_dict["zoom_start"])
        self.current_shot_item.row_data["frame"]["end"] = int(time_dict["zoom_stop"])
        self.current_shot_item.row_data["frame"]["fps"] = int(time_dict["fps"])

        kc_env.save_config(self.current_shot_item.config_path, 
                           self.NAME, 
                           "shot_config", 
                           self.current_shot_item.row_data)

        self.connect_signals(False)
        for each in ["start", "end", "fps"]:
            item = self.ui.shot_table.item(self.current_shot_item.row(), self.shot_table_list.index(each))
            if not item:
                continue

            item.setText(str(self.current_shot_item.row_data["frame"][each]))

        self.connect_signals(True)

    def config_explorer_action_triggered(self):
        if self.ui.tab_widget.currentIndex() == 0:
            selected_items = [l for l in self.ui.shot_table.selectedItems() if l.column() == self.shot_table_list.index("name")]
        else:
            selected_items = [l for l in self.ui.exist_asset_table.selectedItems() if l.column() == self.exist_asset_table_list.index("namespace")]

        if len(selected_items) == 0:
            return

        item = selected_items[0]
        path = False
        if hasattr(item, "config_path"):
            if not item.config_path:
                return
            path = item.config_path

        elif hasattr(item, "asset_path"):
            path = item.asset_path

        if not path:
            return

        kc_explorer.open(path)


    def delete_action_triggered(self):
        selected_items = [l for l in self.ui.shot_table.selectedItems() if l.column() == self.shot_table_list.index("name")]
        if len(selected_items) == 0:
            return

        mes = QtWidgets.QMessageBox.warning(self, "info", u"削除しますか?", QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
        if mes == QtWidgets.QMessageBox.Cancel:
            return

        dte = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        for item in selected_items[::-1]:
            if not item.config_path:
                continue

            d, f = os.path.split(item.config_path)
            archive_path = "{}/archive/{}/{}".format(d, dte, f)
            if not os.path.exists(os.path.dirname(archive_path)):
                os.makedirs(os.path.dirname(archive_path))

            shutil.move(item.config_path, archive_path)

            self.ui.shot_table.removeRow(item.row())

    def render_btn_clicked(self):
        render_scale = self.get_render_scale()
        self.render_scene("edit", render_scale)

    def render_scene(self, mode, render_scale):
        items = [l for l in self.get_shot_table_active_item_data()]
        errors = []
        results_all = []

        for i, item in enumerate(items):
            data = {}
            data["shot_name"] = item["shot_name"]
            data["start"] = item["frame"]["start"]
            data["end"] = item["frame"]["end"]
            data["fps"] = item["frame"]["fps"]
            data["user"] = kc_env.get_user()
            data.update(item["fields"])

            if mode == "edit":
                data["path"] = item["paths"].get(kc_env.mode, {}).get(mode)
            else:
                data["path"] = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["master"], data)

            if not data["path"]:
                print("parse error:", self.project.config["shot"][kc_env.mode]["paths"]["master"])
                continue
            if not os.path.exists(data["path"]):
                print("master not exists:", data["path"])
                continue

            flg = True
            for key in ["start", "end", "fps"]:
                if not isinstance(data[key], int):
                    errors.append("{}: {} not exists".format(item["shot_name"], key))
                    flg = False
                elif key == "fps" and data["fps"] == 0:
                    errors.append("fps is zero: {}".format(item["shot_name"]))
                    flg = False

            if not flg:
                continue

            if not os.path.exists(data["path"]):
                errors.append("{} not exists: {}".format(item["shot_name"], data["path"]))
                continue

            movie_path = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["{}_movie".format(mode)], data)

            data["movie_path"] = movie_path

            data["render_scale"] = render_scale
           
            context, results = self.project.puzzle_play(self.project.tool_config["puzzle"]["mobu_edit_render"], 
                                                       {"primary": data})

            results_all.append([-1, item["shot_name"], item["shot_name"], u"処理開始"])
            results_all.extend(results)
            results_all.append([-2, "-", "-", u"処理しました"])
     
        if len(results_all) != 0:
            x = KcResultDialog(self)
            x.set_ui()
            x.append_header_table(results_all)
            x.resize(1200, 600)
            x.exec_()
        
        if len(errors) > 0:
            for error in errors:
                print(error)
    
    def get_render_scale(self):
        scale = self.ui.render_scale_combo.currentText()
        value = 1
        if scale == "1/2":
            value = 0.5
        elif scale == "1/4":
            value = 0.25
        return value
    

    def convert_execute(self):
        address = False
        if self.ui.render_check.checkState() == QtCore.Qt.Checked:
            address, ok = QtWidgets.QInputDialog.getText(self, "info", u"address", text=self.project.config["general"]["network"]["backbarner"])
            if not ok:
                address = False

        items = [l for l in self.get_shot_table_active_item_data()]
        render_scale = self.get_render_scale()
        results_all = []
        now_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        for item in items:
            errors = []
            data = {"primary": {}, "main": [], "common": {"project": self.project}}

            data["primary"]["path"] = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["master"], item["fields"])

            if not data["primary"]["path"]:
                continue

            data["primary"]["start"] = item["frame"]["start"]
            data["primary"]["end"] = item["frame"]["end"]
            data["primary"]["fps"] = item["frame"].get("fps", 24)

            assets_by_groups = {}
            cam_asset = False
            no_group_error = []
            for asset in item.get("assets", []):
                if not asset.get("selection") and asset["category"] != "camera":
                    continue

                asset = copy.deepcopy(asset)
                asset["scene"] = item["fields"]["scene"]
                asset["cut"] = item["fields"]["cut"]
                asset["start"] = item["frame"]["start"]
                asset["end"] = item["frame"]["end"]

                if "comp" in asset:
                    if "group_name" in asset["comp"]:
                        assets_by_groups.setdefault(asset["comp"]["group_name"], []).append(asset)
                else:
                    if asset["category"] != "camera":
                        no_group_error.append(asset["namespace"])

                if asset["category"] in self.project.config["asset"][kc_env.mode]["paths"]:
                    template = self.project.config["asset"][kc_env.mode]["paths"][asset["category"]]
                    max_template = self.project.config["asset"]["max"]["paths"][asset["category"]]
                else:
                    template = self.project.config["asset"][kc_env.mode]["paths"]["default"]
                    max_template = self.project.config["asset"]["max"]["paths"]["default"]

                if not "config" in template:
                    continue

                asset["config"] = {"plot": self.project.path_generate(template["config"].replace("<config_type>", "plot"), asset), 
                                   "export": self.project.path_generate(template["config"].replace("<config_type>", "export"), asset)} 

                asset["mobu_master_export_path"] = self.project.path_generate(template["master_export"], asset)
                asset["max_asset_path"] = False

                if asset["category"] == "camera":
                    camera_path = self.project.get_latest_camera_path("max")
                    asset["max_asset_path"] = camera_path
                    cam_asset = asset
                else:
                    asset["version"] = "*"    
                    max_asset_directory = self.project.path_generate(os.path.dirname(max_template["rig"]), asset)
                    if os.path.exists(max_asset_directory):
                        files = []
                        for l in os.listdir(max_asset_directory):
                            name_fields = self.project.field_generator.get_field_value(os.path.basename(max_template["rig"]), l)
                            if "<take>" in name_fields:
                                files.append("{}/{}".format(max_asset_directory, l))
                            
                        if len(files) > 0:
                            files.sort()
                            asset["max_asset_path"] = files[-1]

                if not asset["max_asset_path"]:
                    errors.append([False, {}, "", u"[error] maxのパスを生成できません: {}".format(asset["namespace"]), max_template["rig"] + "\n" + asset])
                else:
                    data["primary"].setdefault("assets", []).append(asset)
                    data["main"].append(asset)

            if len(no_group_error) > 0:
                QtWidgets.QMessageBox.warning(self, "info", u"assetがgroup化されていません\n{}".format(u"\n".join(no_group_error)), QtWidgets.QMessageBox.Cancel)
                return
            
            asset_group_names = assets_by_groups.keys()
            asset_group_names.sort()
            
            
            if address:
                group_dialog = GroupDialog(self)
                group_dialog.set_ui(item["shot_name"], asset_group_names)
                group_dialog.exec_()

            post_primary = {}
            post_primary["path"] = self.project.path_generate(self.project.config["shot"]["max"]["paths"]["master"], item["fields"])
            post_primary["assets"] = item.get("assets", [])
            data["primary"]["convert_path"] = post_primary["path"]

            post_main = copy.deepcopy(data["main"])

            post_end = {}
            post_end["path"] = post_primary["path"]
            post_end["shot_name"] = item["shot_name"]
            post_end["start"] = item["frame"]["start"]
            post_end["end"] = item["frame"]["end"]
            post_end["fps"] = item["frame"]["fps"]
            post_end["render_scale"] = render_scale
            post_end["movie_path"] = self.project.path_generate(self.project.config["shot"]["max"]["paths"]["master_movie"], item["fields"])

            camera_namespace = self.project.path_generate(self.project.config["asset"]["namespaces"]["camera"], item["fields"])

            post_end["camera"] = "{}:{}".format(camera_namespace, self.project.config["shot"]["camera_name"])


            post_end["groups"] = assets_by_groups.keys()

            data["post_primary"] = post_primary
            data["post_main"] = post_main
            data["post_end"] = post_end
            data["separate_main"] = []
            for k, v in assets_by_groups.items():
                post_end_ = copy.deepcopy(data["post_end"])
                post_end_["name"] = k
                post_end_["assets"] = v
                d, f = os.path.split(post_end_["path"])
                f, ext = os.path.splitext(f)
                post_end_["path"] = "{}/{}_{}{}".format(d, f, k, ext)
                post_end_["filters"] = [each["namespace"] for each in v]
                d, f = os.path.split(post_end_["movie_path"])
                f, ext = os.path.splitext(f)
                post_end_["movie_path"] = "{}/{}_{}{}" .format(d, f, k, ext)

                if address:
                    post_end_["network_rendering"] = True
                    post_end_["job_create"] = group_dialog.widgets[k]["job_create"].checkState() == QtCore.Qt.Checked
                    post_end_["sdw_suspended"] = group_dialog.widgets[k]["sdw_suspended"].checkState() == QtCore.Qt.Checked
                    post_end_["sdw_create"] = group_dialog.widgets[k]["sdw_create"].checkState() == QtCore.Qt.Checked
                else:
                    post_end_["network_rendering"] = False
                    post_end_["job_create"] = False

                if cam_asset:
                    post_end_["assets"].append(cam_asset)
                
                post_end_["split_flg"] = self.ui.split_check.checkState() == QtCore.Qt.Checked
                if address:
                    post_end_["address"] = address
                data["separate_main"].append(post_end_)

            if len(errors) > 0:
                results_all.append([-1, {}, item["shot_name"], item["shot_name"], u"処理開始"])
                results_all.extend(errors)
                results_all.append([-2, {}, "-", "-", u"処理停止しました"])                
                continue

            pass_data, results = self.project.puzzle_play(self.project.tool_config["puzzle"]["mobu_master_export_varidate"], 
                                                          data, 
                                                          logger_name="convert_execute")
            errors_ = []
            for result in results:
                if result[3].startswith("[error]"):
                    errors_.append(result[3])
                elif not result[0]:
                    errors_.append(result[2])
                elif result == "puzzle process stopped":
                    errors_.append(u"[error] 処理が予期せぬエラーで中止しました。")

            if len(errors_) > 0:
                errors.append(item["shot_name"])
                errors.extend(errors_)
                results_all.append([-1, {}, item["shot_name"], item["shot_name"], u"処理開始"])
                results_all.extend(results)
                results_all.append([-2, {}, "-", "-", u"処理停止しました"])

            if len(errors) > 0:
                continue

            pass_data, results = self.project.puzzle_play(self.project.tool_config["puzzle"]["mobu_master_export"], 
                                     data, 
                                     logger_name="convert_execute")
            

            results_all.append([-1, {}, item["shot_name"], item["shot_name"], u"処理開始"])
            results_all.extend(results)

            data_directory = kc_env.get_log_directory("multi", "KcSceneManager", "puzzle")
            data_path = "{}/{}_data.json".format(data_directory, now_time)
            piece_path = "{}/{}_piece.json".format(data_directory, now_time)
            pass_data_path = "{}/{}_pass_data.json".format(data_directory, now_time)
            if not os.path.exists(data_directory):
                os.makedirs(data_directory)

            files = [l for l in os.listdir(data_directory) if l.split("_")[0] != now_time.split("_")[0]]
            for f in files:
                try:
                    os.remove("{}/{}".format(data_directory, f))
                except:
                    pass

            data_ = {"data": data, "info": {}}
            kc_win_file_io.dump_json(data_path, data_)
            try:
                del pass_data["project"]
                pass_data["project_info"] = {"name": self.project.name, "variation": self.project.variation}
            except:
                pass

            pass_data_ = {"data": pass_data, "info": {}}
            kc_win_file_io.dump_json(pass_data_path, pass_data_)

            piece_data = {"data": self.project.tool_config["puzzle"], "info": {}}
            kc_win_file_io.dump_json(piece_path, piece_data)

            convert_app_data = {}
            convert_app_data["data_path"] = data_path
            convert_app_data["piece_path"] = piece_path
            convert_app_data["pass_path"] = pass_data_path
            convert_app_data["log_directory"] = kc_env.get_log_directory("KcSceneManager", "puzzle")
            convert_app_data["message_output"] = kc_env.get_log_directory("KcSceneManager", "message")
            convert_app_data["result"] = "{}/result.json".format(kc_env.get_log_directory("KcSceneManager", "puzzle"))
            convert_app_data["log_name"] = self.NAME
            # if "convert" in orders:
            #     convert_app_data["order"] = orders["convert"]
            results_all.append([-1, {}, u"max処理", u"max処理", ""])

            pass_data, results = self.project.puzzle_play(self.project.tool_config["puzzle"]["convert"], 
                                     {"main": convert_app_data},
                                     logger_name="convert_execute"
                                     )
            if os.path.exists(convert_app_data["result"]):
                js = kc_win_file_io.load_json(convert_app_data["result"])
                results_all.extend(js["data"]["result"])
            
            results_all.append([-2, {}, "-", "-", u"処理しました"])
    

        self.cmd.file_new()
        x = KcResultDialog(self)
        x.set_ui()
        x.append_header_table(results_all)
        x.resize(1200, 600)
        x.exec_()

    def create_master_btn_clicked(self):
        if self.ui.master_check.checkState() == QtCore.Qt.Checked:
            if self.project.tool_config.get("master_export_action", "convert") == "convert":
                self.convert_execute()
            else:
                self.export_execute()
        else:
            self.export_execute(True)

    def export_execute(self, create_master=False):
        """
        create_master: マスターを作成するかどうか == edit to master
        """
        items = [l for l in self.get_shot_table_active_item_data()]
        render_scale = self.get_render_scale()
        results_all = []
        logger_name = "mobu_master_export_logger" if create_master else "mobu_edit_export_logger"
        
        for item in items:
            item_fields = {k: v for (k, v) in copy.deepcopy(item["fields"]).items() if k not in ["project", "project_variation"]}
            errors = []
            data = {"primary": {}, "main": [], "common": {"project": self.project}}
            if create_master:
                data["primary"]["path"] = item["paths"].get(kc_env.mode, {}).get("edit")
            else:
                data["primary"]["path"] = item["paths"].get(kc_env.mode, {}).get("master")

            if not data["primary"]["path"]:
                continue
        
            item_fields["start"] = item["frame"]["start"]
            item_fields["end"] = item["frame"]["end"]

            data["primary"]["start"] = item["frame"]["start"]
            data["primary"]["end"] = item["frame"]["end"]
            data["primary"]["fps"] = item["frame"].get("fps", 24)

            for asset in item.get("assets", []):
                if not asset.get("selection") and asset["category"] != "camera":
                    continue

                asset = copy.deepcopy(asset)
                asset.update(item_fields)

                if asset["category"] in self.project.config["asset"][kc_env.mode]["paths"]:
                    template = self.project.config["asset"][kc_env.mode]["paths"][asset["category"]]
                else:
                    template = self.project.config["asset"][kc_env.mode]["paths"]["default"]

                if not "config" in template:
                    continue

                asset["config"] = {"plot": self.project.path_generate(template["config"].replace("<config_type>", "plot"), asset), 
                                   "export": self.project.path_generate(template["config"].replace("<config_type>", "export"), asset)} 
                if create_master:
                    asset["mobu_edit_export_path"] = self.project.path_generate(template["edit_export"], asset)
                else:
                    asset["mobu_master_export_path"] = self.project.path_generate(template["master_export"], asset)

                
                if asset["category"] == "camera":
                    camera_path = self.project.get_latest_camera_path()
                    cam_fields = self.project.path_split(self.project.config["asset"][kc_env.mode]["paths"]["camera"]["rig"], camera_path)
                    cam_path = self.project.path_generate(self.project.config["asset"][kc_env.mode]["paths"]["camera"]["sotai"], cam_fields)
                    asset["mobu_sotai_path"] = cam_path
                    asset["rig_path"] = self.project.path_generate(self.project.config["asset"][kc_env.mode]["paths"]["camera"]["rig"], cam_fields)

                else:
                    asset["take"] = "*"
                    asset["mobu_sotai_path"] = self.project.path_generate(template["sotai"], asset)
                    """
                        TODO:
                            ハードコード
                    """
                    sotai_paths = glob.glob(asset["mobu_sotai_path"])
                    sotai_paths.sort()
                    if len(sotai_paths) == 0:
                        print("sotai not found: {}".format(asset["namespace"]))
                        continue

                    asset["mobu_sotai_path"] = sotai_paths[-1]
                    asset["sub_category"] = "*"
                    asset["rig_path"] = self.project.path_generate(template["rig"], asset)


                if not asset["mobu_sotai_path"]:
                    errors.append([False, "", u"[error] sotaiのパスを生成できません: {}".format(asset["namespace"]), template["sotai"] + "\n" + asset])
                elif not os.path.exists(asset["mobu_sotai_path"]):
                    errors.append([False, "", u"[error] sotai pathがありません: {}".format(asset["namespace"]), asset["mobu_sotai_path"]])

                data["primary"].setdefault("assets", []).append(asset)
                data["main"].append(asset)

            post_primary = {}
            post_primary["path"] = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["master"], item["fields"])
            post_primary["assets"] = item.get("assets", [])

            post_main = copy.deepcopy(data["main"])

            post_end = {}
            post_end["path"] = post_primary["path"]
            post_end["shot_name"] = item["shot_name"]
            post_end["start"] = item["frame"]["start"]
            post_end["end"] = item["frame"]["end"]
            post_end["fps"] = item["frame"]["fps"]
            post_end["render_scale"] = render_scale
            post_end["movie_path"] = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["master_movie"], item["fields"])
            if not create_master:
                data["primary"]["publish_path"] = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["publish"], item["fields"])
                data["primary"]["publish_movie_path"] = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["publish_movie"], item["fields"])

            data["post_primary"] = post_primary
            data["post_main"] = post_main
            data["post_end"] = post_end

            if len(errors) > 0:
                results_all.append([-1, item["shot_name"], item["shot_name"], u"処理開始"])
                results_all.extend(errors)
                results_all.append([-2, "-", "-", u"処理停止しました"])                
                continue
            
            varidate_name = "mobu_edit_export_varidate" if create_master else "mobu_master_export_varidate"
            pass_data, results = self.project.puzzle_play(self.project.tool_config["puzzle"].get(varidate_name, "mobu_edit_export_varidate"), 
                                                          data, 
                                                          logger_name=logger_name)

            errors_ = []
            for result in results:
                if result[2].startswith("[error]"):
                    errors_.append(result[2])
                elif not result[0] in [0, 2]:
                    errors_.append(result[2])
                elif result == "puzzle process stopped":
                    errors_.append(u"[error] 処理が予期せぬエラーで中止しました。")

            if len(errors_) > 0:
                errors.append(item["shot_name"])
                errors.extend(errors_)
                results_all.append([-1, item["shot_name"], item["shot_name"], u"処理開始"])
                results_all.extend(results)
                results_all.append([-2, "-", "-", u"処理停止しました"])

            if len(errors) > 0:
                continue
            if create_master:
                task_name = "mobu_edit_export"
            else:
                task_name = "mobu_master_export"

            context, results = self.project.puzzle_play(self.project.tool_config["puzzle"][task_name],
                                     data,
                                     logger_name=logger_name)
            
            results_all.append([-1, item["shot_name"], item["shot_name"], u"処理開始"])
            results_all.extend(results)
            results_all.append([-2, "-", "-", u"処理しました"])

        self.cmd.file_new()
        x = KcResultDialog(self)
        x.set_ui()
        x.append_header_table(results_all)
        x.resize(1200, 600)
        x.exec_()


    def get_shot_table_active_item_data(self):
        items = []
        for r in range(self.ui.shot_table.rowCount()):
            check = self.ui.shot_table.cellWidget(r, self.shot_table_list.index("check"))
            item = self.ui.shot_table.item(r, self.shot_table_list.index("name"))
            row_data = copy.deepcopy(item.row_data)
            if not check.is_active:
                continue

            namespace = self.project.path_generate(self.project.config["asset"]["namespaces"]["camera"], 
                                                   row_data["fields"])

            cam_data = {}
            cam_data["namespace"] = namespace
            cam_data["category"] = "camera"

            model = kc_model.find_model_by_name("{}:meta".format(namespace))
            if model:
                cam_data["take"] = model.PropertyList.Find("take").Data

            row_data["assets"].append(cam_data)

            items.append(row_data)

        return items

    def scene_table_changed(self):
        self.connect_signals(False)

        selected_items = [l for l in self.ui.scene_table.selectedItems() if l.column() == self.scene_table_list.index("name")]

        if len(selected_items) == 0:
            self.ui.shot_table.clearContents()
            self.ui.shot_table.setRowCount(0)
            self.ui.asset_table.clearContents()
            self.ui.asset_table.setRowCount(0)
            self.connect_signals(True)
            return

        if len(selected_items) != 1:
            self.connect_signals(True)
            return

        name  = selected_items[0].text()
        self.current_scene_item = selected_items[0]
        self.list_shot_table(name)

        self.connect_signals(True)

    def list_shot_table(self, name):
        def _get_shot_configs(name):
            config_directory = "{}/{}".format(self.project.tool_config["directory"], name)
            try:
                configs = ["{}/{}".format(config_directory, l) for l in os.listdir(config_directory) if l != "config.json" and os.path.isfile("{}/{}".format(config_directory, l))]
            except BaseException:
                configs = []
            configs.sort()
            return configs

        self.ui.shot_table.clearContents()
        self.ui.shot_table.setRowCount(0)
        shot_paths = []
        if name == "all":
            shot_paths = []
            for r in range(self.ui.scene_table.rowCount()):
                item = self.ui.scene_table.item(r, self.scene_table_list.index("name"))
                if item.text() == "all":
                    continue
                shot_paths.extend(_get_shot_configs(item.text()))

        else:
            shot_paths = _get_shot_configs(name)

        for path in shot_paths:
            try:
                js = kc_win_file_io.load_json(path)
            except:
                print(traceback.format_exc())
                continue
            
            current_file_path = self.cmd.get_current_path()
            self.append_shot_table(js["info"], js["data"], path, current_file_path)

    def shot_table_changed(self):
        selected_items = [l for l in self.ui.shot_table.selectedItems() if l.column() == self.shot_table_list.index("name")]
        if len(selected_items) == 0:
            self.ui.asset_table.clearContents()
            self.ui.asset_table.setRowCount(0)
        if len(selected_items) != 1:
            return
        
        self.current_shot_item = selected_items[0]

        self.list_asset_table(self.current_shot_item)



    def list_asset_table(self, item):
        def _merge_assets(config_assets, assets):
            assets = {l["namespace"]: l for l in assets}
            config_assets_dict = {l["namespace"]: l for l in config_assets}

            a = set(assets.keys())
            b = set(config_assets_dict.keys())

            both = a & b
            a_only = a - b
            b_only = b - a

            merge_assets = {}
            add_namespace = []

            scene_assets = []

            for asset in both:
                add = config_assets_dict[asset]
                add["type"] = "both"
                scene_assets.append(add)

            for asset in a_only:
                add = assets[asset]
                add["type"] = "scene"
                scene_assets.append(add)

            for asset in b_only:
                add = config_assets_dict[asset]
                add["type"] = "config"
                scene_assets.append(add)

            scene_assets = sorted(scene_assets, key=lambda x: x["namespace"])

            return scene_assets

        self.ui.asset_table.clearContents()
        self.ui.asset_table.setRowCount(0)

        if item.is_file_opened:
            assets = [l for l in self.project.get_assets() if l["category"] != "camera"] # + self.project.get_cameras()
        else:
            assets = []

        list_assets = _merge_assets(item.row_data.get("assets", []), assets)

        self.append_asset_table(list_assets)


    def shot_table_check_clicked(self):
        self.sender().is_active = not self.sender().is_active

        rows = [l.row() for l in self.ui.shot_table.selectedItems() if hasattr(l, "row")]
        if not self.sender().row() in rows:
            rows = [self.sender().row()]

        for row in rows:
            check = self.ui.shot_table.cellWidget(row, self.shot_table_list.index("check"))
            item = self.ui.shot_table.item(row, self.shot_table_list.index("name"))
            check.is_active = self.sender().is_active
            self.set_icon(check)
            item.row_data["selection"] = self.sender().is_active

            # data = {"data": item.row_data, 
            #         "info": item.info_data}

            # kc_win_file_io.dump_json(item.config_path, data)

            kc_env.save_config(item.config_path, self.NAME, "shot_config", item.row_data)


    def set_icon(self, btn):
        if btn.is_active:
            btn.setIcon(self.on_check_icon)
        else:
            btn.setIcon(self.off_check_icon)

    def set_table(self, widget):
        lst = getattr(self, "{}_list".format(widget.objectName()))
        dic = getattr(self, "{}_dict".format(widget.objectName()))
        widget.setColumnCount(len(lst))
        names = []
        for i, l in enumerate(lst):
            if l in dic:
                if "view" in dic[l]:
                    names.append(dic[l]["view"])
                else:
                    names.append(l)
                
                if "width" in dic[l]:
                    widget.setColumnWidth(i, dic[l]["width"])
            else:
                names.append(l)

        widget.setHorizontalHeaderLabels(names)

    def user_check_clicked(self):
        self.set_filter()

    def set_filter(self):
        user_check = self.ui.user_check.checkState() == QtCore.Qt.Checked
        
        for r in range(self.ui.shot_table.rowCount()):
            item = self.ui.shot_table.item(r, self.shot_table_list.index("user"))
            if user_check:
                if self.is_current_user(item):
                    self.ui.shot_table.setRowHidden(r, False)
                else:
                    self.ui.shot_table.setRowHidden(r, True)
            else:
                self.ui.shot_table.setRowHidden(r, False)

                    
    def is_current_user(self, item):
        if item.text() == self.user:
            return True
        return False

    def open_exist_asset_action_triggered(self):
        items = [l for l in self.ui.exist_asset_table.selectedItems() if l.column() == self.exist_asset_table_list.index("namespace")]
        if len(items) == 0:
            return

        mes = QtWidgets.QMessageBox.information(self, u"info", u"開きますか?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if mes == QtWidgets.QMessageBox.No:
            return 

        kc_file_io.file_open(str(items[0].asset_path))


    def merge_exist_asset_action_triggered(self):
        items = [l for l in self.ui.exist_asset_table.selectedItems() if l.column() == self.exist_asset_table_list.index("namespace")]
        if len(items) == 0:
            return

        namespace = str(items[0].text())
        asset_path = items[0].asset_path
        asset_type = items[0].row_data["<category>"]

        dialog = AssetDialog(self)
        dialog.set_ui(asset_type, namespace, asset_path, self.project)
        dialog.exec_()

    def master_file_open_action_triggered(self):
        if not self.current_shot_item:
            return

        master_path = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["master"], self.current_shot_item.row_data["fields"])
        if not master_path:
            QtWidgets.QMessageBox.warning(self, "info", u"master pathがありません", QtWidgets.QMessageBox.Cancel)
            return 

        self.file_open_action(master_path, self.current_shot_item.text())

    def open_action_triggered(self):
        if not self.current_shot_item:
            return

        path = self.current_shot_item.row_data.get("paths", {}).get(kc_env.mode, {}).get("edit", False)
        if not path:
            QtWidgets.QMessageBox.warning(self, "info", u"edit pathがありません", QtWidgets.QMessageBox.Cancel)
            return 
        
        self.file_open_action(path)


    def file_open_action(self, path, shot_name=None):
        self.connect_signals(False)
        if os.path.lexists(path):
            self.cmd.file_open(path)

            for r in range(self.ui.shot_table.rowCount()):
                item = self.ui.shot_table.item(r, self.shot_table_list.index("name"))
                path_ = item.row_data["paths"][kc_env.mode]["edit"]
                for c in range(self.ui.shot_table.columnCount()):
                    item_ = self.ui.shot_table.item(r, c)
                    if item_:
                        if shot_name:
                            if item_.text() == shot_name:
                                item_.setForeground(self.colors["enabled"])
                                item.is_file_opened = True
                            else:
                                item_.setForeground(self.colors["disabled"])
                                item.is_file_opened = False
                        else:
                            if self.is_same(path, path_):
                                item_.setForeground(self.colors["enabled"])
                                item.is_file_opened = True
                            else:
                                item_.setForeground(self.colors["disabled"])
                                item.is_file_opened = False

            self.list_asset_table(item)

        self.connect_signals(True)

    def append_scene_table(self, data, selection_name):
        if isinstance(data, list):
            for d in data:
                self.append_scene_table(d, selection_name)
        else:
            r = self.ui.scene_table.rowCount()
            self.ui.scene_table.setRowCount(r+1)

            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item.setText(data)
            item.row_data = data

            self.ui.scene_table.setItem(r, self.scene_table_list.index("name"), item)

            if selection_name == data:
                item.setSelected(True)

    def append_shot_table(self, info, data, path, open_path):
        r = self.ui.shot_table.rowCount()
        self.ui.shot_table.setRowCount(r+1)

        check = self.create_check_btn(data.get("selection", False))
        check.clicked.connect(self.shot_table_check_clicked)

        self.ui.shot_table.setCellWidget(r, self.shot_table_list.index("check"), check)

        item = QtWidgets.QTableWidgetItem()
        item.info_data = info
        item.row_data = data
        item.config_path = path

        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        check.row = item.row

        data_ = {}
        for k, v in data["fields"].items():
            data_["<{}>".format(k)] = v
        name = self.project.field_generator.generate(self.project.config["shot"]["name_pattern"], data_) or "untitled"
        item.setText(name)

        item.row_data["shot_name"] = name
        
        master_path = self.project.path_generate(self.project.config["shot"][kc_env.mode]["paths"]["master"], item.row_data["fields"])

        if master_path and os.path.exists(master_path):
            icon_widget = QtWidgets.QLabel()
            icon_widget.setPixmap(self.o_icon)
            icon_widget.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
            self.ui.shot_table.setCellWidget(r, self.shot_table_list.index("master"), icon_widget)
            icon_widget.setToolTip(u"masterがあります")

        self.ui.shot_table.setItem(r, self.shot_table_list.index("name"), item)

        start = QtWidgets.QTableWidgetItem()
        start.setText(str(data["frame"]["start"]))
        self.ui.shot_table.setItem(r, self.shot_table_list.index("start"), start)

        end = QtWidgets.QTableWidgetItem()
        end.setText(str(data["frame"]["end"]))
        self.ui.shot_table.setItem(r, self.shot_table_list.index("end"), end)

        fps = QtWidgets.QTableWidgetItem()
        if "fps" in data["frame"]:
            fps.setText(str(data["frame"]["fps"]))
            self.ui.shot_table.setItem(r, self.shot_table_list.index("fps"), fps)
        
        if self.ui.user_check.checkState() == QtCore.Qt.Checked:
            if not self.is_current_user(item):
                self.ui.shot_table.setRowHidden(r, True)

        path = data.get("paths", {}).get(kc_env.mode, {}).get("edit", False)
        shot_file_fields = self.project.path_split(self.project.config["shot"][kc_env.mode]["paths"]["edit"], path)

        """
        TODO:
            ハードコード
        """
        user_item = QtWidgets.QTableWidgetItem()
        if "<user>" in shot_file_fields:
            user_item.setText(shot_file_fields["<user>"])
        else:
            user_item.setText(info.get("path_name", info.get("user", info["update_by"])))

        user_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        
        self.ui.shot_table.setItem(r, self.shot_table_list.index("user"), user_item)
        time_text = "-"

        item.is_file_opened = False

        if not path:
            color = self.colors["disabled"]
        elif not os.path.lexists(path):
            color = QtGui.QColor(200, 70, 70)
        else:
            time_text = self.cmd.get_file_time(path)
            if os.path.normpath(path.lower().replace("\\", "/")) == os.path.normpath(open_path.lower().replace("\\", "/")):
                color = self.colors["enabled"]
                item.is_file_opened = True
            else:
                color = self.colors["disabled"]

        time_item = QtWidgets.QTableWidgetItem()
        time_item.setText(time_text)

        time_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.ui.shot_table.setItem(r, self.shot_table_list.index("time"), time_item)

        for c in range(self.ui.shot_table.columnCount()):
            item_ = self.ui.shot_table.item(r, c)
            if item_:
                item_.setForeground(color)
                item_.setTextAlignment(QtCore.Qt.AlignCenter)

    def append_asset_table(self, data):
        if isinstance(data, list):
            for d in data:
                self.append_asset_table(d)
        else:
            r = self.ui.asset_table.rowCount()
            self.ui.asset_table.setRowCount(r+1)
            check = self.create_check_btn(data.get("selection", False))
            check.clicked.connect(self.asset_table_check_clicked)

            check.row_data = data

            self.ui.asset_table.setCellWidget(r, self.asset_table_list.index("check"), check)

            item = QtWidgets.QTableWidgetItem()

            check.row = item.row
            self.ui.asset_table.setItem(r, self.asset_table_list.index("name"), item)

            item.setText(data["namespace"])
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

            
            group_item = QtWidgets.QTableWidgetItem()
            if "comp" in data:
                if "group_name" in data["comp"]:
                    group_item.setText(data["comp"]["group_name"])
            
            self.ui.asset_table.setItem(r, self.asset_table_list.index("group"), group_item)
            group_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            group_item.setTextAlignment(QtCore.Qt.AlignCenter)

            if not self.current_shot_item.is_file_opened:
                item.setForeground(QtGui.QColor(120, 120, 120))    
                group_item.setForeground(QtGui.QColor(120, 120, 120))    

            else:
                info = self.asset_table_state[data["type"]]
                item.setForeground(info["color"])
                item.setToolTip(info["tooltip"])

                group_item.setForeground(info["color"])
                # check.is_active = info["state"]
            # self.set_icon(check)
            item.row_data = data

    def asset_table_check_clicked(self):
        self.sender().is_active = not self.sender().is_active
        self.set_icon(self.sender())

        item = self.ui.asset_table.item(self.sender().row(), self.asset_table_list.index("name"))

        namespace = self.sender().row_data["namespace"]

        assets = self.current_shot_item.row_data.get("assets", [])
        rem = False
        for i, asset in enumerate(assets):
            if asset["namespace"] == namespace:
                asset["selection"] = self.sender().is_active
                rem = True
                if asset["selection"]:
                    info = self.asset_table_state["both"]
                else:
                    info = self.asset_table_state["scene"]
                item.setForeground(info["color"])
                item.setToolTip(info["tooltip"])
                break

        if not rem:
            self.sender().row_data["selection"] = self.sender().is_active
            assets.append(self.sender().row_data)
            info = self.asset_table_state["both"]
            item.setForeground(info["color"])
            item.setToolTip(info["tooltip"])
        # data = {"data": self.current_shot_item.row_data, 
        #         "info": self.current_shot_item.info_data}
        kc_env.save_config(self.current_shot_item.config_path, self.NAME, "shot_config", self.current_shot_item.row_data)

        # kc_win_file_io.dump_json(self.current_shot_item.config_path, self.current_shot_item.row_data)


    def create_check_btn(self, flg):
        btn = QtWidgets.QPushButton()
        btn.is_active = flg
        self.set_icon(btn)
        btn.setIconSize(QtCore.QSize(20, 20))
        btn.setMaximumWidth(20)
        btn.setMinimumWidth(20)
        btn.setMaximumHeight(20)
        btn.setMinimumHeight(20)
        btn.setFlat(True)
        return btn

    def get_max_count(self, root, lst):
        _max = -1
        return -1
        for l in lst:
            name = [s for s in l.replace(root, "").split("/") if s != ""]
            if len(name) > _max:
                _max = len(name)
        #if _max != -1:
        #    _max + 3
        return _max

    def create_tree(self, root, pattern=False):
        lst = []
        lst = [os.path.normpath(l).replace("\\", "/") for l in lst if os.path.lexists(l)]
        self.ui.directory_tree.clear()
        
        c_item = QtWidgets.QTreeWidgetItem(self.ui.directory_tree, 1)
        c_item.setText(0, root)

        c_item.is_root = True
        c_item.setExpanded(True)

        self.root = root.replace("\\", "/")
        self.expand_list = []
        self.ui.directory_tree.setColumnCount(1)
        _max_count = self.get_max_count(root, lst)

        # self.expand_list.append(self.root)
        widget_list = []
        if not os.path.exists(self.root):
            return

        for f in os.listdir(self.root):
            self.walk_tree(self.root, "%s/%s" % (self.root, f), lst, widget_list, deep=_max_count, parent=c_item, pattern=pattern)

        self.reload_tree_flag = True

    def walk_tree(self, root, path, lst, widget_list, deep=-1, parent=False, pattern=False):
        """
        自作os.walk
        """
        check = [l for l in path.replace("\\", "/").replace(root, "").split("/") if l != ""]
        if deep != -1 and len(check) > deep:
            return
        if path.replace("\\", "/").startswith("//"):
            serv = True
        else:
            serv =False
        _dir = "/".join([l for l in path.replace("\\", "/").split("/") if l != ""][:-1])
        if serv:
            _dir = "//%s" % _dir
        _file = check[-1]
        path = "%s/%s" % (_dir, _file)
        if _file[0] in ["."]:
            return

        if "/master" in path or "/Master" in path or "_old" in path or "movie_convert" in path or "mov_edit" in path:
            return

        if os.path.basename(path) in self.ignore:
            return

        if not os.path.exists(path):
            pass 
    
        
        elif os.path.isdir(path):
            if path.endswith(".fbm") or path.endswith(".bck"):
                return
            if parent:
                c_item = QtWidgets.QTreeWidgetItem(parent, 1)
            else:
                c_item = QtWidgets.QTreeWidgetItem(self, 1)

            c_item.setText(0, _file)
            c_item.is_root = False
            c_item.setIcon(0, self.on_check_icon)
            c_item.full_path = path
            c_item.setIcon(0, QtGui.QIcon(""))

            self.expand_list.append(path)
            c_item.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ShowIndicator)

            for child in os.listdir(path):
                self.walk_tree(root, "%s/%s" % (path, child), lst, widget_list, deep, c_item, pattern)

        else:
            if parent:
                c_item = QtWidgets.QTreeWidgetItem(parent, 1)
            else:
                c_item = QtWidgets.QTreeWidgetItem(self, 1)
            self.expand_list.append(path)

            c_item.full_path = path
            c_item.is_root = False
            c_item.setText(0, _file)

            pat_flg = False
            if pattern:
                if path.lower().replace("\\", "/").find(pattern.lower().replace("\\", "/")) != -1:
                    widget_list.append(c_item)
                    pat_flg = True

            if path.replace("\\", "/").lower() in [x.replace("\\", "/").lower() for x in lst] and pat_flg == False:
                widget_list.append(c_item)

    def set_tree_icon(self, item, flg):
        if flg:
            self.item.setIcon(self.tree_icon)
        else:
            self.item.setIcon(self.blank_icon)


    def get_category_assets(self):
        self.category_assets = {}
        for k, v in self.project.config["asset"].get(kc_env.mode, {}).items():
            for k2, v2 in v.items():
                base_path = self.project.path_generate(v2["rig"], {}, force=True)
                keys = self.project.field_generator.get_field_keys(base_path)
                path = base_path

                for key in keys:
                    path = path.replace(key, "*")
                for f in glob.glob(path):
                    f = f.replace("\\", "/")
                    if "/_old" in f:
                        continue
                    fields = self.project.path_split(base_path, f)
                    if fields:
                        if not "<category>" in fields:
                            continue
                        if not fields["<category>"] in self.project.config["asset"]["category"]:
                            continue
                        self.category_assets.setdefault(fields["<category>"], {})
                        if fields["<category>"] in self.project.config["asset"]["namespaces"]:
                            namespace = self.project.config["asset"]["namespaces"][fields["<category>"]]
                        else:
                            namespace = self.project.config["asset"]["namespaces"]["default"]
                        if fields["<category>"] == "camera":
                            fields["<scene>"] = "00"
                            fields["<cut>"] = "0000"

                        fields["<namespace>"] = self.project.field_generator.generate(namespace, fields)
                        fields["<path>"] = f

                        if fields["<category>"] == "camera":
                            self.category_assets["camera"].setdefault("camera", []).append(fields)
                        else:
                            self.category_assets[fields["<category>"]].setdefault(fields["<asset_name>"], []).append(fields)

class KcSceneManagerCmd(object):
    def __init__(self):
        pass

    def file_new(self):
        kc_file_io.file_new()

    def get_current_path(self):
        return kc_file_io.get_file_path()

    def file_open(self, path):
        kc_file_io.file_open(str(path))

    def file_save(self, path):
        kc_file_io.file_save(str(path))

    def get_file_time(self, path):
        try:
            file_meta = time.localtime(os.stat(path).st_mtime)
            return "%04d/%02d/%02d %02d:%02d" % (file_meta[0], file_meta[1], file_meta[2], file_meta[3], file_meta[4])    
        except:
            return "-"

    def get_config_path(self, asset_path, namespace, config_type):
        d, f = os.path.split(asset_path)
        path = "{}/config/{}_{}.json".format(d, namespace, config_type)
        if os.path.exists(path):
            return path
        return False

    def select_from_config(self, path):
        js = kc_win_file_io.load_json(path)
        data = [str("{}:{}".format(l["namespace"], l["name"])) for l in js["data"]]
        kc_model.select(data)
    

def start_app():
    kc_qt.start_app(KcSceneManager, name="KcSceneManager", x=1200, y=500, root=kc_qt.get_root_window())

if __name__ in ["__builtin__", "__main__", "builtins"]:
    def test_ui():
        FBApplication().FileNew()
        path = "H:/works/keica/data/BlendShapeSlider/aoi_05__.fbx"
        FBApplication().FileOpen(path)

        start_app()
    start_app()

