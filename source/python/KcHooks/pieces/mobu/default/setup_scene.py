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
import KcLibs.mobu.kc_model as kc_model

_PIECE_NAME_ = "SetupCamera"

class SetupCamera(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(SetupCamera, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = "add light and hide models"
        detail = ""

        for each in [-90, 0, 90, 180]:
            light = FBLight("light_{}".format(each))
            light.Show = True
            light.PropertyList.Find("Type").Data = 1
            light.Rotation = FBVector3d(each, 0, 90)
        
        for each in FBSystem().Scene.RootModel.Children:
            for child in each.Children:
                if not child.Name == "GEO":
                    m_list = FBModelList()
                    FBGetSelectedModels(m_list, child, False)
                    for m in m_list:
                        m.Show = False

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {}

    data = {
           "namespace": "camera name",
           "width": 1920,
           "height": 1080
            }

    x = SetupCamera(piece_data=piece_data, data=data)
    x.execute()
