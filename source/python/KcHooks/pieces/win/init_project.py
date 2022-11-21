# -*- coding: utf8 -*-

import os
import sys

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

from KcLibs.core.KcProject import KcProject

from puzzle2.PzLog import PzLog

TASK_NAME = "init_project"

def main(event={}, context={}):
    """
    add project object to the data
    """

    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    update_context = {}
    if "project" in data:
        if isinstance(data["project"], dict):
            project = KcProject(logger_name="temp_puzzle_process")
            project.set(data["project"]["name"], data["project"]["variation"])
            if "tool" in data["project"]:
                project.set_tool_config(*data["project"]["tool"])

            update_context["common"] = {"project": project}
            logger.debug("add project to common: {}".format(update_context["common"]))
            logger.details.add_detail("add project to common: {}".format(update_context["common"]))

    return_code = 2

    return {"return_code": return_code, "update_context": update_context}

if __name__ == "builtins":
    data = {"project": {"name": "DTN", "variation": "default", "tool": ["multi", "KcSceneManager"]}}
    main(event={"data": data})
