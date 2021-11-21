#-*- coding: utf8 -*-

import os
import sys
import json
import pprint

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env

import KcLibs.mobu.kc_group as kc_group

reload(kc_env)
_PIECE_NAME_ = "AssetCreateJson"


class AssetCreateJson(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(AssetCreateJson, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        def _split(long_name):
            if ":" in long_name:
                name_s = long_name.split(":")
                namespace = ":".join(name_s[:-1])
                name = name_s[-1]
            else:
                namespace = False
                name = long_name

            return namespace, name

        flg = False
        header = ""
        detail = ""
        groups = {l.LongName: l for l in FBSystem().Scene.Groups}
        current_path = FBApplication().FBXFileName
        d, f = os.path.split(current_path)

        export_plot ={k: v for (k, v) in self.data["properties"].items() if k in ["export", "plot"]}
        
        for each, value in export_plot.items():
            m_list = FBModelList()
            FBGetSelectedModels(m_list)
            for m in m_list:
                m.Selected = False

            group = kc_group.get_group(value)
            if not group:
              continue
              
            item_names = []
            for item in group.Items:
                namespace, name = _split(item.LongName)
                item_names.append({"namespace": namespace, "name": name})

            info = kc_env.get_info(name="config json")

            path = "{}/config/{}_{}.json".format(d, self.data["namespace"], each)
            if not os.path.lexists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            json.dump({"info": info, "data": item_names}, 
                      open(path, "w"), "utf8", indent=4)

        return flg, self.pass_data, header, detail

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
                           'plot': 'tsukikQuad_plot', 
                           'namespace': 'CH_tsukikoQuad', 
                           'asset_name': 'tsukikoQuad', 
                           'version': 3, 
                           'export': 'tsukiko_quad', 
                           'take': 2}
            }

    x = AssetCreateJson(piece_data=piece_data, data=data)
    x.execute()
