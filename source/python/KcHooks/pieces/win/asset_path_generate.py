import os
import sys
import pprint
import glob
sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_model as kc_model
from KcLibs.core.KcProject import KcProject
from puzzle2.PzLog import PzLog

TASK_NAME = "asset_path_generate"
from pyfbsdk import *
def main(event={}, context={}):
    """
    this may create a new asset path
    then pass it to the next task
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger
    
    return_code = 0
    update_context = {}
    asset_dependency_paths_cache = data.get("asset_dependency_paths_cache", {})
    namespace_paths = asset_dependency_paths_cache.get(data["namespace"], {})
    if len(namespace_paths) > 0:
        for k, v in namespace_paths.items():
            logger.debug("{}: {}".format(k, v))
            logger.details.add_detail("{}: {}".format(k, v))
            update_context[k] = v
        logger.details.set_header(return_code, u"関連パスをcontextから取得しました")
        # return code 2 for skipping to result view
        return {"return_code": 2, "update_context": update_context}
    else:
        update_context.setdefault("asset_dependency_paths_cache", {})
        update_context["asset_dependency_paths_cache"].setdefault(data["namespace"], {})
        meta_name = "{}:meta".format(data["namespace"])
        meta = kc_model.to_object(meta_name)
        if meta:
            take = meta.PropertyList.Find("take")
            if take:
                data["take"] = int(take.Data)

        data["version"] = "*"
        if data["category"] == "CH":
            data["sub_category"] = "*"

        asset_dependency_paths = data.get("asset_dependency_paths", {})
        for k, v in asset_dependency_paths.items():
            path = data["project"].path_generate(v, data)
            if "*" in path:
                paths = glob.glob(path)
                paths.sort()
                if len(paths) > 0:
                    paths.sort()
                    path = paths[-1]

            update_context["{}.{}".format(TASK_NAME, k)] = path.replace("\\", "/")
            update_context["asset_dependency_paths_cache"][data["namespace"]]["{}.{}".format(TASK_NAME, k)] = path.replace("\\", "/")

        update_context["{}.take".format(TASK_NAME)] = data["take"]
        update_context["asset_dependency_paths_cache"][data["namespace"]]["{}.take".format(TASK_NAME)] = data["take"]

        for k, v in update_context.items():
            if k == "asset_dependency_paths_cache":
                continue
            logger.debug("{}: {}".format(k, v))
            logger.details.add_detail("{}: {}".format(k, v))

        logger.details.set_header(return_code, u"関連パスを生成しました")

        return {"return_code": 2, "update_context": update_context}


if __name__ == "builtins":
    project = KcProject()
    project.set("DTN", 
                "default")


    data = {'asset_dependency_paths': {'export': '<asset_root>/<category>/models/CH_<asset_name>_export.json',
                            'mobu_sotai_path': '<asset_root>/<category>/sotai/CH_<asset_name>_sotai_t<take>.fbx',
                            'plot': '<asset_root>/<category>/models/CH_<asset_name>_plot.json',
                            'rig_path': '<asset_root>/<category>/<sub_category>/CH_<asset_name>_t<take>_<version>.fbx'},
            'asset_name': 'WULMtg',
            'category': 'CH',
            'config': {'export': 'K:/DTN/LO/Asset_keica/CH/models/CH_WULMtg_export.json',
                        'plot': 'K:/DTN/LO/Asset_keica/CH/models/CH_WULMtg_plot.json'},
            'cut': 'A9000-A9002',
            'end': 120,
            'mobu_edit_export_path': 'K:/DTN/LO/A_S99/A_S99_A9000-A9002/master/export/DTN_S99_A9000-A9002_anim_CH_WULMtg.fbx',
            'mobu_sotai_path': 'K:/DTN/LO/Asset_keica/CH/sotai\\CH_WULMtg_sotai_t01.fbx',
            'namespace': 'CH_WULMtg',
            'part': 'A',
            'progress': 'anim',
            'project': project,
            'rig_path': 'K:/DTN/LO/Asset_keica/CH/*/CH_WULMtg_t*_*.fbx',
            'root_directory': 'K:/DTN',
            'scene': 0,
            'selection': True,
            'seq': 'S99',
            'shot_root': 'K:/DTN/LO',
            'start': 0,
            'sub_category': '*',
            'take': '*',
            'true_namespace': 'CH_WULMtg',
            'type': 'config',
            'update_at': '2022/11/17 17:27:20',
            'update_by': 'moriyama',
            'user': 'amek',
            'version': '*'}

    main(event={"data": data})