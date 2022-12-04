#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_file_io as kc_file_io
import KcLibs.mobu.kc_story as kc_story

from puzzle2.PzLog import PzLog

TASK_NAME = "file_publsh"


def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0
    kc_story.delete_tracks()
    if kc_file_io.file_save(data["publish_path"]):
        logger.details.set_header(return_code, u"ファイルを保存しました: {}".format(os.path.basename(data["publish_path"])))
        logger.debug(u"ファイルを保存しました: {}".format(data["publish_path"]))
        logger.details.add_detail(u"\nファイルを保存しました: \n{}".format(data["publish_path"]))
    else:
        return_code = 1
        logger.details.set_header(return_code, u"ファイルを保存できませんでした: {}".format(os.path.basename(data["publish_path"])))
        logger.warning(u"ファイルを保存できませんでした: {}".format(data["publish_path"]))
        logger.details.add_detail(u"\nファイルを保存できませんでした: \n{}".format(data["publish_path"]))

    return {"return_code": return_code}


if __name__ == "__main__":
    data = {"": ""}
    main(event={"data": data})