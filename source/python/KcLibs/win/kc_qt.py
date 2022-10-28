"""
# -*-coding: utf8 -*-
"""

import os
import sys
import importlib
import subprocess

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)


os.environ["QT_PREFERRED_BINDING"] = os.pathsep.join(["PySide", "PySide2"])

import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()


kc_app = importlib.import_module("KcLibs.{}.kc_app".format(kc_env.mode))
reload(kc_app)

from Qt import QtWidgets, QtCore, QtGui
if not kc_env.mode == "max":
    from Qt import QtCompat

if kc_env.mode in ["maya", "win"]:
    ROOT_WIDGET = QtWidgets.QMainWindow

elif kc_env.mode in ["max"]:
    ROOT_WIDGET = QtWidgets.QDialog

else:
    ROOT_WIDGET = QtWidgets.QWidget


class ConnectSignals(list):
    def __init__(self):
        self.connected = False
    
    def on(self):
        self._change(True)

    def off(self):
        self._change(False)
    
    def add(self, signal, function):
        self.append({"object": signal, "function": function})
    
    def _change(self, flg):
        if flg == self.connected:
            return

        for signal in self:
            if flg:
                signal["object"].connect(signal["function"])
            else:
                signal["object"].disconnect(signal["function"])
        
        self.connected = flg

def context_menu(widget, actions, function):
    menu = QtWidgets.QMenu()
    for action in actions:
        action_ = QtWidgets.QAction(action["name"], menu)
        action_.triggered.connect(action["function"])

        menu.addAction(action_)

    widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    widget.customContextMenuRequested.connect(function)
    return menu

def load_ui(ui_file, tool_instance=None):
    if kc_env.mode == "max":
        to_py_file = ui_file.replace(".ui", ".py")
        generate = False

        if os.path.exists(to_py_file):
            if os.stat(to_py_file).st_mtime < os.stat(ui_file).st_mtime:
                generate = True

        else:
            generate = True

        if generate:
            kc_app.compile_ui(ui_file)

        source = ui_file
        target = mod
        rel_path = os.path.relpath(source, target)
        rel_path, ext = os.path.splitext(rel_path)
        rel_path = rel_path.replace("\\", "/")
        import_path = ".".join(rel_path.replace(".py", "").split("/"))

        ui_module = importlib.import_module(import_path)
        form = ui_module.Ui_Form()
        form.setupUi(tool_instance)
		
        """
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(form)
        tool_instance.setLayout(layout)
        tool_instance.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		"""
		
        return form
    else:
        ui = QtCompat.loadUi(ui_file)
        if hasattr(tool_instance, "setCentralWidget"):
            tool_instance.setCentralWidget(ui)
        else:
            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(ui)
            tool_instance.setLayout(layout)
        return ui

def set_table(widget, lst, dic):
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


def get_root_window():
    app_ = QtWidgets.QApplication.instance()
    if not app_:
        return
    result = None
    if hasattr(app_, "activeWindow"):
        result, current = None, app_.activeWindow()
        while current:
            result, current = current, current.parent()
    else:
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.accessibleName() in ["Mainboard", "MainBoard"]:
                result = widget
                break

    return result


def start_app(tool_instance, **kwargs):
    for item in QtWidgets.QApplication.topLevelWidgets():
        if hasattr(item, "NAME") and "name" in kwargs:
            if item.NAME == kwargs["name"]:
                item.close()

    kwargs["root"] = get_root_window()
    kc_app.start_app(tool_instance, **kwargs)


if __name__ in ["__main__", "__builtin__"]:
    class TestWindow(ROOT_WIDGET):
        NAME = "TestWindow"
        def __init__(self, parent=None):
            super(TestWindow, self).__init__(parent)

        def set_ui(self):

            ui_path = "{}/source/python/KcTools/mobu/KcSetup/form/ui/main.ui".format(os.environ["KEICA_TOOL_PATH"])
            ui_path = "F:/works/keica/KcToolBox/source/python/KcTools/multi/KcSceneManager/form/ui/main.ui"
            self.ui = load_ui(ui_path, self)
            self.show()

    start_app(TestWindow, root=get_root_window())


