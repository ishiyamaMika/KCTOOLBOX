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

import KcLibs.mobu.kc_group as kc_group

from puzzle2.PzLog import PzLog

TASK_NAME = "asset_create_json"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    def _split(long_name):
        if ":" in long_name:
            name_s = long_name.split(":")
            namespace = ":".join(name_s[:-1])
            name = name_s[-1]
        else:
            namespace = False
            name = long_name

        return namespace, name

    flg = True
    groups = {l.LongName: l for l in FBSystem().Scene.Groups}
    current_path = FBApplication().FBXFileName
    d, f = os.path.split(current_path)

    export_plot = {k: v for (k, v) in data["properties"].items() if k in ["export", "plot"]}
    error = []
    for each, value in export_plot.items():
        m_list = FBModelList()
        FBGetSelectedModels(m_list)
        for m in m_list:
            m.Selected = False
        group = kc_group.get_group(value)
        if not group:
            return_code = 1
            logger.details.add_detail("group not exists: {}".format(value))
            continue
            
        item_names = []
        for item in group.Items:
            namespace, name = _split(item.LongName)
            item_names.append({"namespace": namespace, "name": name})

        info = kc_env.get_info(name="config json")

        if len(item_names) == 0:
            return_code = 1
            logger.details.add_detail(u"group item is empty: pass")
            print("group item is empty")

        else:
            if "config_path" in data:
                path = data["config_path"]
                path = path.replace("<config_type>", each)

            else:
                if "root_directory" in data:
                    d = data["root_directory"]

                path = "{}/config/{}_{}.json".format(d, data["namespace"], each)

            kc_env.save_config(path, "model names", "asset", item_names)

    return {"return_code": return_code}

if __name__ == "__builtin__":

    piece_data = {'groups': [{'file_name': '<namespace>_plot.json',
                  'name': '<namespace>_plot'},
                   {
                   'file_name': '<namespace>_export.json', 'name': None}],
                   'name': 'create_json',
                   'path': 'E:/works/client/keica/data/json',
                   'piece': 'KcHooks.pieces.mobu.default.asset_create_json',
                   'view': 'create json(_plot, _export)',
                   'widgets': [{'btn': {'find': 'plot',
                                        'function': 'get_groups',
                                        'icon': 'reload.png'},
                              'name': 'plot',
                              'widget': 'QComboBox'},
                             {'btn': {'find': 'export',
                                      'function': 'get_groups',
                                      'icon': 'reload.png'},
                              'name': 'export',
                              'widget': 'QComboBox'}]}

    data = {'namespace': 'Mia',
            'properties': {'category': 'CH', 
                           'plot': 'tsukikoQuad_plot', 
                           'namespace': 'Mia', 
                           'asset_name': 'tsukikoQuad', 
                           'version': 3, 
                           'export': 'tsukiko_quad', 
                           'take': 2}
            }

    print(main({"data": data}))

