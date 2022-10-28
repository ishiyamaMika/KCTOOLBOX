# -*- coding: utf8 -*-

import os
import sys
import importlib

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

os.environ["QT_PREFERRED_BINDING"] = os.pathsep.join(["PySide", "PySide2"])