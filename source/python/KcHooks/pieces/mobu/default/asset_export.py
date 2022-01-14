#-*- coding: utf8 -*-

import os
import sys
import json

from pyfbsdk import *


mods = ["{}/source/python".format(os.environ["KEICA_TOOL_PATH"]), 
       "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])]

for mod in mods:
    if not mod in sys.path:
        sys.path.append(mod)


from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_model as kc_model
import KcLibs.mobu.kc_file_io as kc_file_io
reload(kc_model)
_PIECE_NAME_ = "AssetExport"

from KcLibs.core.KcProject import *


class AssetExport(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(AssetExport, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""
        print "AssetExport---"

        if self.piece_data.get("mode") == "varidate":
            return self.varidate()
        else:
            return self.main()

    def varidate(self):
        import re

        export_path = self.data["export_path"]
        if not export_path:
            return True, self.pass_data, u"[error] エクスポートパスを作成できませんでした: {} > {}".format(self.data["namespace"], export_path), ""

        if not self.data["config"]["export"]:
            return True, self.pass_data, u"[error] 設定ファイルパスを作成できませんでした: {}".format(self.data["namespace"]), ""

        if not os.path.exists(self.data["config"]["export"]):
            return True, self.pass_data, u"[error] 設定ファイルパスが存在しませんでした: {}".format(self.data["namespace"]), ""

        
        asset_directory = os.path.normpath(os.path.join(self.data["config"]["export"], "../../"))
        paths = self.pass_data["project"].config["asset"]["mobu"]["paths"]

        asset_meta = self.pass_data["project"].get_asset(self.data["namespace"])
        if not asset_meta:
            return True, self.pass_data, u"[error] metaモデルがアセットに設定されていません: {}".format(self.data["namespace"]), ""

        take_versions = []
        for each in os.listdir(asset_directory):
            if not each.lower().endswith(".fbx"):
                continue

            asset_path = "{}/{}".format(asset_directory, each)

            if self.data["category"] in paths:
                template = paths[self.data["category"]]["rig"]
            else:
                template = paths["default"]["rig"]

            fields = self.pass_data["project"].path_split(template, asset_path)
            if "<take>" in fields:
                try:
                    take_versions.append([int(fields["<take>"]), int(fields["<version>"])])
                except:
                    continue

        take_versions.sort()
        if len(take_versions) == 0:
            return True, self.pass_data, u"[error] アセットファイルが存在しません: {}".format(self.data["namespace"]), ""
        
        if asset_meta["take"] < take_versions[-1][0]:
            return True, self.pass_data, u"[error] シーン中のアセットのテイクが違います: {} ({} {}) < ({} {})".format(self.data["namespace"], int(asset_meta["take"]), int(asset_meta["version"]), take_versions[-1][0], take_versions[-1][1]), ""

        info, models = self.pass_data["project"].sticky.read(self.data["config"]["export"])
        model_names = ["{}:{}".format(self.data["namespace"], l["name"]) for l in models]

        models = kc_model.to_object(model_names) or []

        if len(model_names) != len(models):
            diff = list(set(model_names) | set([l.LongName for l in models]))
            return True, self.pass_data, u"[error] 設定ファイルとシーンのモデルの数が違います: {} ({})".format(self.data["namespace"], len(diff)), u"以下のmodelがありません\n{}".format("\n".join(diff))

        return True, self.pass_data, u"設定ファイルとシーンのモデル数は一致しています: {}".format(self.data["namespace"]), ""

    def main(self):
        def _ignore(model_name):
            ignores = ["_ctrlSpace_", "_jtSpace_"]
            for ignore in ignores:
                if ignore in model_name:
                    return False
            return True

        kc_model.unselected_all()
        flg = True

        info, models = self.pass_data["project"].sticky.read(self.data["config"]["export"])

        model_names = ["{}:{}".format(self.data["namespace"], l["name"]) for l in models if _ignore(l["name"])]

        models = kc_model.select(model_names)
        if self.data["category"] == "camera":
            for model in models:
                if isinstance(model, FBCamera):
                    self.pass_data["@camera"] = model.LongName
                    self.pass_data["@width"] = model.ResolutionWidth
                    self.pass_data["@height"] = model.ResolutionHeight
                    break

        if len(model_names) == len(models):
            self.logger.debug("models is all selected: {}".format(self.data["namespace"]))
            kc_file_io.file_save(str(self.data["export_path"]), selection=True)

        else:
            models_ = set([l.LongName for l in models])
            model_names_ = set(model_names)
            self.logger.warning("this model is not selected: {}: {}".format(self.data["namespace"], " ".join(list(model_names_-models_))))

        header = u"ファイルをエクスポートしました: {}".format(self.data["namespace"])
        detail = u"path: \n{}".format(self.data["export_path"])

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    x = KcProject()
    x.set("ZIM", "home")
    piece_data = {'path': "E:/works/client/keica/data/assets", 
                  "mode": "varidate", 
                  "paint": 
                    {
                        "export_path": "mobu_edit_export_path"}
                    }

    data = {u'category': u'CH',
           'config': {'export': False, 'plot': False},
           'cut': u'001',
           'end': 0,
           'mobu_edit_export_path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c001/master/export/ZIM_s01c001_anim_CH_tsukikoQuad.fbx',
            u'config': {'export': "E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/tsukikoQuad/MB/config/CH_tsukikoQuad_export.json",
                            'plot': "E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/tsukikoQuad/MB/config/CH_tsukikoQuad_plot.json"},
           'mobu_sotai_path': False,
           u'namespace': u'CH_tsukikoQuad',
           'scene': u'01',
           u'selection': True,
           'start': 0,
           u'take': 2.0,
           u'true_namespace': u'CH_tsukikoQuad',
           u'type': u'both',
           u'update_at': u'2021/11/18 01:17:16',
           u'update_by': u'amek'}

    x = AssetExport(piece_data=piece_data, data=data, pass_data={"project": x})
    print x.execute()
