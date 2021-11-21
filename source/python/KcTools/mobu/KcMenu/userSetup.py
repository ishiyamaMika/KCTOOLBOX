# -*- coding: utf8 -*-

import os
import sys
import maya.utils as utils
import maya.cmds as cmds

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
import KcTools.maya.KcMenu.main as menu_main

def create_menus():
    menu_main.create_menu("{}/config/apps/maya/menu".format(kc_env.get_root_directory()))

if not cmds.about(batch=True):
    utils.executeDeferred(create_menus)


