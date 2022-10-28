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
from KcLibs.core.KcProject import KcProject
import KcLibs.mobu.kc_key as kc_key
import KcLibs.mobu.kc_model as kc_model
reload(kc_key)
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
        def _ignore(model_name):
            return True
            ignores = ["_ctrlSpace", "_jtSpace"]
            for ignore in ignores:
                if ignore in model_name:
                    return False
            return True

        flg = True
        header = ""
        detail = ""
        
        """
        start = self.data["start"]
        end = self.data["end"]
        fps = self.pass_data["project"].config["general"]["fps"]
        """
        
        model_names = []
        for asset in self.data.get("assets", []):
            if not "config" in asset:
                continue
            config = asset["config"].get("plot")
            if self.logger:
                self.logger.debug("config path: {}".format(config))
            if not config:
                continue

            if not os.path.lexists(config):
                continue
            
            info, data = self.pass_data["project"].sticky.read(config)
            for d in data:
                if not _ignore(d):
                    continue
                model_names.append("{}:{}".format(asset["namespace"], d["name"]))

        kc_model.select(model_names)

        print("select camera models")
        print("plot")
        header = u"plotしました: {}".format(len(model_names))
        detail = "plot:\n" + "\n".join(model_names)
        kc_key.plot_selected()

        if "interpolate" in self.piece_data:
            m_list = FBModelList()
            FBGetSelectedModels(m_list)
            stepped = kc_key.change_key_to_stepped([l for l in m_list])
            detail += u"\n\nstepped:\n"
            detail += u"\n".join(stepped)
            if self.logger:
                self.logger.debug("change key to stepped")

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {'path': "E:/works/client/keica/data/assets"}


    data = {
            "start": 0,
            "end": 100,
            "assets": [{"namespace": "", "name": "", "category": "CH", "number": 1}, 
                       {"namespace": "", "name": "", "category": "camera"}]
            }

    x = PlotAll(piece_data=piece_data, data=data)
    x.execute()
