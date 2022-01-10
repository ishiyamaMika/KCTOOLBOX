#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)
from puzzle.Piece import Piece

import KcLibs.mobu.kc_transport_time as kc_transport_time

_PIECE_NAME_ = "ChangeTime"

class ChangeTime(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(ChangeTime, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = str(self.piece_data)
        detail = ""

        if self.piece_data["mode"] == "change":
            self.pass_data[_PIECE_NAME_] = kc_transport_time.get_scene_time()
            
            if self.piece_data["fps"] != self.data["fps"]:
                if self.piece_data["fps"] > self.data["fps"]:
                    value = self.piece_data["fps"] / self.data["fps"]
                    start = self.data["start"] * value
                    end = self.data["end"] * value + (value-1)
                else:
                    value = self.data["fps"] / self.piece_data["fps"]
                    start = self.data["start"] / value
                    end = self.data["end"] / value

                fps = self.piece_data["fps"]
            else:
                start = self.data["start"]
                end = self.data["end"]
                fps = self.piece_data["fps"]

            kc_transport_time.set_scene_time(loop_start=start, 
                                             loop_stop=end, 
                                             zoom_start=start, 
                                             zoom_stop=end, 
                                             fps=fps)

            new_time = kc_transport_time.get_scene_time()

            detail = "change time to: {}-{}({}) -> {}-{}({})".format(self.data["start"],
                                                                     self.data["end"],
                                                                     self.data["fps"],
                                                                     new_time["loop_start"], 
                                                                     new_time["loop_stop"], 
                                                                     new_time["fps"])
            self.pass_data["@start"] = start
            self.pass_data["@end"] = end
            self.pass_data["@fps"] = fps

            header = u"シーンのフレームを変更しました"
            if self.logger: self.logger.debug(detail)
            
        elif self.piece_data["mode"] == "revert":
            header = "revert scene time"
            if _PIECE_NAME_ in self.pass_data:
                detail = "revert time to: {}-{}({})".format(self.pass_data[_PIECE_NAME_]["loop_start"], 
                                                            self.pass_data[_PIECE_NAME_]["loop_stop"], 
                                                            self.pass_data[_PIECE_NAME_]["fps"])

                header = u"シーンのフレームを戻しました"
                kc_transport_time.set_scene_time(**self.pass_data[_PIECE_NAME_])
                if self.logger: self.logger.debug(detail)
            else:
                header = u"シーンのフレームは変更されていませんでした"

        return flg, self.pass_data, header, detail

from KcLibs.core.KcProject import *
import KcLibs.core.kc_env as kc_env

if __name__ == "__builtin__":
    piece_data = {"fps": 24}
    
    data ={u'cut': u'005',
           'start': 0,
           'end': 8,
           'fps': 8,
           'movie_path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c005/edit/mov_edit/ZIM_s01c005_anim_t01_02_amek.fbx',
           'path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c005/edit/ZIM_s01c005_anim_t01_02_amek_ANIM.fbx',
           u'progress': u'ANIM',
           u'project': u'ZIM',
           u'project_variation': u'home',
           u'scene': u'01',
           'shot_name': 's01c005',
           u'take': u'01',
           'user': 'amek',
           "render_fps": 24,
           u'version': u'02'}

    pass_data = {"ChangeTime": {
                            "loop_start": 10,
                            "loop_stop": 100,
                            "zoom_start": 10,
                            "zoom_stop": 100,
                            "fps": 8
                            }
                     }

    piece_data["mode"] = "change"

    x = ChangeTime(piece_data=piece_data, data=data, pass_data=pass_data)
    x.execute()