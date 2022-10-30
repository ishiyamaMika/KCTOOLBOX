# -*- coding: utf8 -*-

import os
import sys
import json
import copy
import re

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)
print(mod)
print(sys.path)
import KcLibs.core.kc_env as kc_env
import KcLibs.win.kc_qt as kc_qt
from KcLibs.win.kc_qt import QtWidgets, QtCore, QtGui

import KcLibs.maya.kc_mesh as kc_mesh


kc_env.append_sys_paths()

import maya.cmds as cmds
from functools import wraps
from puzzle2.PzLog import PzLog
import KcLibs.maya.kc_file_io as kc_file_io
import shutil
_LOG_ = PzLog("KcConvert", log_directory=kc_env.get_log_directory("KcConvert"))
_LOGGER_ = _LOG_.logger

def undo_chunk(func):
    def do(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        res = func(*args, **kwargs)
        cmds.undoInfo(closeChunk=True)
        return res
    return do

class KcConvert(kc_qt.ROOT_WIDGET):
    NAME = "KcConvert"

    def __init__(self, parent=None):
        super(KcConvert, self).__init__(parent)
        self.tool_directory = kc_env.get_tool_config("maya", self.NAME)

    def set_ui(self):
        ui_path = "{}/form/ui/main.ui".format(self.tool_directory)
        self.ui = kc_qt.load_ui(ui_path, self)
        self.ui.do_btn.clicked.connect(self.do_btn_clicked)

        self.show()

    def do_btn_clicked(self):

        current = cmds.file(sn=True, q=True)
        current_d, current_f = os.path.split(current)
        current_d = "{}/02_maya".format(current_d)
        if not os.path.exists(current_d):
            os.makedirs(current_d)

        current_f, current_ext = os.path.splitext(current_f)

        new_path = "{}/{}_convert{}".format(current_d, current_f, current_ext)

        print("=========", new_path)

        sx = cmds.getAttr("Reference.sx")
        sy = cmds.getAttr("Reference.sy")
        sz = cmds.getAttr("Reference.sz")

        cmds.setAttr("Reference.sx", 1)
        cmds.setAttr("Reference.sy", 1)
        cmds.setAttr("Reference.sz", 1)
        kc_file_io.save_file(new_path)

        mesh_list = cmds.listRelatives("Mesh", ad=True)
        joint_list = [l for l in cmds.listRelatives("Hips", ad=True)]

        kc_mesh.detach_bind(mesh_list)
        kc_mesh.set_poly_smooth(1, mesh_list)
        cmds.bakePartialHistory(all=True)
        kc_mesh.bind(mesh_list, joint_list)
        current = cmds.file(sn=True, q=True)
        temp_path = "{}/keica/temp/temp.ma".format(os.environ["TEMP"])

        if not os.path.exists(os.path.dirname(temp_path)):
            os.makedirs(os.path.dirname(temp_path))
        shutil.copy2(current, temp_path)
        kc_file_io.reference_file("TEMP", temp_path)

        for mesh in mesh_list:
            temp = "|".join(["TEMP:{}".format(l) for l in mesh.split("|") if l != ""])
            try:
                kc_mesh.copy_weight(temp, mesh)
                print(temp, mesh, "---done")
            except:
                import traceback
                print(traceback.format_exc())
                print(temp, mesh, "---failed")

        cmds.file(removeReference=True, referenceNode=cmds.ls(type="reference")[0])
        kc_mesh.remove_unused_influences(mesh_list)

        cmds.setAttr("Reference.sx", sx)
        cmds.setAttr("Reference.sy", sy)
        cmds.setAttr("Reference.sz", sz)

        kc_file_io.save_file()
        QtWidgets.QMessageBox.information(self, "info", u"完了しました", QtWidgets.QMessageBox.Ok)


def start_app():
    kc_qt.start_app(KcConvert, root=kc_qt.get_root_window(), name="KcConvert")

if __name__ == "__main__":
    def get_root_mesh__TEST():
        x = KcConvertCommand()
        print(x.get_root())

    def set_poly_smooth__TEST():
        x = KcConvertCommand()
        print(x.set_poly_smooth(2))
    #cmds.file(r"H:\works\keica\data\material\Rollei_Pencil_08.ma", o=True, f=True)

    start_app()
    # set_poly_smooth__TEST()
print(1)