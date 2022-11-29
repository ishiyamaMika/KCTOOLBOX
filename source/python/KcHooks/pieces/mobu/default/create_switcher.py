#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

from puzzle2.PzLog import PzLog
import KcLibs.mobu.kc_camera as kc_camera

TASK_NAME = "create_switcher"
DATA_KEY_REQUIRED = ["switcher_path"]

def main(event={}, context={}):
    """
    create switcher from setting file

    key required from data:
        switcher_path: setting path of switcher
    """

    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    info, data_ = kc_env.load_config(data["switcher_path"])
    logger.debug("data: {}".format(data_))
    logger.details.add_detail("data: {}".format(data_))

    return_code = 0
    try:
        kc_camera.set_switcher(data_, clear_all=True)
        logger.details.set_header(u"スイッチャーを作成しました")
    except BaseException:
        import traceback
        traceback.print_exc()
        logger.details.set_header(u"スイッチャーを作成できませんでした")    

    logger.details.add_detail(u"switcher path: {}".format(data["switcher_path"]))

    kc_camera.change_cam("switcher")

    return {"return_code": return_code}


if __name__ in ["__main__", "__builtin__", "builtins"]:
    data = {"switcher_path": "K:/DTN/3D/s00/cA9000-A9999/master/export/DTN_s00cA9000-A9999_Cam_AA9000-A9999.fbx.switcher.json"}
    data = {"switcher_path": "K:/DTN/LO/A_S99/A_S99_A9000-A9002/master/export/DTN_S99_A9000-A9002.fbx.switcher.json"}
    main(event={"data": data})