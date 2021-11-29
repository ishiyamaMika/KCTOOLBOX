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
import KcLibs.mobu.kc_file_io as kc_file_io
reload(kc_model)
_PIECE_NAME_ = "AssetExport"

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

        if self.data["category"] == "cam":
            return flg, self.pass_data, header, detail
        
        if self.piece_data.get("varidate"):
            return varidate()
        else:
            return main()

    def varidate(self):
        export_path = self.data["config"].get("export")
        if not export_path:
            return False, self.pass_data, "export path is not exists: {}".format(export_path), ""

        info, models = self.pass_data["project"].sticky.read(export_path)

        model_names = ["{}:{}".format(self.data["namespace"], l["name"]) for l in models]

        models = kc_model.select(model_names)
        
        if len(model_names) != len(models):
            return False, self.pass_data, "model count not same", ""

    def main(self):
        kc_model.unselected_all()

        export_path = self.data["config"].get("export")
        if not export_path:
            return flg, self.pass_data, header, detail

        info, models = self.pass_data["project"].sticky.read(export_path)

        model_names = ["{}:{}".format(self.data["namespace"], l["name"]) for l in models]

        models = kc_model.select(model_names)
        if len(model_names) == len(models):
            self.logger.debug("models is all selected: {}".format(self.data["namespace"]))
            kc_file_io.file_save(str(self.data["export_path"]), selection=True)

        else:
            models_ = set([l.LongName for l in models])
            model_names_ = set(model_names)
            self.logger.warning("this model is not selected: {}: {}".format(self.data["namespace"]), " ".join(list(model_names_-models_)))

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {'path': "E:/works/client/keica/data/assets"}
    data = {
            "namespace": "", 
            "name": "", 
            "category": "CH", 
            "number": 1
            }

    x = AssetExport(piece_data=piece_data, data=data)
    x.execute()
