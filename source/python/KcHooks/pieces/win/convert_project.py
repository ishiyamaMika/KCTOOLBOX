import os
import sys

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

from KcLibs.core.KcProject import KcProject

from puzzle2.PzLog import PzLog

TASK_NAME = "convert_project"
DATA_KEY_REQUIRED = [""]

def main(event={}, context={}):
    """
    pass_data: project_info, project
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    flg = True

    if "project_info" in data:
        project = KcProject()
        project.set(data["project_info"]["name"], 
                    data["project_info"]["variation"])
        

        data["{}.project".format(TASK_NAME)] = project
        del data["project_info"]
        logger.debug("cast project object")
   
    return {"return_code": return_code}

if __name__ == "__builtin__":
    piece_data = {"include_model": True}
    data = {"namespace": "cam_s01c006A", "start": 10, "stop": 30, "fps": 8}

    data.update(piece_data)
    main({"data": data})
