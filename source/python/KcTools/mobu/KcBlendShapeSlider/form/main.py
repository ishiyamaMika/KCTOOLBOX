# -*- coding: utf8 -*-

import os
import sys
import json
import copy
import re
import traceback

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
import KcLibs.win.kc_qt as kc_qt
from KcLibs.win.kc_qt import QtWidgets, QtCore, QtGui

import KcLibs.mobu.kc_key as kc_key
import KcLibs.mobu.kc_model as kc_model
from KcLibs.mobu.kc_Relation import kcRelation

kc_env.append_sys_paths()
reload(kc_qt)

from pyfbsdk import *

class ColorDialog(QtWidgets.QDialog):
    color_set = QtCore.Signal(dict)
    def __init__(self, parent=None):
        super(ColorDialog, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        hlayout = QtWidgets.QHBoxLayout()
        self.r_spin = QtWidgets.QSpinBox()
        self.g_spin = QtWidgets.QSpinBox()
        self.b_spin = QtWidgets.QSpinBox()
        self.r_spin.setMinimum(0)
        self.g_spin.setMinimum(0)
        self.b_spin.setMinimum(0)

        self.r_spin.setMaximum(255)
        self.g_spin.setMaximum(255)
        self.b_spin.setMaximum(255)

        hlayout.addWidget(self.r_spin)
        hlayout.addWidget(self.g_spin)
        hlayout.addWidget(self.b_spin)

        set_btn = QtWidgets.QPushButton()
        set_btn.clicked.connect(self.set_btn_clicked)
        set_btn.setText("set")

        self.label = QtWidgets.QLabel()
        self.r_spin.valueChanged.connect(self.value_changed)
        self.g_spin.valueChanged.connect(self.value_changed)
        self.b_spin.valueChanged.connect(self.value_changed)
        layout.addLayout(hlayout)
        layout.addWidget(self.label)
        layout.addWidget(set_btn)
        layout.setSpacing(2)
        self.setLayout(layout)

    def set_color(self, color):
        self.r_spin.setValue(color[0])
        self.g_spin.setValue(color[1])
        self.b_spin.setValue(color[2])

    def value_changed(self):
        rgb = [self.r_spin.value(), self.g_spin.value(), self.b_spin.value()]
        color = u"background-color: rgb({}, {}, {})".format(*rgb)
        
        self.label.setStyleSheet(color)

    def set_btn_clicked(self):
        color = [self.r_spin.value(), self.g_spin.value(), self.b_spin.value()]
        dic = {"color": color, "btn": self.btn}
        self.color_set.emit(dic)
        self.close()


class KcBlendShapeSlider(QtWidgets.QWidget):
    NAME = "KcBlendShapeSlider"
    VER = 2.0

    def __init__(self, parent=None):
        super(KcBlendShapeSlider, self).__init__(parent)
        self.tool_directory = kc_env.get_tool_config("mobu", self.NAME)
        self.shapes_table_list = ["name"]
        self.shapes_table_dict = {}
        self.groups_table_list = ["check", "color", "name"]
        self.groups_table_dict = {"check": {"view": "", "width": 20}, "color": {"view": "", "width": 20}}
        self.create_table_list = ["center", "name"]
        self.create_table_dict = {"center": {"view": "", "width": 20}}
        self.current_groups_item = False
        self.cmd = KcBlendShapeSliderCmd()
        self.search = "(.*) < (.*)"
        self.pattern = self.search.replace("(.*)", "{}")

    def set_ui(self):
        self.current_path = self.cmd.get_scene_name()
        ui_path = "{}/form/ui/main.ui".format(self.tool_directory)
        self.ui = kc_qt.load_ui(ui_path, self)
        self.set_table(self.ui.groups_table)
        self.set_table(self.ui.shapes_table)
        self.set_table(self.ui.create_table)
        self.ui.create_table.verticalHeader().setMovable(True)
        self.set_shapes()
        self.ui.const_combo.lineEdit().setPlaceholderText(u"constraint名")
        consts = self.cmd.get_constraint_names()
        consts.insert(0, "")
        self.ui.const_combo.addItems(consts)
        path = "{}/_info/tools/KcBlendShapeSlider.json".format(os.path.dirname(self.cmd.get_scene_name()))
        self.import_from_file(path)

        self.ui.reload_btn.setText("")
        self.ui.reload_btn.setIcon(QtGui.QIcon("{}/form/icon/reload.png".format(self.tool_directory)))
        self.ui.reload_btn.setIconSize(QtCore.QSize(24, 24))
        self.ui.reload_btn.setFlat(True)

        self.ui.clear_btn.setText("")
        self.ui.clear_btn.setIcon(QtGui.QIcon("{}/form/icon/trash.png".format(self.tool_directory)))
        self.ui.clear_btn.setIconSize(QtCore.QSize(24, 24))
        self.ui.clear_btn.setFlat(True)
        self.ui.reload_btn.setFocus()
        self.connect_signals(True)

    def connect_signals(self, flg): 
        if flg:
            self.ui.groups_add_btn.clicked.connect(self.groups_add_btn_clicked)
            self.ui.groups_rem_btn.clicked.connect(self.groups_rem_btn_clicked)

            self.ui.clear_btn.clicked.connect(self.clear_btn_clicked)
            self.ui.groups_table.currentCellChanged.connect(self.groups_table_index_changed)
            self.ui.add_btn.clicked.connect(self.add_btn_clicked)
            self.ui.rem_btn.clicked.connect(self.rem_btn_clicked)
            self.ui.import_btn.clicked.connect(self.import_btn_clicked)
            self.ui.export_btn.clicked.connect(self.export_btn_clicked)
            self.ui.reload_btn.clicked.connect(self.reload_btn_clicked)
            self.ui.save_btn.clicked.connect(self.save_btn_clicked)
            self.ui.shapes_table.cellDoubleClicked.connect(self.add_btn_clicked)
            self.ui.create_table.cellDoubleClicked.connect(self.rem_btn_clicked)
            self.ui.group_line.returnPressed.connect(self.group_line_pressed)
            self.ui.create_btn.clicked.connect(self.create_btn_clicked)
            self.ui.shapes_filter_line.returnPressed.connect(self.shapes_filter_line_entered)
        else:
            self.ui.groups_add_btn.clicked.disconnect(self.groups_add_btn_clicked) 
            self.ui.clear_btn.clicked.disconnect(self.clear_btn_clicked)            
            self.ui.groups_table.currentCellChanged.disconnect(self.groups_table_index_changed)
            self.ui.rem_btn.clicked.disconnect(self.rem_btn_clicked)
            self.ui.add_btn.clicked.disconnect(self.add_btn_clicked)
            self.ui.shapes_table.cellDoubleClicked.disconnect(self.add_btn_clicked)
            self.ui.create_table.cellDoubleClicked.disconnect(self.rem_btn_clicked)
            self.ui.group_line.returnPressed.disconnect(self.group_line_pressed)
            self.ui.create_btn.clicked.disconnect(self.create_btn_clicked)
            self.ui.shapes_filter_line.returnPressed.disconnect(self.shapes_filter_line_entered)
            self.ui.import_btn.clicked.disconnect(self.import_btn_clicked)
            self.ui.export_btn.clicked.disconnect(self.export_btn_clicked)
            self.ui.save_btn.clicked.disconnect(self.save_btn_clicked)
            self.ui.reload_btn.clicked.disconnect(self.reload_btn_clicked)

    def clear_btn_clicked(self):
        self.clear_ui()

    def shapes_filter_line_entered(self):
        text = unicode(self.sender().text())
        for r in range(self.ui.shapes_table.rowCount()):
            item = self.ui.shapes_table.item(r, self.get_shapes_table_index("name"))
            if item.is_out:
                continue

            item_text = unicode(item.text())
            if re.search(text, item_text, re.IGNORECASE):
                self.ui.shapes_table.setRowHidden(r, False)
            else:
                self.ui.shapes_table.setRowHidden(r, True)

    def group_line_pressed(self):
        self.groups_add_btn_clicked()

    def get_row_(self, table, name):
        for r in range(table.rowCount()):
            item = table.item(r, self.get_table_index(table, "name"))
            if unicode(item.text()) == name:
                return r
        return -1

    def import_from_file(self, path, namespace=None):
        if not os.path.exists(path):
            return
        try:
            js = json.load(open(path, "r"), "utf8")
        except:
            print "load file failed: {}".format(path)
            return
        info, datas = js["info"], js["data"]
        ver = info.get("ver", 1.0)
        if ver < 2.0:
            print "config version 2.0　or higher is required. (current: {})".format(ver)
            return

        if namespace:
            datas = self.cmd.update_config(namespace, datas)
        else:
            self.set_shapes()
        for data in datas:
            name = data.pop("name")
            self.append_groups_table(name, **data)

        self.reload()

    def import_btn_clicked(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "info", u"イメージのパス")
        if file_path[0] == "":
            return

        namespace = self.cmd.get_scene_namespace()
        if namespace:
            text, ok = QtWidgets.QInputDialog.getText(self, 
                                                      "info", 
                                                      "replace namespace? {}".format(namespace), 
                                                      QtWidgets.QLineEdit.Normal, namespace)
            if ok:
                namespace = text

        self.clear_ui()
        self.import_from_file(file_path[0], namespace)
        QMessageBox.information(self, "info", u"インポートしました", QMessageBox.Ok)

    def clear_ui(self):
        self.ui.create_table.clearContents()
        self.ui.create_table.setRowCount(0)
        self.ui.shapes_table.clearContents()
        self.ui.shapes_table.setRowCount(0)
        self.ui.groups_table.clearContents()
        self.ui.groups_table.setRowCount(0)
        

    def export_btn_clicked(self):
        file_path = QtWidgets.QFileDialog.getSaveFileName(self,"export file", "", "*.json")
        if file_path[0] == "":
            return

        self.get_row_data(file_path[0])
        QMessageBox.information(self, "info", u"エクスポートしました", QMessageBox.Ok)

    def save_btn_clicked(self):
        path = "{}/_info/tools/KcBlendShapeSlider.json".format(os.path.dirname(self.cmd.get_scene_name()))
        self.get_row_data(path)
        QMessageBox.information(self, "info", u"保存しました", QMessageBox.Ok)

    def reload_btn_clicked(self):
        self.connect_signals(False)
        self.ui.shapes_filter_line.clear()

        self.set_current_shapes(self.current_groups_item)
        if self.current_path == "":
            self.reload()
        elif self.current_path != self.cmd.get_scene_name():
            namespace = self.cmd.get_scene_namespace()
            if namespace:
                text, ok = QtWidgets.QInputDialog.getText(self, 
                                                          "info", 
                                                          "replace namespace? {}".format(namespace), 
                                                          QtWidgets.QLineEdit.Normal, namespace)
                if ok:
                    datas = self.get_row_data()
                    datas = self.cmd.update_config(text, datas)
                    self.clear_ui()
                    for data in datas:
                        name = data.pop("name")
                        self.append_groups_table(name, **data)

        self.reload()

        self.current_path = self.cmd.get_scene_name()
        self.connect_signals(True)

    def get_row_data(self, path=None):
        if self.current_groups_item:
            self.set_current_shapes(self.current_groups_item)
        create = []
        for r in range(self.ui.groups_table.rowCount()):
            btn = self.ui.groups_table.cellWidget(r, self.get_groups_table_index("check"))
            item = self.ui.groups_table.item(r, self.get_groups_table_index("name"))

            const_name = unicode(self.ui.const_combo.currentText())
            if not const_name:
                const_name = "BlendShapes"

            name = unicode(item.text())
            if name == "":
                name = "BlendShapes"

            dic = {}
            dic["name"] = name
            dic["const_name"] = const_name
            dic["shapes"] = item.shape_data
            dic["center_is"] = item.center_shape_data
            dic["is_switching"] = self.ui.switching_check.checkState() == QtCore.Qt.Checked
            dic["color"] = item.marker_color
            dic["check"] = btn.is_active
            create.append(dic)

        if path is not None:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            json.dump({"data": create, 
                       "info": 
                          {"name": "KcBlendShapeSlider", "ver": self.VER}
                      }, 
                      open(path, "w"), "utf8", indent=4)

        return create




    def create_btn_clicked(self):
        path = "{}/_info/tools/KcBlendShapeSlider.json".format(os.path.dirname(self.cmd.get_scene_name()))
        create = self.get_row_data(path)

        roots = []
        model = self.cmd.get_selected_model()
        if model is not None:
            res = QtWidgets.QMessageBox.question(self, "info", u"以下を親にして作成します\n{}".format(model.LongName), QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.No|QtWidgets.QMessageBox.Cancel)
            if res == QtWidgets.QMessageBox.Cancel:
                return
            elif res == QtWidgets.QMessageBox.No:
                model = None

        for i, each in enumerate(create):
            if not each["check"]:
                continue

            try:
                root, parent = self.cmd.create_constraint(each, size=6, index=i)
                roots.append({"root": root, "index": i, "parent": parent})
            except:
                print "create failed: {}".format(each["name"])
                print traceback.format_exc()

        self.cmd.set_pos_to_model(model, roots)
        QtWidgets.QMessageBox.information(self, "info", u"作成しました", QtWidgets.QMessageBox.Ok)


    def add_btn_clicked(self):
        items = self.ui.shapes_table.selectedItems()

        for item in items:
            name = unicode(item.text())
            src_row = self.get_row_(self.ui.shapes_table, name)
            dst_row = self.get_row_(self.ui.create_table, name)

            self.ui.shapes_table.setRowHidden(item.row(), True)
            item.is_out = True
            dic = {"model": item.model_name, "shape": item.shape_name, "namespace": item.namespace}
            self.append_create_table(dic)
            item.setSelected(False)

    def rem_btn_clicked(self):
        items = self.ui.create_table.selectedItems()

        for item in items[::-1]:
            name = unicode(item.text())
            src_row = self.get_row_(self.ui.create_table, name)
            dst_row = self.get_row_(self.ui.shapes_table, name)

            self.ui.create_table.removeRow(src_row)
            self.ui.shapes_table.setRowHidden(dst_row, False)
            item.is_out = False

    def set_current_shapes(self, item):
        if not item:
            return
        item.shape_data = []
        item.center_shape_data = []
        for r in range(self.ui.create_table.rowCount()):
            logical = self.ui.create_table.verticalHeader().logicalIndex(r)
            item_ = self.ui.create_table.item(logical, self.get_create_table_index("name"))
            shape = {"shape": item_.shape_name, "model": item_.model_name, "namespace": item_.namespace}
            item.shape_data.append(shape)
            center = self.ui.create_table.cellWidget(logical, self.get_create_table_index("center"))
            if center.is_active:
                item.center_shape_data = shape

    def groups_table_index_changed(self, y, x, oy, ox):
        self.connect_signals(False)
        if oy != -1:
            old_item = self.ui.groups_table.item(oy, self.get_groups_table_index("name"))
            self.set_current_shapes(old_item)

        item = self.ui.groups_table.item(y, self.get_groups_table_index("name"))
        self.current_groups_item = item
        self.ui.create_table.clearContents()
        self.ui.create_table.setRowCount(0)
        self.set_shapes_table_and_create_table()
        self.connect_signals(True)

    def groups_add_btn_clicked(self):
        self.connect_signals(False)
        self.set_shapes()
        name = unicode(self.ui.group_line.text())
        if name == "":
            name = "BlendShapes"
        self.append_groups_table(name, check=True)
        self.ui.group_line.setText("")
        self.connect_signals(True)

    def groups_rem_btn_clicked(self):
        self.connect_signals(False)
        rows = [item.row() for item in self.ui.groups_table.selectedItems()]
        rows = list(set(rows))
        rows.sort(reverse=True)
        for row in rows:
            self.ui.groups_table.removeRow(row)
        self.current_groups_item = False
        # self.reload()
        if not self.current_groups_item:
            for r in range(self.ui.shapes_table.rowCount()):
                self.ui.shapes_table.setRowHidden(r, True)        
        self.ui.create_table.clearContents()
        self.ui.create_table.setRowCount(0)
        
        self.connect_signals(True)

    def append_groups_table(self, name, **kwargs):
        item = QtWidgets.QTableWidgetItem()
        item.setText(name)

        row = self.ui.groups_table.rowCount()
        self.ui.groups_table.setRowCount(row+1)
        self.ui.groups_table.setItem(row, self.get_groups_table_index("name"), item)
        btn = QtWidgets.QPushButton()
        self.ui.groups_table.setCellWidget(row, self.get_groups_table_index("check"), btn)
        btn.is_active = kwargs.get("check", False)
        btn.on_icon = QtGui.QIcon("{}/form/icon/check_on.png".format(self.tool_directory))
        btn.off_icon = QtGui.QIcon("{}/form/icon/check_off.png".format(self.tool_directory))
        if btn.is_active:
            btn.setIcon(btn.on_icon)
        else:
            btn.setIcon(btn.off_icon)
        btn.setIconSize(QtCore.QSize(20, 20))
        btn.setFlat(True)
        btn.row = row
        btn.clicked.connect(self.toggle_check_btn)

        color_btn = QtWidgets.QPushButton()
        color_btn.row = row
        if "right" in name.lower():
            temp_color = [0, 0, 220]
        elif "mouth" in name.lower():
            temp_color = [220, 220, 0]
        else:
            temp_color = [220, 0, 0]

        item.marker_color = kwargs.get("color", temp_color)
        color_btn.setStyleSheet("background-color: rgb({}, {}, {})".format(*item.marker_color))
        item.shape_data = kwargs.get("shapes", [])
        item.center_shape_data = kwargs.get("center_is", {})
        color_btn.item = item
        self.ui.groups_table.setCellWidget(row, self.get_groups_table_index("color"), color_btn)
        color_btn.clicked.connect(self.color_btn_clicked)

    def color_btn_clicked(self):
        widget = ColorDialog(self)
        widget.btn = self.sender()
        widget.color_set.connect(self.color_changed)
        widget.set_color(self.sender().item.marker_color)
        widget.exec_()

    def color_changed(self, dic):
        dic["btn"].setStyleSheet("background-color: rgb({}, {}, {})".format(*dic["color"]))
        dic["btn"].item.marker_color = dic["color"]

    def toggle_check_btn(self):
        flg = not self.sender().is_active
        row = self.sender().row
        rows = [item.row() for item in self.ui.groups_table.selectedItems()]
        if row not in rows:
            rows = [row]

        for row in rows:
            item = self.ui.groups_table.cellWidget(row, self.get_groups_table_index("check"))
            if flg:
                item.setIcon(item.on_icon)
            else:
                item.setIcon(item.off_icon)
            item.is_active = flg
    
    def center_btn_clicked(self):
        pushed_btn = self.sender()
        pushed_btn.setIcon(pushed_btn.on_icon)
        self.sender().is_active = True
        for r in range(self.ui.create_table.rowCount()):
            btn = self.ui.create_table.cellWidget(r, self.get_create_table_index("center"))
            if btn == pushed_btn:
                print btn, "pass", r
            else:
                btn.setIcon(btn.off_icon)
                btn.is_active = False

    def get_table_list(self, table):
        return getattr(self, "{}_list".format(table.objectName()))

    def get_table_dict(self, table):
        return getattr(self, "{}_dict".format(table.objectName()))

    def get_groups_table_index(self, name):
        return self.get_table_index(self.ui.groups_table, name)

    def get_create_table_index(self, name):
        return self.get_table_index(self.ui.create_table, name)

    def get_shapes_table_index(self, name):
        return self.get_table_index(self.ui.shapes_table, name)

    def get_table_index(self, table, name):
        lst = self.get_table_list(table)
        if name in lst:
            return lst.index(name)
        return -1

    def set_table(self, table):
        lst = self.get_table_list(table)
        dic = self.get_table_dict(table)
        table.setColumnCount(len(lst))
        ls = []
        for i, l in enumerate(lst):
            if l in dic:
                if "view" in dic[l]:
                    ls.append(dic[l]["view"])
                else:
                    ls.append(l)

                if "width" in dic[l]:
                    table.setColumnWidth(i, dic[l]["width"])
            else:
                ls.append(l)

        table.setHorizontalHeaderLabels(ls)

    def append_shapes_table(self, shape, hide=False):
        if len(self.ui.groups_table.selectedItems()) == 0:
            hide = True
        else:
            hide = False

        self.append_table(self.ui.shapes_table, shape, hide=hide)

    def append_create_table(self, shape, center_flg=False):
        self.append_table(self.ui.create_table, shape, center=center_flg)

    def append_table(self, table, shape, hide=False, center=False):
        if isinstance(shape, list):
            for d in shape:
                self.append_table(table, d, hide=hide)

        else:
            color = None
            if isinstance(shape, dict):
                name = self.to_view(shape)
            else:
                name = shape

            for r in range(table.rowCount()):
                check_item = table.item(r, self.get_table_index(table, "name"))
                if check_item:
                    if shape == check_item.text():
                        color = QtGui.QColor(255, 0, 0)
                        break

            row = table.rowCount()
            table.setRowCount(row+1)
            item = QtWidgets.QTableWidgetItem()

            if isinstance(shape, dict):
                item.model_name = shape["model"]
                item.namespace = shape["namespace"]
                item.shape_name = shape["shape"]
            item.setText(name)
            if color:
                item.setForeground(color)

            table.setItem(row, self.get_table_index(table, "name"), item)
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            item.is_out = False
            if hide:
                table.setRowHidden(row, True)
                item.is_out = True

            center_index = self.get_table_index(table, "center")
            if center_index == -1:
                return

            btn = QtWidgets.QPushButton()
            btn.setFlat(True)
            btn.on_icon = QtGui.QIcon("{}/form/icon/arrow_on.png".format(self.tool_directory))
            btn.off_icon = QtGui.QIcon("{}/form/icon/arrow_off.png".format(self.tool_directory))
            btn.off_up_icon = QtGui.QIcon("{}/form/icon/arrow_up_off.png".format(self.tool_directory))
            if center:
                btn.is_active = True
                btn.setIcon(btn.on_icon)
            else:
                btn.is_active = False
                btn.setIcon(btn.off_icon)                
            btn.setIconSize(QtCore.QSize(15, 15))
            btn.row = row
            btn.clicked.connect(self.center_btn_clicked)
            
            table.setCellWidget(row, center_index, btn)

    def set_shapes(self):
        self.ui.shapes_table.clearContents()
        self.ui.shapes_table.setRowCount(0)
        self.shapes = self.cmd.get_shapes()
        for k, v in self.shapes.items():
            if v["count"] == 0:
                continue
            v["shapes"].sort()
            for shape in v["shapes"]:
                self.append_shapes_table(shape, True)

    def reload(self):
        self.ui.create_table.setRowCount(0)
        self.ui.shapes_table.setRowCount(0)
        self.set_shapes()
        self.set_shapes_table_and_create_table()

    def to_view(self, data):
        return self.pattern.format(data["model"], data["shape"])

    def set_shapes_table_and_create_table(self):
        if not self.current_groups_item:
            for r in range(self.ui.shapes_table.rowCount()):
                self.ui.shapes_table.setRowHidden(r, True)
        else:
            for r in range(self.ui.shapes_table.rowCount()):
                item = self.ui.shapes_table.item(r, self.get_shapes_table_index("name"))
                item.is_out = False
                self.ui.shapes_table.setRowHidden(r, False)

            shape_data = self.current_groups_item.shape_data
            center_shape_data = self.current_groups_item.center_shape_data
            is_center_exists = False
            for data in shape_data:
                if data is None:
                    continue
                src_row = self.get_row_(self.ui.shapes_table, self.to_view(data))
                dst_row = self.get_row_(self.ui.create_table, self.to_view(data))
                item = self.ui.shapes_table.item(src_row, self.get_shapes_table_index("name"))
                if item is None:
                    continue
                item.is_out = True
                self.ui.shapes_table.setRowHidden(item.row(), True)
                if center_shape_data == data:
                    center_flg = True
                    is_center_exists = True
                else:
                    center_flg = False

                self.append_create_table(data, center_flg)

    def keyPressEvent(self, event):
        pass


class KcBlendShapeSliderCmd(object):
    def __init__(self):
        self.model_shapes = {}
        self.search = "(.*) < (.*)"
        self.pattern = self.search.replace("(.*)", "{}")

    def update_config(self, namespace, config):
        config = copy.deepcopy(config)
        current_shapes = self.get_shapes()
        for each in config:
            new_shapes = []
            for shape in each["shapes"]:
                if shape is None:
                    continue
                new_model_name = shape["model"].replace(shape["namespace"], namespace)
                new_shape = {k.replace(shape["namespace"], namespace): v.replace(shape["namespace"], namespace) for k, v in shape.items()}
                if new_model_name in current_shapes:
                    if new_shape in current_shapes[new_model_name]["shapes"]:
                        new_shapes.append(new_shape)

            each["shapes"] = new_shapes
            if isinstance(each["center_is"], dict) and len(each["center_is"]) > 0:
                each["center_is"] = {k: v.replace(each["center_is"]["namespace"], namespace) for k, v in each["center_is"].items()}

            each["namespace"] = namespace

        return config
  


    def get_shapes(self):
        shape_dic = {}
        for m in FBSystem().Scene.Components:
            if isinstance(m, (FBModelSkeleton, FBModelNull, FBModelPlaceHolder)):
                continue

            if not isinstance(m, FBModel):
                continue

            if not m.BlendShapeDeformable:
                continue

            shape_dic[m.LongName] = {} # {"model": m}
            self.model_shapes[m.LongName] = {"model": m}

            for i in range(m.GetSrcCount()):
                mesh = m.GetSrc(i)
                if not isinstance(mesh, FBMesh):
                    continue
                shape_dic[m.LongName]["count"] = mesh.ShapeGetCount()
                if ":" in m.LongName:
                    shape_dic[m.LongName]["namespace"] = m.LongName.split(":")[0]
                else:
                    shape_dic[m.LongName]["namespace"] = None
                shape_dic[m.LongName]["model_name"] = m.Name
                for ii in range(mesh.ShapeGetCount()):
                    dic = {"model": m.LongName, "shape": mesh.ShapeGetName(ii), "namespace": shape_dic[m.LongName]["namespace"]}
                    shape_dic[m.LongName].setdefault("shapes", []).append(dic)
                    self.model_shapes[m.LongName].setdefault("shapes", []).append(dic["shape"])
    
        return shape_dic

    def get_constraint_names(self):
        const = []
        for each in FBSystem().Scene.Constraints:
            if not isinstance(each, FBConstraintRelation):
                continue

            if "_CTRL_" in each.Name:
                const.append(each.Name.split("_CTRL_")[0])

        return const

    def get_scene_name(self):
        return FBApplication().FBXFileName

    def get_selected_model(self):
        m_list = FBModelList()
        FBGetSelectedModels(m_list)
        if len(m_list) == 0:
            return None
        else:
            return m_list[-1]

    def set_pos_to_model(self, model, children):
        for child in children:
            if child["root"] is None:
                if model:
                    model.ConnectSrc(child["parent"])
            else:
                if model:
                    model.ConnectSrc(child["root"])
                child["root"].ConnectSrc(child["parent"])
            kc_key.set_rot(child["parent"], [90, 0, 0], False)
            #kc_key.set_trs(child["parent"], [0, -child["index"]*3.5, 0], False)

    def create_constraint(self, data, size=10, root=None, index=0):
        def _create_slider(parent, name, count, center, size, color):
            guide = FBModelMarker("{}_guide".format(name))
            w = (size*count)/2
            guide.Look = FBMarkerLook.kFBMarkerLookSquare
            guide.Color = FBColor(220, 220, 220)
            guide.PropertyList.Find("Pickable").Data = True
#            if center != 0:
#                kc_key.set_trs(guide, [w+size, 0, 0], True)
#            else:
            kc_key.set_trs(guide, [w, 0, 0], True)
            # kc_key.set_rot(guide, [90, 0, 0], True)
            kc_key.set_scl(guide, [w, 1, 1], True)
            parent.ConnectSrc(guide)

            null = FBModelNull("{}_Ofs".format(name))
            parent.ConnectSrc(null)
            guide.Show = True

            ctrl = FBModelMarker("{}_CTRL".format(name))
            null.ConnectSrc(ctrl)
            ctrl.Show = True
            ctrl.Color = FBColor(*color)
            ctrl.Look = FBMarkerLook.kFBMarkerLookBox
            
            center_pos = size*center
 
            kc_key.set_trs(null, [center_pos, 0, 0], True)
            kc_key.set_scl(ctrl, [1, 0.5, 1.7], False)
            FBSystem().Scene.Evaluate()

            return guide, ctrl

        def _create_main_relation(const_name, ctrl, shapes, center, size, toggle=True, index=0):
            gbl_ofs = index * 1500

            relation = kcRelation("{}_Relation".format(const_name))
            src = relation.set_source_box(ctrl, False, y=gbl_ofs)
            vec2num = relation.set_func_box(["Converters", "Vector to number"])
            relation.connect_box(src, "Lcl Translation", "V", vec2num)
            relation.move_from_box(src, vec2num, x=400)
            ofs = (center * size)
            if center != 0:
                min_max = [[(i*size)-ofs, ((i+1)*size)-ofs] for i in range(len(shapes))]
                min_max.insert(center, [0, 0])
                #min_max = min_max[1:]
                shapes.insert(center, None)
            else:
                min_max = [[i*size, (i+1)*size] for i in range(len(shapes))]

            shape_range = []
            for i, shape in enumerate(shapes):
                if shape is None:
                    continue

                model_name = shape["model"]
                shape = shape["shape"]

                shape = str(shape)
                temp_min, temp__max = min_max[i]
                if temp_min < 0:
                    shape_range.append(temp_min)
                    min_ = temp__max
                    max_ = temp_min
                else:
                    shape_range.append(temp__max)
                    min_ = temp_min
                    max_ = temp__max

                substruct = relation.set_func_box(["Number", "Subtract (a - b)"], data=["b", min_])
                relation.connect_box(vec2num, "X", "a", substruct)

                #is_equal = relation.set_func_box(["Number", "Is Identical (a == b)"], data=["b", 0.0])
                #relation.connect_box(substruct, "Result", "a", is_equal)

                relation.move_from_box(vec2num, substruct, x=400, y=(i*200))
                #relation.move_from_box(vec2num, is_equal, x=800, y=i*200)

                substruct02 = relation.set_func_box(["Number", "Subtract (a - b)"])
                relation.move_from_box(substruct, substruct02, x=0, y=100)
                #relation.move_from_box(substruct02, is_equal, x=1600, y=i*200)

                relation.set_func_data(substruct02, "a", max_)
                relation.set_func_data(substruct02, "b", min_)
                divide = relation.set_func_box(["Number", "Divide (a/b)"])

                relation.connect_box(substruct, "Result", "a", divide)
                relation.connect_box(substruct02, "Result", "b", divide)

                relation.move_from_box(substruct02, divide, x=400, y=0)

                multi = relation.set_func_box(["Number", "Multiply (a x b)"], data=["b", 100])

                if not toggle:
                    scale_ofs = relation.set_func_box(["Number", "Scale And Offset (Number)"])
                    relation.set_func_data(scale_ofs, "Clamp Max", 1.0)
                    relation.set_func_data(scale_ofs, "Clamp Min", 0.0)
                    relation.connect_box(scale_ofs, "Result", "a", multi)
                    relation.connect_box(divide, "Result", "X", scale_ofs)
                    relation.move_from_box(substruct02, scale_ofs, x=1800, y=400)
                    relation.move_from_box(scale_ofs, multi, x=1800, y=200)
                else:
                    if_cond02 = relation.set_func_box(["Number", "IF Cond Then A Else B"], data=["b", 0])
                    is_between = relation.set_func_box(["Number", "Is Between A and B"])
                    relation.set_func_data(is_between, "a", 1.0)
                    relation.set_func_data(is_between, "b", 0.0)
                    relation.connect_box(divide, "Result", "Value", is_between)
                    relation.connect_box(divide, "Result", "a", if_cond02)
                    relation.connect_box(is_between, "Result", "Cond", if_cond02)
                    relation.connect_box(if_cond02, "Result", "a", multi)

                    relation.move_from_box(divide, is_between, x=200, y=100)
                    relation.move_from_box(is_between, if_cond02, x=400, y=-200)
                    relation.move_from_box(if_cond02, multi, x=400, y=0)
                

                model = False
                if model_name in self.model_shapes:
                    model = self.model_shapes[model_name]["model"]
                
                #for k, v in self.model_shapes.items():
                #    if shape in v["shapes"]:
                #        model = v["model"]
                #        break

                if not model:
                    continue

                model.PropertyList.Find(shape).SetAnimated(True)

                target = relation.set_target_box(model, False)
                relation.connect_box(multi, "Result", shape, target)
            
                relation.move_from_box(multi, target, x=2000)
            relation.constraint.Active = True

            return shape_range
        
        def _create_CTRL_relation(const_name, ctrl, shape_range, size, center, index):
            gbl_index = index * 600

            relation = kcRelation("{}_Relation".format(ctrl.Name))

            src = relation.set_source_box(ctrl, False, y=gbl_index)
            dst = relation.set_target_box(ctrl, False)
            sum_10_num = (len(shape_range)/10) + 1
            sum_10s = []
            sum_10_join = False
            alphabet = "abcdefghij"
            num2vec = relation.set_func_box(["Converters", "Number to Vector"])
            relation.connect_box(num2vec, "Result", "Lcl Translation", dst)
            if sum_10_num > 1:
                sum_10_join = relation.set_func_box(["Number", "Sum 10 Numbers"])
                relation.connect_box(sum_10_join, "Result", "X", num2vec)

            for i in range(sum_10_num):
                sum_10 = relation.set_func_box(["Number", "Sum 10 Numbers"])
                if sum_10_join:
                    alpha_index = i % 10
                    relation.connect_box(sum_10, "Result", alphabet[alpha_index], sum_10_join)
                else:
                    relation.connect_box(sum_10, "Result", "X", num2vec)

                sum_10s.append(sum_10)
            
            
            vec2num = relation.set_func_box(["Converters", "Vector to Number"])
            relation.connect_box(src, "Lcl Translation", "V", vec2num)

            relation.move_from_box(src, vec2num, x=350)
            
            for i, max_ in enumerate(shape_range):
                if max_ <= 0:
                    value = max_ + 0.5
                    direction = 0
                else:
                    value = max_ - 0.5
                    direction = 1

                if max_ == 0 and center != 0:
                    is_greater = relation.set_func_box(["Number", "Is Identical (a == b)"], data=["b", 0])
                    multi = relation.set_func_box(["Number", "Multiply (a x b)"], data=["b", 0])
                elif direction == 0:
                    is_greater = relation.set_func_box(["Number", "Is Less or Equal (a <= b)"], data=["b", value])
                    multi = relation.set_func_box(["Number", "Multiply (a x b)"], data=["b", -size])
                else:
                    is_greater = relation.set_func_box(["Number", "Is Greater or Equal (a >= b)"], data=["b", value])
                    multi = relation.set_func_box(["Number", "Multiply (a x b)"], data=["b", size])

                relation.connect_box(vec2num, "X", "a", is_greater)
                relation.connect_box(is_greater, "Result", "a", multi)
                if i == 0:
                    sum_10 = sum_10s[0]
                else:
                    sum_10_num = (i/10)
                    sum_10 = sum_10s[sum_10_num]
                
                alpha_index = i % 10
                relation.connect_box(multi, "Result", alphabet[alpha_index], sum_10)

                relation.move_from_box(vec2num, is_greater, x=350, y=i*200)
                relation.move_from_box(is_greater, multi, x=350)

            relation.move_from_box(vec2num, sum_10s, x=2000, y_step=200)
            relation.move_from_box(sum_10s[0], num2vec, x=350)
            relation.move_from_box(num2vec, dst, x=350)

            #folder = self.add_const_folder("CTRL")
            #folder.Items.append(relation.constraint)
            #folder.ConnectSrc()            
            relation.constraint.Active = True
            #kc_key.set_scl(ctrl, [0, 0, 0], False)


        self.get_shapes()
        name = str(data["name"])
        shapes = data["shapes"]# [str(l) for l in data["shapes"]]


        if "_" in name:
            root_name = "{}_Root".format(name.split("_")[0])
            root = kc_model.find_model_by_name(root_name)
            name = "_".join(name.split("_")[1:])
            if not root:
                root = FBModelNull(root_name)

        parent = FBModelNull(name)

        if isinstance(data["center_is"], list) and len(data["center_is"]) == 0:
            center = 0
        elif data["center_is"]["shape"] == shapes[0]:
            center = 0
        else:
            center = shapes.index(data["center_is"]) + 1

        guide, ctrl = _create_slider(parent, name, len(shapes), center=center, size=size, color=data["color"])

        
        shape_range = _create_main_relation(data["const_name"], ctrl, data["shapes"], center=center, size=size, index=index)
        if data["is_switching"]:
            _create_CTRL_relation("{}_CTRL".format(data["const_name"]), ctrl, shape_range, size, center=center, index=index)

        return root, parent

    def add_const_folder(self, name, force=False):
        tmp = FBConstraintRelation("__TMP_NAV_MODULE_DELETE__")
        return self.create_folder(name, tmp, delete=True, force=force)

    def create_folder(self, name, add_item, delete=True, force=False):
        if force:
            folder = False
        else:
            folder = self.get_folder(name)
        if folder:
            return folder
        create = FBFolder(name, add_item)
        #if delete:
        #    add_item.FBDelete()
        self._delete_tmp()
        return create

    def get_folder(self, name):
        for folder in FBSystem().Scene.Folders:
            if folder.LongName == name:
                return folder
        return False

    def _delete_tmp(self):
        print "delete action"
        for c in FBSystem().Scene.Constraints[::-1]:
            if c.Name.find("__TMP_NAV_MODULE_DELETE__") != -1:
                print "%s > delete" % c.Name
                c.FBDelete()

    def get_scene_namespace(self):
        for model in FBSystem().Scene.RootModel.Children:
            if ":" in model.LongName:
                return model.LongName.split(":")[0]
        return None


def start_app():
    kc_qt.start_app(KcBlendShapeSlider, root=kc_qt.get_root_window(), name="KcBlendShapeSlider", x=1000)


if __name__ == "__builtin__":
    def test_cmd():
        x = KcBlendShapeSliderCmd()
        data = [
                {
                    "shapes": [
                        "Fmouth_normal_1",
                        "Fmouth_normal_2",
                        "Fmouth_normal_3", 
                        "Fmouth_normal_4"
                    ], 
                    "is_switching": True, 
                    "center_is": {}, 
                    "name": "eye_normal", 
                    "const_name": "BlendShapes",
                    "color": [100, 100, 255]
                }
                ]
        data_path = "H:/works/keica/data/BlendShapeSlider/_info/tools/KcBlendShapeSlider.json"
        data = json.load(open(data_path, "r"), "utf8")
        # data = {"shapes": ["eye_normal_1_R", "eye_normal_2_R", "eye_normal_3_R", "eye_normal_4_R"], "as_switching": False, "center_is": False, "name": "Eye", "const_name": "BlendShapes"}
        FBApplication().FileNew()
        path = "H:/works/keica/data/BlendShapeSlider/aoi_05__.fbx"
        FBApplication().FileOpen(path)
        root = x.create_constraint(data[0], size=10)
        kc_key.set_trs(root, [-45, 130, 0], True)
        kc_key.set_rot(root, [90, 0, 0], True)

    def test_cmd02():
        x = KcBlendShapeSliderCmd()
        #shapes = x.get_shapes()

        path = "H:/works/keica/data/BlendShapeSlider/_info/tools/KcBlendShapeSlider_test.json"
        js = json.load(open(path, "r"), "utf8")
        print js
        x.update_config("Lily", js["data"])

    def test_ui():
        FBApplication().FileNew()
        path = "H:/works/keica/data/BlendShapeSlider/aoi_05__.fbx"
        FBApplication().FileOpen(path)

        start_app()    
    start_app()
