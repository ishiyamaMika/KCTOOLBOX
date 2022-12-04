#-*-coding: utf8-*-
import os
import sys
import glob

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import KcProject

from puzzle2.PzLog import PzLog

TASK_NAME = "remove_files"

def main(event={}, context={}):
    """
    piece_data: patterns
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    flg = True
    header = ""
    detail = ""

    for each in self.piece_data["patterns"]:
        if each["root"] not in data:
            if logger:
                logger.debug("root is not exists: {}".format(each["root"]))
                logger.debug("root is not keys: {}".format(", ".join(data.keys())))
            continue
        remove_path = os.path.normpath(os.path.join(data[each["root"]], each["target"]))
        files = glob.glob(remove_path)
        if logger:logger.debug("root path: {}".format(remove_path))
        for f in files:
            try:
                os.remove(f)
                detail += "removed: {}\n".format(f)
                if logger: 
                    logger.debug("removed: {}".format(f))
            except:
                detail += "remove failed: {}\n".format(f)
                if logger: 
                    logger.debug("remove failed: {}".format(f))
    if detail == "":
        header = u"削除するkomaファイルがありませんでした"
    else:
        header = u"既存のkomaファイルを削除しました"
    logger.details.set_header(return_code, header)
    logger.details.add_detail(detail)
    return {"return_code": return_code}

if __name__ == "__builtin__":
    piece_data = {"patterns": [{"root": "path", "target": "../import/*_koma.json"}]}
    path = "X:/Project/_942_ZIZ/3D/s99/c999/3D/master/ZIM_s99c999_anim.max"
    data = {"path": path}

    data.update(piece_data)
    main({"data": data})
