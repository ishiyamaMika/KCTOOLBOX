from inspect import trace
import os
import sys
import json

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()
from KcLibs.core.KcProject import KcProject


from puzzle.Piece import Piece


_PIECE_NAME_ = "CreateDirectories"

class CreateDirectories(Piece):
    def __init__(self, **args):
        super(CreateDirectories, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = "create directories"
        detail = ""
        path = self.data["path"]
        cut_root = os.path.normpath(os.path.join(path, "../../../"))
        directories = ["_OUTPUT",
                       "aep",
                       "aep/_Sozai",
                       "aep/render",
                       "3D",
                       "3D/edit",
                       "3D/rend"
                       ]
        
        for group in self.data["groups"]:
            directories.append("aep/render/{}".format(group))

        for each in directories:
            directory = "{}/{}".format(cut_root, each)
            if not os.path.lexists(directory):
                try:
                    os.makedirs(directory)
                    detail += u"create successed: {}\n".format(directory)
                    if self.logger:
                        self.logger.debug(u"create successed: {}".format(directory))
                except:
                    detail += u"create failed   : {}\n".format(directory)
                    if self.logger:
                        self.logger.debug(u"create failed   : {}".format(directory))

        return flg, self.pass_data, header, detail

if __name__ in ["__main__", "__builtin__"]:
    piece_data = {}
    data = {
            "shot_name": "s99c500",
            "end": 40,
            "render_scale": 0.5,
            "start": 0,
            "camera": "cam_s99c500:Merge_Camera",
            "movie_path": "X:/Project/_942_ZIZ/3D/s99/c500/movie_convert/max/ZIM_s99c500_max.avi",
            "fps": 8,
            "path": "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/s99/c500/3D/master/ZIM_s99c500_anim.max"
        }

    x = CreateDirectories(piece_data=piece_data, data=data)
    x.execute()
