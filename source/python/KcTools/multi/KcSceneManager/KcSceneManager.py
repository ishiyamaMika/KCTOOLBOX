import os
import sys

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()

import KcTools.multi.KcSceneManager.form.main as scene_manager
scene_manager.start_app()
