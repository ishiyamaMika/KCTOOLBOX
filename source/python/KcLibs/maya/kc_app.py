# -*- coding: utf8 -*-


import os
import sys
from maya import OpenMayaUI

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
print mod

if mod not in sys.path:
    sys.path.append(mod)
import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()

from Qt import QtWidgets, QtCompat

def start_app(tool_instance, **kwargs):
    maya_main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    maya_main_window = QtCompat.wrapInstance(long(maya_main_window_ptr), QtWidgets.QWidget)
    main = tool_instance(maya_main_window)
    main.options = kwargs
    main.set_ui()
    main.show()