#-*- coding: utf8 -*-

import os
import sys
import json
import pprint

from pyfbsdk import *


mods = ["{}/source/python".format(os.environ["KEICA_TOOL_PATH"]), 
       "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])]

for mod in mods:
    if not mod in sys.path:
        sys.path.append(mod)

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import KcProject
import KcLibs.mobu.kc_key as kc_key

_PIECE_NAME_ = "PlotAll"

class PlotAll(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(PlotAll, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""
        print "PlotAll---"

        kc_project = KcProject()
        kc_project.set("ZIZ")

        start = self.data["start"]
        end = self.data["end"]
        fps = kc_project.config["general"]["fps"]

        for asset in self.data.get("assets", []):
            print asset

        print "select camera models"
        print "plot"
        kc_key.plot_selected()

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {'path': "E:/works/client/keica/data/assets"}


    data = {
            "start": 0,
            "end": 100,
            "assets": [{"namespace": "", "name": "", "category": "CH", "number": 1}, 
                       {"namespace": "", "name": "", "category": "cam"}]
            }

    x = PlotAll(piece_data=piece_data, data=data)
    x.execute()
