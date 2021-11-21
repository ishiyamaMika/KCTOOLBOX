#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

_PIECE_NAME_ = "GetCameras"

class GetCameras(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(GetCameras, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = False
        header = ""
        detail = ""


        cameras = []
        for each in FBSystem().Scene.Cameras:
            if each.SystemCamera:
                continue
            cam_s = each.LongName.split(":")
            if len(cam_s) == 1:
                namespace = False
            else:
                namespace = cam_s[0]

            if not namespace:
                continue

            name = each.Name
            if self.piece_data.get("include_model"):
                cameras.append({"namespace": namespace, "name": name, "model": each, "category": "cam"})
            else:
                cameras.append({"namespace": namespace, "name": name, "category": "cam"})

        self.pass_data["cameras"] = cameras
        print "XXXXXXXXXXXXXXXXXXX", cameras

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    piece_data = {"include_model": True}
    data = {}

    x = GetCameras(piece_data=piece_data, data=data)
    x.execute()

    print x.pass_data
