# -*- coding: utf8 -*-

import os
import sys
import json
import copy

mods = ["{}/source/python".format(os.environ["KEICA_TOOL_PATH"]), 
        "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])]
for mod in mods:
    if mod not in sys.path:
        sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
import KcLibs.win.kc_qt as kc_qt
import KcLibs.maya.kc_material as kc_material
from KcLibs.win.kc_qt import QtWidgets, QtCore, QtGui
from puzzle.PzLog import PzLog

_LOG_ = PzLog("KcImageMapper", log_directory=kc_env.get_log_directory("KcImageMapper"))
_LOGGER_ = _LOG_.logger

kc_env.append_sys_paths()
reload(kc_qt)
reload(kc_material)
if kc_env.mode == "maya":
    import maya.cmds as cmds


class KcGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(KcGraphicsView, self).__init__(parent)
        self.scene_area = KcGraphicsScene()
        self.setScene(self.scene_area)


class KcGraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super(KcGraphicsScene, self).__init__(parent)


class Emitter(QtCore.QObject):
    image_clicked = QtCore.Signal(dict)


class KcImageItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super(KcImageItem, self).__init__(parent)
        self.emitter = Emitter()

    def mouseMoveEvent(self, event):
        mouse_pos = event.pos()

    def mousePressEvent(self, event):
        pos = event.pos()
        rgb = self.pixmap().toImage().pixel(pos.x(), pos.y())
        x = QtGui.QColor(rgb)

        self.emitter.image_clicked.emit({"rgb": x.getRgb(), "x": pos.x(), "y": pos.y()})

    def set_pixmap(self, path):
        self.setPixmap(QtGui.QPixmap(path))


class KcGraphicsItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super(KcGraphicsItem, self).__init__(*args, **kwargs)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setBrush(QtGui.QBrush(QtGui.QColor(*kwargs.get("brush_color", [100, 100, 100]))))
        self.setPen(QtGui.QPen(QtGui.QColor(*kwargs.get("pen_color", [0, 0, 0]))))
        self.setRect(0, 0, 10, 10)
        self.emitter = Emitter()

    def mousePressEvent(self, event):
        self.emitter.image_clicked.emit({"info": self.info})

class KcImageMapper(kc_qt.ROOT_WIDGET):
    NAME = "KcImageMapper"
    info_signal = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super(KcImageMapper, self).__init__(parent)
        self.tool_directory = kc_env.get_tool_config("maya", self.NAME)
        self.material_table_list = ["check", "name"]
        self.material_table_dict = {"check": {"view": "", "width": 20}}
        self.cmd = KcImageMapperCommand()
        self.connected = False
        self.pixmap_item = None
        self.low_color = [110, 110, 110]
        self.hi_color = [220, 220, 220]

    def set_ui(self, outside_mode=False, config_item=False):
        ui_path = "{}/form/ui/main.ui".format(self.tool_directory)
        self.ui = kc_qt.load_ui(ui_path, self)
        print(ui_path)
        self.outside_mode = outside_mode

        self.graphics_view = KcGraphicsView(self)
        self.ui.graphics_layout.addWidget(self.graphics_view)


        self.set_table(self.ui.material_table)

        self.config_path = self.cmd.get_info_config_path()
        print(self.config_path)
        if self.outside_mode:
            if "path" in config_item:
                self.config_path = config_item["path"]

        if not os.path.exists(self.config_path):
            file_path = QtWidgets.QFileDialog.getOpenFileName(self, "info", u"イメージのパス")
            self.file_config = {"data": {"items": []}, "info": {}}
            self.file_config["data"]["path"] = file_path[0]
        else:
            self.file_config = json.load(open(self.config_path, "r"), "utf8")
        
        if self.outside_mode:
            self.file_config["data"]["items"] = [config_item["item"]]
            # self.file_config["data"]["path"] = config_item["path"]

        self.ui.file_line.setText(self.file_config["data"]["path"])

        self.get_materials()
        self.change_pixmap(self.file_config["data"]["path"], self.file_config["data"]["items"])

        self.ui.assign_btn.clicked.connect(self.assign_btn_clicked)
        self.reset_splitter()
        self.connect_signals(True)

        self.material_menu = QtWidgets.QMenu()
        action = QtWidgets.QAction("remove", self)

        self.material_menu.addAction(action)

        self.ui.material_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.material_table.customContextMenuRequested.connect(self.material_table_menu_exec)


        self.ui.reload_btn.setIcon(QtGui.QIcon("{}/form/icon/reload.png".format(self.tool_directory)))
        self.ui.close_btn.clicked.connect(self.close_btn_clicked)
        self.ui.import_btn.clicked.connect(self.import_btn_clicked)
        self.ui.export_btn.clicked.connect(self.export_btn_clicked)
        if self.outside_mode:
            self.set_outside_mode(config_item)

        self.show()

    def import_btn_clicked(self):
        if os.path.lexists(self.config_path):
            where = os.path.dirname(self.config_path)
        else:
            where = "{}/info/tools".format(os.path.dirname(cmds.file(sn=True, q=True)))
            if not os.path.exists(where):
                os.makedirs(where)
        path, filter_ = QtWidgets.QFileDialog.getOpenFileName(self, "import path", where, "(*.json)")
        if path == "":
            return

        # self.config_path = path
        self.reload(path)

    def export_btn_clicked(self):
        if os.path.lexists(self.config_path):
            where = os.path.dirname(self.config_path)
        else:
            where = os.path.dirname(cmds.file(sn=True, q=True))
        path, filter_ = QtWidgets.QFileDialog.getSaveFileName(self, "export path", where, "(*.json)")
        if path == "":
            return

        self.save_config(save_path=path)


    def material_table_menu_exec(self, point):
        self.material_menu.exec_(self.sender().mapToGlobal(point))

    def close_btn_clicked(self):
        try:
            self.ui.close()
        except:
            pass
        try:
            self.close()
        except:
            pass

    def reset_splitter(self):
        self.ui.splitter.setSizes([40, 400])

    def save_config(self, change_materials=False, save_path=None):
        if self.outside_mode:
            return
        self.connect_signals(False)
        if save_path is None:
            save_path = self.config_path # self.cmd.get_info_config_path()
            # self.config_path = save_path

        self.get_item()
        items = []

        mat_sets = []
        for r in range(self.ui.material_table.rowCount()):
            item = self.ui.material_table.item(r, self.material_table_list.index("name"))
            if not item:
                continue
            if not hasattr(item, "info"):
                continue

            if not item.info:
                continue

            rgb = self.pixmap_item.pixmap().toImage().pixel(item.info["x"], item.info["y"])
            color = QtGui.QColor(rgb)
            rgb_value = color.toRgb()

            info_ = {"x": item.info["x"], "y": item.info["y"], "rgb": item.info["rgb"]} # copy.deepcopy(item.info)

            # del info_["object"]
            info_["material"] = unicode(item.text())
            items.append(info_)

            mat_sets.append([info_["material"], rgb_value])

        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))

        if not self.outside_mode:
            print("save config path: {}".format(save_path))
            json.dump({"data": {"path": unicode(self.ui.file_line.text()), "items": items}, "info": {}}, open(save_path, "w"), "utf8", indent=4)
        else:
            print("outside mode: save pass")
        if change_materials:
            for each in mat_sets:
                try:
                    self.cmd.set_material(*each)
                except:
                    cmds.warning("error occur check this material. {} value: {}".format(each[0], each[1]))

        self.connect_signals(True)

    def assign_btn_clicked(self):
        self.save_config(True)

    def connect_signals(self, flg):
        if not self.connected and flg:
            self.ui.material_table.itemSelectionChanged.connect(self.material_table_current_cell_changed)
            self.ui.file_line.editingFinished.connect(self.file_line_editing_finished)
            self.ui.file_btn.clicked.connect(self.file_btn_clicked)
            self.ui.reload_btn.clicked.connect(self.reload_btn_clicked)
            self.ui.clear_btn.clicked.connect(self.clear_btn_clicked)
            self.connected = True
        elif self.connected and not flg:
            self.ui.material_table.itemSelectionChanged.disconnect(self.material_table_current_cell_changed)
            self.ui.file_line.editingFinished.disconnect(self.file_line_editing_finished)
            self.ui.file_btn.clicked.disconnect(self.file_btn_clicked)
            self.ui.reload_btn.clicked.disconnect(self.reload_btn_clicked)
            self.ui.clear_btn.clicked.disconnect(self.clear_btn_clicked)
            self.connected = False

    def reload_btn_clicked(self):
        self.reload()
        # if self.outside_mode:
        #     return


    def reload(self, reload_path=None):
        if reload_path is None:
            self.save_config(False)
            reload_path = self.config_path
        print(">>>>", reload_path)

        if reload_path == "":
            return
        self.file_config = json.load(open(reload_path, "r"), "utf8")

        self.ui.material_table.setRowCount(0)

        for item in self.graphics_view.scene().items()[::-1]:
            if not hasattr(item, "info"):
                continue
            self.graphics_view.scene().removeItem(item)

        self.get_materials()
        print("image:", self.file_config["data"]["path"])
        self.change_pixmap(self.file_config["data"]["path"], self.file_config["data"]["items"])
        self.ui.file_line.setText(self.file_config["data"]["path"])
        self.reset_splitter()

    def clear_btn_clicked(self):
        selected = self.ui.material_table.selectedItems()
        if len(selected) == 0:
            selected = []
            for r in range(self.ui.material_table.rowCount()):
                item = self.ui.material_table.item(r, self.material_table_list.index("check"))
                selected.append(item)

            message = u"全てのアイテムをクリアしますか？"
        else:
            message = u"選択しているアイテムをクリアしますか？"

        mes = QtWidgets.QMessageBox.information(self, u"info", message, QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
        if mes == QtWidgets.QMessageBox.Cancel:
            return

        for s in selected:
            if hasattr(s, "info") and s.info:
                self.graphics_view.scene().removeItem(s.info["object"])
                s.info = False
                color_item = self.ui.material_table.item(s.row(), self.material_table_list.index("check"))
                # color_item.setBackground(QtGui.QColor(40, 40, 40))
                item = self.ui.material_table.item(s.row(), self.material_table_list.index("name"))
                item.setForeground(QtGui.QColor(*self.low_color))
                col = kc_material.get_material_color(str(item.text()))
                color_item.setBackground(QtGui.QColor(*col))
            else:
                s.setForeground(QtGui.QColor(*self.low_color))

    def file_btn_clicked(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "info", u"イメージのパス")
        self.ui.file_line.setText(file_path[0])
        self.file_line_editing_finished()

    def file_line_editing_finished(self):
        path = unicode(self.ui.file_line.text())

        if not os.path.exists(path):
            self.change_pixmap(None)
            return

        if self.outside_mode:
            self.change_pixmap(path)
            self.reset_splitter()
        else:
            self.reload_btn_clicked()

    def material_table_current_cell_changed(self):
        for g_item in self.graphics_view.scene().selectedItems():
            g_item.setSelected(False)

        for r in range(self.ui.material_table.rowCount()):
            item = self.ui.material_table.item(r, self.material_table_list.index("name"))
            if not hasattr(item, "info"):
                continue

            elif not item.info:
                continue

            if item.isSelected():
                item.info["object"].setSelected(True)
            else:
                item.info["object"].setSelected(False)

    def set_table(self, widget):
        list_ = getattr(self, "{}_list".format(widget.objectName()))
        dict_ = getattr(self, "{}_dict".format(widget.objectName()))
        widget.setColumnCount(len(list_))
        label = []
        for c, name in enumerate(list_):
            view = name
            if name in dict_:
                if "view" in dict_[name]:
                    view = dict_[name]["view"]

                if "width" in dict_[name]:
                    widget.setColumnWidth(c, dict_[name]["width"])

            label.append(view)

        widget.setHorizontalHeaderLabels(label)

    def append_material_table(self, data):
        if isinstance(data, list):
            for d in data:
                self.append_material_table(d)

        else:
            r = self.ui.material_table.rowCount()
            self.ui.material_table.setRowCount(r + 1)
            item = QtWidgets.QTableWidgetItem()
            item.setText(data["name"])
            item.setForeground(QtGui.QColor(*self.low_color))
            self.ui.material_table.setItem(r, self.material_table_list.index("name"), item)
            color_item = QtWidgets.QTableWidgetItem()
            self.ui.material_table.setItem(r, self.material_table_list.index("check"), color_item)
            color_item.setBackground(QtGui.QColor(*data["color"]))

            
            #for c, name in enumerate(self.material_table_list):
            #    item = QtWidgets.QTableWidgetItem()
            #    if name == "name":
            #        item.setText(data["name"])
            #    print(data["name"])
            #    self.ui.material_table.setItem(r, c, item)

    def change_pixmap(self, path=None, item_infos=[]):
        if self.pixmap_item is None:
            if path is None:
                pic = None
            elif os.path.exists(path):
                pic = QtGui.QPixmap(path)
            else:
                pic = None

            self.pixmap_item = KcImageItem(pic)
            self.pixmap_item.emitter.image_clicked.connect(self.color_pick)
            self.graphics_view.scene().addItem(self.pixmap_item)

        else:
            self.pixmap_item.set_pixmap(path)
            self.ui.splitter.setSizes([1, 5])
        
        if not self.outside_mode:
            for r in range(self.ui.material_table.rowCount()):
                item = self.ui.material_table.item(r, self.material_table_list.index("name"))
                for info in item_infos:
                    if info["material"] == unicode(item.text()):
                        self.set_material_table_item(item, info)

    def get_materials(self):
        mat_list = self.cmd.get_materials()
        self.append_material_table(mat_list)

    def get_item(self):
        for item in self.graphics_view.scene().items():
            if not hasattr(item, "position"):
                continue

    def color_pick(self, info):
        style = "background-color: rgba({}, {}, {}, {})".format(*info["rgb"])
        self.ui.color_label.setStyleSheet(style)

        if self.outside_mode:
            info_ = {}
            info_["rgb"] = info["rgb"]
            info_["x"] = info["x"]
            info_["y"] = info["y"]

            self.graphics_view.scene().removeItem(self.current_item)
            self.set_single_item(info) 
            self.info_signal.emit(info)

        else:
            for select in self.ui.material_table.selectedItems():
                if select.column() != self.material_table_list.index("name"):
                    continue

                if hasattr(select, "info") and select.info:
                    self.graphics_view.scene().removeItem(select.info["object"])

                self.set_material_table_item(select, info)

    def item_clicked(self, dic):
        self.connect_signals(False)
        material = dic["info"].get("material", False)
        if material:
            for r in range(self.ui.material_table.rowCount()):
                item = self.ui.material_table.item(r, self.material_table_list.index("name"))
                if item:
                    if item.text() == material:
                        item.setSelected(True)
                    else:
                        item.setSelected(False)
        self.connect_signals(True)

    def set_material_table_item(self, table_item, info):
        item = KcGraphicsItem()
        self.graphics_view.scene().addItem(item)
        item.position = QtCore.QPointF(info["x"], info["y"])

        rgb = self.pixmap_item.pixmap().toImage().pixel(info["x"], info["y"])
        color = QtGui.QColor(rgb)
        rgb_value = color.getRgb()
        info["rgb"] = rgb_value
        info["object"] = item
        item.setPos(item.position)

        color_item = self.ui.material_table.item(table_item.row(), self.material_table_list.index("check"))
        color_item.setBackground(QtGui.QColor(*info["rgb"]))
        name = self.ui.material_table.item(table_item.row(), self.material_table_list.index("name"))
        info["material"] = unicode(name.text())
        name.setForeground(QtGui.QColor(*self.hi_color))
        color_item.info = info
        table_item.info = info
        item.info = info
        item.emitter.image_clicked.connect(self.item_clicked)

    def set_outside_mode(self, info=None):
        self.ui.material_layout_widget.setVisible(False)
        self.ui.assign_btn_layout_widget.setVisible(False)
        self.set_single_item(info["item"])

    def set_single_item(self, info):
        item = KcGraphicsItem()
        self.graphics_view.scene().addItem(item)
        item.position = QtCore.QPointF(info["x"], info["y"])

        rgb = self.pixmap_item.pixmap().toImage().pixel(info["x"], info["y"])
        color = QtGui.QColor(rgb)
        rgb_value = color.getRgb()
        info["rgb"] = rgb_value
        info["object"] = item
        item.setPos(item.position)
        item.info = info

        item.setSelected(True)
        self.current_item = item

        #color_item = self.ui.material_table.item(table_item.row(), self.material_table_list.index("check"))
        #color_item.setBackground(QtGui.QColor(*info["rgb"]))
        #name = self.ui.material_table.item(table_item.row(), self.material_table_list.index("name"))
        # info["material"] = info[]
        # color_item.info = info
        # table_item.info = info
        # item.emitter.image_clicked.connect(self.item_clicked)
    def keyPressEvent(self, event):
        return

class KcImageMapperCommand(object):
    def __init__(self):
        pass

    def get_materials(self):
        if kc_env.mode == "win":
            return [{"name": "head_mat"}, {"name": "body_mat"}, {"name": "hand_mat"}]
        else:
            return [{"name": mat, "color": kc_material.get_material_color(mat)} for mat in cmds.ls(materials=True) if "particle" not in mat]

    def get_info_config_path(self):
        if kc_env.mode == "win":
            return "H:/works/keica/data/image/config.json"
        else:
            file_path = cmds.file(sn=True, q=True)
            if file_path == "":
                return "{}/tools/KcImageMapper.json".format(kc_env.get_user_config("KcImageMapper"))
            d, f = os.path.split(file_path)
            return "{}/info/tools/KcImageMapper.json".format(d)

    def set_material(self, material, value):
        if kc_env.mode == "win":
            return

        if cmds.attributeQuery("color", node=material, exists=True):
            cmds.setAttr("{}.color".format(material), value.redF(), value.greenF(), value.blueF(), type="double3")
        elif cmds.attributeQuery("outColor", node=material, exists=True):
            cmds.setAttr("{}.outColor".format(material), value.redF(), value.greenF(), value.blueF(), type="double3")
        else:
            cmds.warning("attribute color or outColor was not exists.change color failed.{}".format(material))


def start_app():
    kc_qt.start_app(KcImageMapper, root=kc_qt.get_root_window(), name="KcImageMapper")

if __name__ == "__main__":
    start_app()
