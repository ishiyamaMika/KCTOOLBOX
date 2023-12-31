# -*- coding: utf8 -*-

import os
import sys
import re
import importlib
import glob
import datetime

try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import *

import KcLibs.mobu.kc_file_io as kc_file_io
import KcLibs.mobu.kc_model as kc_model
import KcLibs.win.kc_qt as kc_qt

from KcLibs.win.kc_qt import QtWidgets, QtCore, QtGui

from puzzle2.PzTask import PzTask

from PySide2 import QtWidgets

kc_env.append_sys_paths()

from pyfbsdk import *

class CompleterLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(CompleterLineEdit, self).__init__(parent)
        self.setFrame(False)

    def set(self, names):
        model = QtGui.QStandardItemModel()
        for name in names:
            item = QtGui.QStandardItem(name)
            model.setItem(model.rowCount(), 0, item)
        completer = QtWidgets.QCompleter(self)
        completer.setModel(model)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(completer)

class KcSetupper(QtWidgets.QWidget):
    NAME = "KcSetupper"
    VERSION = "1.2.1"

    def __init__(self, parent=None):
        super(KcSetupper, self).__init__(parent)
        self.tool_directory = kc_env.get_tool_config("mobu", self.NAME)
        self.project = KcProject()
        self.preset_value_widgets = {}
        self.cmd = KcSetupperCmd()
        self.cmd.project = self.project
        self.user_config_path = "{}/user_config.json".format(kc_env.get_user_config("mobu", "KcSetupper"))
        self.user_config_schema = {
            "project": "", 
            "variation": ""
        }

        info, self.user_config = kc_env.load_config(self.user_config_path, self.user_config_schema)

        self.asset_config_schema = {
            "project": "",
            "variation": "",
            "asset_name": ""
        }

    def update_user_config(self):
        override_data = {}
        override_data["project"] = self.project_combo.currentText()
        override_data["variation"] = self.variation_combo.currentText()
        
        self.project.sticky.values_override(self.user_config, override_data, use_field_value=False)

        self.user_config.update(override_data)
        print(self.user_config)

        kc_env.save_config(self.user_config_path, self.NAME, "user", self.user_config)

    def update_asset_config(self):
        data = self.get_data()
        path = kc_file_io.get_file_path()
        if path == "":
            return

        d, f = os.path.split(path)
        config_path = "{}/config/setting_{}.json".format(d, data["namespace"])

        kc_env.save_config(config_path, self.NAME, "asset", data)

    def set_ui(self):
        top_layout = QtWidgets.QVBoxLayout()

        doc_btn = QtWidgets.QPushButton()
        doc_btn.setMaximumHeight(24)
        doc_btn.setMinimumHeight(24)
        doc_btn.setMaximumWidth(24)
        doc_btn.setMinimumWidth(24)

        hlayout = QtWidgets.QHBoxLayout()
        self.project_combo = QtWidgets.QComboBox()
        self.project_combo.addItems(self.project.project_variations.keys())


        self.variation_combo = QtWidgets.QComboBox()

        hlayout.addWidget(self.project_combo)
        hlayout.addWidget(self.variation_combo)

        project = self.project_combo.currentText()
        variations = self.project.project_variations[project]

        reload_btn = QtWidgets.QPushButton()
        hlayout.addWidget(reload_btn)
        # hlayout.addWidget(doc_btn)

        hlayout.setSpacing(4)

        top_layout.addLayout(hlayout)

        self.layout = QtWidgets.QVBoxLayout()
        top_layout.addLayout(self.layout)

        reload_btn.clicked.connect(self.reload)
        reload_btn.setText("reload")

        spacer = QtWidgets.QSpacerItem(30, 
                                       20, 
                                       QtWidgets.QSizePolicy.Expanding, 
                                       QtWidgets.QSizePolicy.Expanding)
        top_layout.addItem(spacer)
  
        self.setLayout(top_layout)

        self.show()

        self.project_combo_changed()
        print(self.user_config)
        if self.user_config.get("variation"):
            index = self.project_combo.findText(self.user_config["variation"])
            if index != -1:
                self.variation_combo.setCurrentIndex(index)

        self.project_combo.currentIndexChanged.connect(self.project_combo_changed)

    def project_combo_changed(self):
        proj = self.project_combo.currentText()
        variations = self.project.project_variations[proj]
        self.variation_combo.clear()
        self.variation_combo.addItems(variations)

    def get_settings(self):
        path = kc_file_io.get_file_path()
        fields = {}
        settings = []
        if path:
            d, f = os.path.split(path)
            for k, v in self.project.config["asset"]["mobu"]["paths"].items():
                rig = self.project.config["asset"]["mobu"]["paths"][k].get("rig", "")
                fields = self.project.path_split(os.path.dirname(rig), d)
                if fields:
                    break
    
            setting_path = "{}/config/setting_*.json".format(d)
            for path in glob.glob(setting_path):
                search = re.search(setting_path.replace("*", "(.*)").replace("\\", "/"), path.replace("\\", "/"))
                if search:
                    settings.append(search.groups()[0])

        if "<asset_name>" in fields:
            asset_name = fields["<asset_name>"]
        else:
            d, f = os.path.split(path)
            f, ext = os.path.splitext(f)
            asset_name = f
        
        return asset_name, settings

    def reload(self):
        for i in range(self.layout.count())[::-1]:
            self.layout.takeAt(i)

        self.project.set(self.project_combo.currentText(), 
                         self.variation_combo.currentText()
                        )
        self.project.set_tool_config("mobu", self.NAME)

        asset_name, settings = self.get_settings()

        hlayout = QtWidgets.QHBoxLayout()
        text = QtWidgets.QLabel("asset name")
        widget = CompleterLineEdit()
        widget.set(settings)

        widget.editingFinished.connect(self.asset_name_changed)

        hlayout.addWidget(text)
        hlayout.addWidget(widget)
        self.layout.addLayout(hlayout)

        self.preset_value_widgets["asset_name"] = {"widget": widget, "type": "QLineEdit"}

        for preset in self.project.tool_config.get("preset", []):
            btn = QtWidgets.QPushButton()
            btn.setText(preset.get("view", preset["name"]))

            btn.row_data = preset

            if "widgets" in preset:
                for widget_set in preset["widgets"]:
                    hlayout = QtWidgets.QHBoxLayout()
                    view = widget_set.get("view", widget_set["name"])
                    text = QtWidgets.QLabel(widget_set["name"])

                    text.setText(view)

                    value = False
                    if "widget" not in widget_set:
                        self.layout.addWidget(text)
                        continue

                    text.setMinimumWidth(200)
                    text.setMaximumWidth(200)
                    widget = getattr(QtWidgets, widget_set["widget"])()
                    widget.setObjectName(widget_set["name"])
                    if "place_holder" in widget_set:
                        widget.setPlaceholderText(widget_set["place_holder"])

                    filters = [l for l in widget_set.keys() if l.endswith("filter")]
                    for filter_ in filters:
                        setattr(widget, filter_, widget_set[filter_])

                    hlayout.addWidget(text)
                    hlayout.addWidget(widget)
                    if "btn" in widget_set:
                        btn_ = QtWidgets.QPushButton()
                        btn_.setIcon(QtGui.QIcon("{}/form/icon/{}".format(self.tool_directory, widget_set["btn"]["icon"])))
                        btn_.setIconSize(QtCore.QSize(18, 18))
                        btn_.setMinimumWidth(18)
                        btn_.setMaximumWidth(18)
                        btn_.setMinimumHeight(18)
                        btn_.setMaximumHeight(18)                        
                        btn_.setFlat(True)
                        btn_.combo = widget
                        btn_.row_data = widget_set
                        btn_.clicked.connect(getattr(self, widget_set["btn"]["function"]))
                        getattr(self, widget_set["btn"]["init"])(btn_)
                        hlayout.addWidget(btn_)
                    hlayout.setMargin(0)
                    hlayout.setSpacing(2)
                    self.layout.addLayout(hlayout)

                    if widget_set["widget"] == "QComboBox":
                        widget.addItems(widget_set.get("items", []))
                        if "function" in widget_set:
                            widget.currentIndexChanged.connect(getattr(self, widget_set["function"]))

                    if value:
                        if widget_set["widget"] in ["QSpinBox", "QDoubleSpinBox"]:
                            widget.setValue(value)
                        elif widget_set["widget"] == "QComboBox":
                            widget.setCurrentIndex(widget.findText(value))
                        else:
                            widget.setText(value)

                    if "enabled" in widget_set:
                        widget.setEnabled(widget_set["enabled"])
                    self.preset_value_widgets[widget_set["name"]] = {"widget": widget, 
                                                                     "type": widget_set["widget"]}
            if "function" in preset:
                btn.clicked.connect(getattr(self, preset["function"]))
            else:
                btn.clicked.connect(self.btn_clicked)

            self.layout.addWidget(btn)

        spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.layout.addSpacerItem(spacer)
        self.update_from_settings(asset_name)

    def filter_combo_changed(self):
        combo_name = self.sender().objectName()
        for name, widget in self.preset_value_widgets.items():
            if hasattr(widget["widget"], "{}_filter".format(combo_name)):
                if self.sender().currentText() in getattr(widget["widget"], "{}_filter".format(combo_name)):
                    widget["widget"].setEnabled(True)
                else:
                    widget["widget"].setEnabled(False)

    def asset_name_changed(self):
        wid = self.sender()
        wid.editingFinished.disconnect(self.asset_name_changed)
        name = wid.text()
        self.update_from_settings(name)
        wid.setText(name)

        wid.editingFinished.connect(self.asset_name_changed)

    def update_from_settings(self, name):
        path = kc_file_io.get_file_path()
        if not path:
            return "", []

        d, f = os.path.split(path)
        take = 1
        version = 1

        match = re.match(".*_t([0-9]*).*", f)
        if match:
            take_ = match.groups()[0]
            if take_.isdigit():
                take = int(take_)
            version = 1

        match = re.match(".*_t([0-9]*)_([0-9]*).*", f)
        if match:
            take, version = [int(l) for l in match.groups()]
            version += 1

        #name = unicode(self.sender().text())
        setting_path = "{}/config/setting_{}.json".format(d, name)
        data = {"properties": {}}
        if os.path.exists(setting_path):
            info, data = kc_env.load_config(setting_path)

        else:
            data["properties"].update(self.cmd.get_meta())

        data["properties"]["take"] = take
        data["properties"]["version"] = version
        for k, v in data["properties"].items():
            if k in self.preset_value_widgets:
                widget = self.preset_value_widgets[k]["widget"]
                if isinstance(widget, QtWidgets.QLineEdit):
                    widget.setText(v)

                elif isinstance(widget, QtWidgets.QComboBox):
                    index = widget.findText(v)
                    for i in range(widget.count()):
                        print(widget.itemText(i), widget.itemText(i) == v)
                    if index != -1:
                        widget.setCurrentIndex(index)

                elif isinstance(widget, QtWidgets.QSpinBox):
                    widget.setValue(v)

    def get_groups(self, widget):
        if widget is None:
            return

        if not widget:
            return

        widget.combo.clear()
        groups = self.cmd.get_groups()
        widget.combo.addItems(groups)
        f = ""
        for group in groups:
            if isinstance(widget.row_data["btn"]["find"], list):
                for g in widget.row_data["btn"]["find"]:
                    if g in group:
                        f = group
                        break
            else:
                if widget.row_data["btn"]["find"] in group:
                    f = group
                    break

        index = widget.combo.findText(f)
        if index == -1:
            index = 0

        widget.combo.setCurrentIndex(index)

    def get_default(self):
        pass

    def get_data(self):
        data = {}
        data["asset_name"] = str(self.preset_value_widgets["asset_name"]["widget"].text())
        if data["asset_name"] == "":
            QtWidgets.QMessageBox.warning(self, "info", u"asset名が空です", QtWidgets.QMessageBox.Cancel)
            return 

        data["meta"] = self.project.config["asset"]["meta"]
        data["properties"] = {}
        category = False
        for k, v in self.preset_value_widgets.items():
            if v["type"] in ["QSpinBox", "QDoubleSpinBox"]:
                value = v["widget"].value()
            elif v["type"] == "QComboBox":
                value = str(v["widget"].currentText())
            else:
                value = str(v["widget"].text())
            # data[k] = value
            data["properties"][k] = value
            if k == "category":
                category = value

        if category:
            namespace_pattern = self.project.config["asset"]["namespaces"]
            if not category in namespace_pattern:
                pattern = namespace_pattern["default"]
            else:
                pattern = namespace_pattern[category]
            fields = {}
            for k, v in data["properties"].items():
                if isinstance(v, list):
                    continue
                elif isinstance(v, dict):
                    continue
                else:
                    fields["<{}>".format(k)] = v
           
            if category == "camera":
                fields["<scene>"] = "00"
                fields["<cut>"] = "000"
            namespace = self.project.path_generate(pattern, fields)
        else:
            return False

        data["properties"]["namespace"] = namespace
        data["namespace"] = namespace

        paths = self.project.config["asset"][kc_env.mode]["paths"]
        if category in paths:
            rig_path = paths[category]["rig"]
            sotai_path = paths[category]["sotai"]
            config_path = paths[category]["config"]
        else:
            rig_path = paths["default"]["rig"]
            sotai_path = paths["default"]["sotai"]
            config_path = paths["default"]["config"]

        data["rig_path"] = self.project.path_generate(rig_path, data["properties"])
        data["sotai_path"] = self.project.path_generate(sotai_path, data["properties"])
        print(111, config_path)
        print(222, data["properties"])
        data["config_path"] = self.project.path_generate(config_path, data["properties"], force=True)
        print(data["config_path"], "---------------------------")
        return data

    def set_group_btn_clicked(self):
        self.get_groups(self.sender())

    def btn_clicked(self):
        self.execute(self.sender())

    def save_btn_clicked(self):
        self.cmd.update_meta_date()
        self.execute(self.sender())
        self.update_asset_config()

    def execute(self, widget):
        data = self.get_data()
        if not data:
            return

        piece_data = widget.row_data
        mod = importlib.import_module(piece_data["module"])
        reload(mod)
        # data.update(piece_data)
        # response = mod.main({"data": data})
        task = PzTask(module=mod, task=piece_data, data=data)
        response = task.execute()
        
        flg = response["return_code"] == 0
        # flg, pass_data, header, detail = mod.execute()
        if not flg:
            QtWidgets.QMessageBox.information(self, u"info", u"実行できませんでした\n{}".format(piece_data["view"]), QtWidgets.QMessageBox.Ok)
        else:
            self.update_user_config()
            QtWidgets.QMessageBox.information(self, u"info", u"実行しました\n{}".format(piece_data["view"]), QtWidgets.QMessageBox.Ok)

    def keyPressEvent(self, event):
        pass

class KcSetupperCmd(object):
    def __init__(self):
        pass

    def get_meta(self):
        meta = {}
        metas = self.project.get_assets()
        if len(metas) > 0:
            meta = metas[0]
            if "version" in meta:
                meta["version"] += 1

        return meta

    def get_groups(self):
        return [l.LongName for l in FBSystem().Scene.Groups]

    def update_meta_date(self):
        model = kc_model.find_model_by_name("meta", ignore_namespace=True)
        if model:
            update_at = model.PropertyList.Find("update_at")
            update_by = model.PropertyList.Find("update_by")
            if update_at:
                now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                update_at.Data = now

            if update_by:
                update_by.Data = kc_env.get_user()

def start_app():
    kc_qt.start_app(KcSetupper, name="KcSetupper", x=400, y=500)

if __name__ in ["__builtin__", "builtins"]:
    def test_ui():
        FBApplication().FileNew()
        path = "H:/works/keica/data/BlendShapeSlider/aoi_05__.fbx"
        FBApplication().FileOpen(path)
        start_app()    

    start_app()


