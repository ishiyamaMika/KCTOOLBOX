# -*- coding: utf8 -*-

import os
import sys
import json
import copy
import traceback
import time
import datetime
import importlib
import shutil
import glob

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

from KcLibs.core.KcProject import *
import KcLibs.core.kc_env as kc_env

logger = kc_env.get_logger("temp")

x = KcProject(logger=logger)
logger.debug("TEMP")
x.set("ZIM", "default")

x.set_tool_config("multi", "KcSceneManager")

data = {'primary':
          {u'cut': u'005',
           'end': 20,
           'fps': 8,
           'movie_path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c005/edit/mov_edit/ZIM_s01c005_anim_t01_02_amek.mov',
           'path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c005/edit/ZIM_s01c005_anim_t01_02_amek_ANIM.fbx',
           u'progress': u'ANIM',
           u'project': u'ZIM',
           u'project_variation': u'home',
           u'scene': u'01',
           'shot_name': 's01c005',
           'start': 10,
           u'take': u'01',
           'user': 'amek',
           u'version': u'02'}
        }

results = x.puzzle_play(x.tool_config["puzzle"]["mobu_edit_render"], 
                    data, 
                    {"project": x}, 
                    ["primary"])

for result in results[1]:
    print result