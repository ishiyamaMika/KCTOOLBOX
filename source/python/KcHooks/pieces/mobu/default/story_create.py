#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mods = ["{}/source/python".format(os.environ["KEICA_TOOL_PATH"]), 
       "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])]

for mod in mods:
    if not mod in sys.path:
        sys.path.append(mod)


from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_story as kc_story
import KcLibs.mobu.kc_file_io as kc_file_io

_PIECE_NAME_ = "StoryCreate"

class StoryCreate(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(StoryCreate, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""


        asset_path = str(self.data["asset_path"])

        assets = self.pass_data["project"].get_assets()
        exists = False
        for asset in assets:
            if self.data["namespace"] == asset["namespace"]:
                exists = True

        if not exists:
            detail += u"assetを追加しました\n{}\n".format(asset_path)
            kc_file_io.file_merge(asset_path, str(self.data["namespace"]))
        else:
            detail += u"アセットはすでにシーンに存在します\n"

        plot_config_path = self.data["config"]["plot"]
        if not plot_config_path:
            header = u"設定ファイルがありませんでした: {}".format(self.data["namespace"])
            detail = u"path: {}".format(plot_config_path)
            self.logger.debug(header)
            return True, self.pass_data, header, detail

        info, models = self.pass_data["project"].sticky.read(plot_config_path)
        model_names = ["{}:{}".format(self.data["namespace"], l["name"]) for l in models]
        track = kc_story.create_story_track(str(self.data["namespace"]), model_names)

        kc_story.create_clip(track, str(self.data["export_path"]), offset=self.data["start"])

        if self.logger: self.logger.debug("update: {}".format(self.data["namespace"]))

        detail += "\n" + unicode(self.data)

        return flg, self.pass_data, u"storyのクリップを作成しました: {}".format(self.data["namespace"]), detail

if __name__ == "__builtin__":
    piece_data = {"paint": {
                        "asset_path": "mobu_sotai_path"
                        }
                 }
    data = {
           "namespace": "", 
           "name": "", 
           "category": "CH", 
           "number": 1, 
           "asset_path": ""
            }

    data = {u'asset_name': u'ABCDE',
           u'category': u'LO',
           u'config': {'export': 'E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/LO/ABCDE/MB/config/LO_ABCDE_asasad_export.json',
                       'plot': 'E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/LO/ABCDE/MB/config/LO_ABCDE_asasad_plot.json'},
           'cut': u'001',
           'end': 0,
           'mobu_edit_export_path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c001/master/export/ZIM_s01c001_anim_LO_ABCDE_asasad_02.fbx',
           'mobu_asset_path': 'E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/LO/ABCDE/MB/LO_ABCDE_asasad_sotai_t00.fbx',
           u'namespace': u'LO_ABCDE_asasad_02',
           'scene': u'01',
           u'selection': True,
           'start': 0,
           u'take': 0.0,
           u'true_namespace': u'LO_ABCDE_asasad',
           u'type': u'both',
           u'update_at': u'2021/11/23 13:33:10',
           u'update_by': u'amek',
           u'variation': u'asasad',
           u'version': 0.0}


    from KcLibs.core.KcProject import *

    kc_project = KcProject()
    kc_project.set("ZIM", "default")

    pass_data = {"project": kc_project}

    x = StoryCreate(piece_data=piece_data, data=data, pass_data=pass_data)
    x.execute()
