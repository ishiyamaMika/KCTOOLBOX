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


#palette_tools_startup.py
if "PALETTE_TOOLS" in os.environ:
    sys.path.append("%s\\python" % os.environ["PALETTE_TOOLS"])
    sys.path.append("%s\\python\\lib\\site-packages" % os.environ["PALETTE_TOOLS"])
    menu = "%s\\config\\app\\%s" % (os.environ["PALETTE_TOOLS"], "menu.py")
    try:
        FBApplication().ExecuteScript(menu)
    except:
        pass
