#-*- coding: utf8 -*-

import os
import sys
import json
import re

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

import KcLibs.mobu.kc_model as kc_model
import KcLibs.mobu.kc_file_io as kc_file_io
from puzzle2.PzLog import PzLog

TASK_NAME = "export_sequencer"

def main(event={}, context={}):
    """
    export sequencer
    """

    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    


    return {"return_code": return_code}


if __name__ == "__main__":
    data = {"": ""}
    main(event={"data": data})