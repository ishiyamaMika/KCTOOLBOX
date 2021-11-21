# -*- coding: utf8 -*-

import os
import sys
import json
import copy
import re

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)
print mod

import KcLibs.core.kc_env as kc_env
import KcLibs.win.kc_qt as kc_qt
from KcLibs.win.kc_qt import QtWidgets, QtCore, QtGui

import KcLibs.maya.kc_mesh as kc_mesh

reload(kc_qt)

kc_env.append_sys_paths()

import maya.cmds as cmds
from functools import wraps
from puzzle.PzLog import PzLog
import KcLibs.maya.kc_file_io as kc_file_io
import shutil
reload(kc_file_io)
_LOG_ = PzLog("KcReferenceReplacer", log_directory=kc_env.get_log_directory("KcReferenceReplacer"))
_LOGGER_ = _LOG_.logger

def undo_chunk(func):
    def do(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        res = func(*args, **kwargs)
        cmds.undoInfo(closeChunk=True)
        return res
    return do

class KcReferenceReplacer(kc_qt.ROOT_WIDGET):
    NAME = "KcReferenceReplacer"

    def __init__(self, parent=None):
        super(KcReferenceReplacer, self).__init__(parent)
        self.tool_directory = kc_env.get_tool_config("maya", self.NAME)
        self.anim_path_keyword = "04_animation"
        self.true_color = "background-color: rgb(100, 100, 200)"
        self.false_color = "background-color: rgb(200, 100, 100)"
        self.norm_color = "background-color: rgb(95, 95, 95)" 
        self.reference_table_list = ["name", "is_loaded", "reload", "import", "delete", "shade", "hiColor", "..."]
        self.btn_names = ["reload", "import", "delete", "shade", "hiColor", "..."]
        self.reference_table_dict = {"name": {"width": 200}, 
                                     "hiColor": {"view": ""}, 
                                     "delete": {"view": ""},
                                     "shade": {"view": ""}, "...": {"view": ""}, "reload": {"view": ""}}

    def set_ui(self):
        ui_path = "{}/form/ui/main.ui".format(self.tool_directory)
        self.ui = kc_qt.load_ui(ui_path, self)
        self.set_table(self.ui.reference_table)
        # self.ui.do_btn.clicked.connect(self.do_btn_clicked)
        self.reload()
        self.show()
        self.resize(750, self.height())
        self.ui.reload_btn.clicked.connect(self.reload)

    def get_table_list_index(self, word):
        return self.reference_table_list.index(word)

    def get_list_dict(self, wid):
        lst = getattr(self, "{}_list".format(wid.objectName()))
        dic = getattr(self, "{}_dict".format(wid.objectName()))
        return lst, dic

    def set_table(self, wid):
        lst, dic = self.get_list_dict(wid)

        wid.setColumnCount(len(lst))
        wid.horizontalHeader().setStretchLastSection(True)
        views = []
        for c, l in enumerate(lst):
            if l in dic:
                if "view" in dic[l]:
                    views.append(dic[l]["view"])
                else:
                    views.append(l)

                if "width" in dic[l]:
                    wid.setColumnWidth(c, dic[l]["width"])
            else:
                views.append(l)

        wid.setHorizontalHeaderLabels(views)

    def reload(self):
        self.ui.reference_table.clearContents()
        self.ui.reference_table.setRowCount(0)
        references = kc_file_io.get_references()
        for reference in references:
            if not reference["trace"]:
                continue

            temp_path = reference["without_copy_number"].replace("_shade", "").replace("_hiColor", "")

            shade = temp_path.replace("{}.ma".format(reference["namespace"]), "{}_shade.ma".format(reference["namespace"]))
            if not "Camera" in temp_path:
                if os.path.exists(shade):
                    reference["shade_path"] = shade

                hiColor = temp_path.replace("{}.ma".format(reference["namespace"]), "{}_hiColor.ma".format(reference["namespace"]))
                if os.path.exists(hiColor):
                    reference["hiColor_path"] = hiColor

            for ref2 in references:
                if not ref2["trace"]:
                    continue

                if "_{}_".format(ref2["namespace"]) in reference["namespace"]:
                    reference["asset_namespace"] = ref2["namespace"]
        for reference in references:
            if not reference["trace"]:
                continue

            self.append_table(reference)

    def append_table(self, reference):
        r = self.ui.reference_table.rowCount()
        self.ui.reference_table.setRowCount(r+1)

        name = reference["namespace"]
        load = reference["is_loaded"]

        item = QtWidgets.QTableWidgetItem()
        item.setText(name)
        self.ui.reference_table.setItem(r, self.get_table_list_index("name"), item)

        load_btn = QtWidgets.QPushButton()
        if load:
            load_btn.setText("True")
            load_btn.setStyleSheet(self.true_color)
        else:
            load_btn.setText("False")
            load_btn.setStyleSheet(self.false_color)


        load_btn.info = reference
        load_btn.clicked.connect(self.load_ref_btn_clicked)
        self.ui.reference_table.setCellWidget(r, self.get_table_list_index("is_loaded"), load_btn)

        for each in self.btn_names:
            btn = QtWidgets.QPushButton()
            btn.setObjectName("{}_{:03d}_btn".format(each, r))
            btn.info = reference
            self.ui.reference_table.setCellWidget(r, self.get_table_list_index(each), btn)
            btn.clicked.connect(self.each_btn_clicked)
            btn.setText(each)
            if each == "shade" and "shade_path" not in reference:
                btn.setEnabled(False)
            if each == "hiColor" and "hiColor_path" not in reference:
                btn.setEnabled(False)

    def each_btn_clicked(self):
        category, num, name = self.sender().objectName().split("_")
        r = int(num)

        info = self.sender().info
        if category == "delete":
            if self.sender().text() == "delete":
                kc_file_io.remove_reference(info["node"], delete=True)
                if not cmds.objExists(info["node"]):
                    self.sender().setText("load")
                    self.sender().setStyleSheet(self.true_color)
            else:
                if info.get("asset_namespace", False):
                    kc_file_io.animation_reference(info["without_copy_number"], info["asset_namespace"])
                else:
                    kc_file_io.reference_file(info["namespace"], info["without_copy_number"])
                self.sender().setText("delete")
                self.sender().setStyleSheet(self.norm_color)

        elif category == "reload":
            kc_file_io.replace_reference(info["node"], info["without_copy_number"])

        elif category == "shade":
            kc_file_io.replace_reference(info["node"], info["shade_path"])
            pass

        elif category == "hiColor":
            kc_file_io.replace_reference(info["node"], info["hiColor_path"])

        elif category == "import":
            d, f = os.path.split(info["without_copy_number"])
            d = "{}/fbx".format(d.replace("/ma", ""))
            f = f.replace(".ma", ".fbx")
            fbx_path = "{}/{}".format(d, f)
            print fbx_path, os.path.exists(fbx_path)

            kc_file_io.remove_reference(info["node"], delete=True)
            kc_file_io.file_import(fbx_path)




    def load_ref_btn_clicked(self):
        if self.sender().text() == "True":
            kc_file_io.remove_reference(self.sender().info["node"], delete=False, unload=True)
            self.sender().setText("False")
            self.sender().setStyleSheet(self.false_color)
        else:
            kc_file_io.load_reference(self.sender().info["node"])
            self.sender().setText("True")
            self.sender().setStyleSheet(self.true_color)

    def do_btn_clicked(self):
        for info in kc_file_io.get_references():
            if not info["trace"]:
                continue
            if not info["is_loaded"]:
                continue
            path = info["without_copy_number"]
            if self.anim_path_keyword not in path:
                continue
            kc_file_io.remove_reference(info["node"], delete=True)

        QtWidgets.QMessageBox.information(self, "info", u"完了しました", QtWidgets.QMessageBox.Ok)


def start_app():
    kc_qt.start_app(KcReferenceReplacer, root=kc_qt.get_root_window(), name="KcReferenceReplacer")

if __name__ == "__main__":
    def get_root_mesh__TEST():
        x = KcReferenceReplacerCommand()
        print x.get_root()

    def set_poly_smooth__TEST():
        x = KcReferenceReplacerCommand()
        print x.set_poly_smooth(2)
    #cmds.file(r"H:\works\keica\data\material\Rollei_Pencil_08.ma", o=True, f=True)

    start_app()
    # set_poly_smooth__TEST()

