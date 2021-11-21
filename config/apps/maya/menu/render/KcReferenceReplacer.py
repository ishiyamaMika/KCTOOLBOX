# -*- coding: utf8 -*-

import os
import sys

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()

import KcTools.maya.KcReferenceReplacer.form.main as main

main.start_app()
