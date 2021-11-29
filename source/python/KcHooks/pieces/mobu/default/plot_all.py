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
import KcLibs.mobu.kc_model as kc_model

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

        start = self.data["start"]
        end = self.data["end"]
        fps = self.pass_data["project"].config["general"]["fps"]
        model_names = []
        for asset in self.data.get("assets", []):
            if not "config" in asset:
                continue
            config = asset["config"].get("plot")
            if not config:
                continue

            print config

            if not os.path.lexists(config):
                continue
            
            info, data = self.pass_data["project"].sticky.read(config)
            for d in data:
                model_names.append("{}:{}".format(asset["namespace"], d["name"]))

        kc_model.select(model_names)

        print "select camera models"
        print "plot"
        print len(model_names)
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
