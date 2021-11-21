# -*- coding: utf8 -*-

import os
import sys
import importlib

if os.environ["KEICA_TOOL_PATH"] not in sys.path: 
    sys.path.append("{}/source/python".format(os.environ["KEICA_TOOL_PATH"]))


if not mod_path in sys.path:
    sys.path.append(mod_path)    

os.environ["QT_PREFERRED_BINDING"] = os.pathsep.join(["PySide", "PySide2"])