#-*- coding: utf8 -*-

import os
import sys
import re

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece
import KcLibs.mobu.kc_model as kc_model
reload(kc_model)
_PIECE_NAME_ = "GetAssets"

class GetAssets(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(GetAssets, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        def _number(namespace):
            search = re.search(".*_([0-9]*)", namespace)
            if search:
                groups = [l for l in search.groups() if not l == ""]
                if len(groups) > 0:
                    return int(groups[0])
            return 1

        flg = True
        header = ""
        detail = ""

        assets = []
        
        for meta_model in kc_model.find_models_by_name("*:meta"):
            meta_data = {}
            for meta_name in self.data["meta"]:
                meta_property = meta_model.PropertyList.Find(meta_name)
                if meta_property:
                    if meta_name == "namespace":
                        meta_name = "true_namespace"
                    meta_data[meta_name] = meta_property.Data
            namespace = meta_model.LongName.split(":")[0]
            meta_data["namespace"] = namespace

            assets.append(meta_data)
            if self.logger: self.logger.debug("namespace: {}".format(namespace))

        self.pass_data["assets"] = assets

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    piece_data = {"include_model": True}
    data = {"meta": ["namespace", "version", "take", "category"]}

    x = GetAssets(piece_data=piece_data, data=data)
    x.execute()
    import pprint
    pprint.pprint(x.pass_data)
