#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

import KcLibs.mobu.kc_transport_time as kc_transport_time
reload(kc_transport_time)
_PIECE_NAME_ = "ChangeCamera"

class ChangeCamera(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(ChangeCamera, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        cameras = []
        for cam in FBSystem().Scene.Cameras:
            if cam.SystemCamera:
                continue
            if cam.LongName.startswith("{}:".format(self.data["namespace"])):
                app = FBApplication()
                app.SwitchViewerCamera(cam)
                kc_transport_time.set_zoom_time(self.data["start"], 
                                                self.data["stop"],
                                                self.data["fps"])
                FBSystem().Scene.Evaluate()



        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    piece_data = {"include_model": True}
    data = {"namespace": "cam_s01c006A", "start": 10, "stop": 30, "fps": 8}

    x = ChangeCamera(piece_data=piece_data, data=data)
    x.execute()

