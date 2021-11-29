#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

import KcLibs.mobu.kc_group as kc_group

_PIECE_NAME_ = "AssetCreateFolder"

class AssetCreateFolder(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(AssetCreateFolder, self).__init__(**args)
        self.name = _PIECE_NAME_

        self.categories = {
            "Constraints": "<asset_name>_con",
            "Materials": "<asset_name>_mat",
            "VideoClips": "<asset_name>_vid",
            "Textures": "<asset_name>_tx",
            "Shaders": "<asset_name>_sha"
        }

    def execute(self):
        def _is_in_folder(item):
            if len([i for i in range(item.GetDstCount()) if isinstance(item.GetDst(i), FBFolder) and item.GetDst(i).Name != "Constraints"]) == 0:
                return False
            return True

        def _create_folder(name, item):
            return FBFolder(str(name), item)

        folders = {l.Name: l for l in FBSystem().Scene.Folders}
        flg = True
        header = ""
        detail = ""
        ignore_type = ["ORCharacterSolver_HIK", "FBCharacter"]
        ignore_name = ["Default Shader"]
        for category in self.categories.keys():
            name = self.categories[category].replace("<asset_name>", self.data["asset_name"])
            items = []
            for each in getattr(FBSystem().Scene, category):
                if each.ClassName() in ignore_type:
                    continue

                if each.LongName in ignore_name:
                    continue

                if _is_in_folder(each):
                    continue

                items.append(each)

            if len(items) > 0:
                if name in folders:
                    folder = folders[name]
                else:
                    item = items.pop(0)
                    folder = _create_folder(name, item)

                for item in items:
                    folder.ConnectSrc(item)





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

    x = AssetCreateFolder(piece_data=piece_data, data=data)
    x.execute()
