import sys
import os

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_model as kc_model

from puzzle2.PzLog import PzLog

TASK_NAME = "asset_add_root"

def main(event={}, context={}):

    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    root_name = data["root_name"]
    root_model = kc_model.find_model_by_name(root_name, ignore_namespace=True)
    if root_model:
        logger.details.set_header(u"rootモデルがすでに存在します")
        return {"return_code": 0}
    
    

    



    


    return {"return_code": return_code}


if __name__ == "__main__":
    data = {"": ""}
    main(event={"data": data})