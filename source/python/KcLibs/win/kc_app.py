# -*- coding: utf8 -*-


import os
import sys

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

kc_env.append_sys_paths()

os.environ["QT_PREFERRED_BINDING"] = os.pathsep.join(["PySide", "PySide2"])

from Qt import QtWidgets


def start_app(tool_instance, **kwargs):
    app = QtWidgets.QApplication(sys.argv)
    tool = tool_instance(kwargs.get("root", None))
    if "style" in kwargs:
    	app.setStyle(kwargs["style"])
    tool.options = kwargs
    tool.set_ui()
    app.exec_()