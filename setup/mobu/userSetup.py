# -*- coding: utf8 -*-

import os
import sys
from pyfbsdk import FBApplication

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
import KcTools.mobu.KcMenu.main as menu_main

menu_main.create_menu("{}/config/apps/mobu/menu".format(kc_env.get_root_directory()))