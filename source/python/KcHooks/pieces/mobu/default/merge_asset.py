# -*- coding: utf8 -*-

import os
import sys

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_file_io as kc_file_io
import KcLibs.mobu.kc_model as kc_model

kc_env.append_sys_paths()

from puzzle2.PzLog import PzLog

TASK_NAME = "merge_asset"
DATA_KEY_REQUIRED = ["namespace", "asset_path"]

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger
    logger.debug("data: {}".format(data))
    return_code = 0

    if kc_file_io.file_merge(str(data["asset_path"]), namespace=data["namespace"]):
        logger.details.set_header(u"ファイルをマージしました: {}".format(data["asset_path"]))
        logger.debug(u"ファイルをマージしました: {}".format(data["asset_path"]))
        logger.details.add_detail(u"ファイルをマージしました: {}".format(data["asset_path"]))
    else:
        logger.details.set_header(u"ファイルをマージできませんでした: {}".format(data["asset_path"]))
        logger.warning(u"ファイルをマージできませんでした: {}".format(data["asset_path"]))
        logger.details.add_detail(u"ファイルをマージできませんでした: {}".format(data["asset_path"]))
        return_code = 1

    return {"return_code": return_code}


if __name__ == "__main__":
    data = {"namespace": ""}
    main(event={"data": data})
