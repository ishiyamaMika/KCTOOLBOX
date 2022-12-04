#-*- coding: utf8 -*-

import os
import sys
import json

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_file_io as file_io


from puzzle2.PzLog import PzLog

TASK_NAME = "file_save"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    logger.debug("file save: {}".format(data["path"]))

    flg = True
    path = data["path"]
    if not os.path.lexists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    
    file_io.file_save(path)
    header = u"ファイルを保存しました: {}".format(os.path.basename(path))
    detail = u"path\n{}".format(path)

    logger.details.set_header(return_code, header)
    logger.details.add_detail(detail)
    return {"return_code": return_code}

if __name__ == "__builtin__":

    piece_data = {'path': "E:/works/client/keica/data/assets"}

    data = {'namespace': 'Mia',
            'properties': [{'name': 'category', 'value': 'CH'},
                {'name': 'plot', 'value': 'Mia_plot'},
                {'name': 'major', 'value': 1},
                {'name': 'namespace', 'value': 'Mia'},
                {'name': 'export', 'value': 'Mia_export'},
                {'name': 'minor', 'value': 1}]}
    
    data.update(piece_data)
    main({"data": data})


 