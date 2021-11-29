#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

import KcLibs.mobu.kc_group as kc_group

_PIECE_NAME_ = "AssetCreateGroups"

class AssetCreateGroups(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(AssetCreateGroups, self).__init__(**args)
        self.name = _PIECE_NAME_

    def get_all_models(self):
        self.models = []
        for model in FBSystem().Scene.RootModel.Children:
            if "_Ctrl:Reference" in model.LongName:
                continue

            m_list = FBModelList()
            FBGetSelectedModels(m_list, model, False)
            self.models.extend([l for l in m_list])

    def geometry(self):
        items = []
        for model in self.models:
            if model.ClassName() == "FBModel":
                items.append(model)

        return items

    def skeleton(self):
        items = []
        for model in self.models:
            if model.ClassName() == "FBModelSkeleton":
                items.append(model)

        return items

    def others(self):
        items = []
        ignore_type = ["ORCharacterSolver_HIK"]
        ignore_name = ["Default Shader"]
        for category in ["Constraints", "Materials", "Shaders", "Textures", "VideoClips"]:
            for each in getattr(FBSystem().Scene, category):
                if each.ClassName() in ignore_type:
                    continue

                if each.LongName in ignore_name:
                    continue

                items.append(each)
        return items


    def execute(self):
        flg = True
        header = ""
        detail = ""

        self.scene_groups = {}

        self.get_all_models()

        for group in FBSystem().Scene.Groups:
            name = "/".join([l.LongName for l in kc_group.get_group_hierachy(group)])
            self.scene_groups[name] = group

        def _create(name):
            name_s = name.split("/")
            parent = None
            for i in range(len(name_s)):
                group_name = "/".join(name_s[:i+1])
                if not group_name in self.scene_groups:
                    name = group_name.split("/")[-1]
                    parent = False
                    parent_name = "/".join(group_name.split("/")[:-1])
                    if parent_name in self.scene_groups:
                        parent = self.scene_groups[parent_name]

                    group = FBGroup(name)
                    if parent:
                        parent.ConnectSrc(group)
                        
                    self.scene_groups[group_name] = group

        for group_setting in self.piece_data["groups"]:
            group_name = group_setting["template"].replace("<asset_name>", self.data["asset_name"])
            _create(group_name)

            group = self.scene_groups[group_name]

            if "category" in group_setting:
                items = getattr(self, group_setting["category"])()
                for item in items:
                    group.ConnectSrc(item)

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    data = {"asset_name": "tsukikoQuad"}
    piece_data = {
          "groups": [
                {"template": "<asset_name>_top"},
                {"template": "<asset_name>_top/<asset_name>_geo",
                 "category": "geometry"},
                {"template": "<asset_name>_top/<asset_name>_skl", 
                 "category": "skeleton"},
                {"template": "<asset_name>_top/<asset_name>_plot"},
                {"template": "<asset_name>_top/<asset_name>_export"},
                {"template": "<asset_name>_topABC/<asset_name>_exporta/AAAAA", 
                 "category": "others"}
                ]
            }

    x = AssetCreateGroups(piece_data=piece_data, data=data)
    x.execute()
