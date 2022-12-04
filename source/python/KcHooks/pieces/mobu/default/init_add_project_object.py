
# -*- coding: utf8 -*-

import os
import sys
import pprint

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

mod = "{}/source/python/site-packages/py3".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import KcProject

from puzzle2.PzLog import PzLog

TASK_NAME = "init_add_project_object"

def main(event={}, context={}):
    data = event.get("data", {})
    update_context = {}
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    if data.get("project_setup"):
        x = KcProject(logger=logger)
        x.set(data["project_setup"]["project"], 
              data["project_setup"]["variation"])

        x.set_tool_config(data["project_setup"]["category"], 
                          data["project_setup"]["tool_name"])

        update_context["common"] = {}
        update_context["common"]["project"] = x
        logger.debug("add project object to context: {}({})".format(data["project_setup"]["project"],
                                                                    data["project_setup"]["variation"]))

        logger.details.set_header(return_code, u"プロジェクトオブジェクトをコンテキストに追加しました: {}".format(data["project_setup"]["project"]))
        logger.details.add_detail(u"プロジェクトオブジェクトをコンテキストに追加しました: {}".format(data["project_setup"]["project"]))

    return_code = 0

    return {"return_code": return_code, "update_context": update_context}


if __name__ == "__main__":
    data = {"": ""}
    main(event={"data": data})