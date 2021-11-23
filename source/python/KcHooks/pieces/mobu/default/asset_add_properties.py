#-*- coding: utf8 -*-

import os
import sys
import random
import datetime

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_model as kc_model


_PIECE_NAME_ = "AssetAddProperties"

class AssetAddProperties(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(AssetAddProperties, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = False
        header = ""
        detail = ""
        root_model_name = self.piece_data["parent_name"].replace("<namespace>", self.data["namespace"])

        model = kc_model.find_model_by_name(self.piece_data["parent_name"].split(":")[-1], ignore_namespace=True)

        meta_model = kc_model.find_model_by_name("meta", ignore_namespace=True)

        if not meta_model:
            meta_model = FBModelMarker("meta")
            if model:
                model.ConnectSrc(meta_model)

        property_list = {l.Name: l for l in meta_model.PropertyList if l.Name != ""}
        take = -1
        for prop in self.data["meta"]:
            if not prop in self.data["properties"]:
                continue

            value = self.data["properties"][prop]

            if isinstance(value, int):
                create_type = "number"

            elif isinstance(value, float):
                create_type = "double"

            else:
                create_type = "String"
                value = str(value)

            if prop in property_list:
                print "already exists"
                property_list[prop].Data = value
            else:
                if meta_model.PropertyList.Find(str(prop)):
                    meta_model.PropertyList.Find(str(prop)).Data = value
                else:
                    kc_model.create_custom_property(meta_model, prop, create_type, value)

            if prop == "take":
                take = value

        if take > 0:
            color = self.piece_data["color"].get(take, "random")
            if color == "random":
                color = (random.randint(0, 255)/255.0, random.randint(0, 255)/255.0, random.randint(0, 255)/255.0)

            meta_model.Color = FBColor(*color)
       
        now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        if "update_at" in property_list:
            property_list["update_at"].Data = now
        else:
            kc_model.create_custom_property(meta_model, "update_at", "String", now)
        
        if "update_by" in property_list:
            property_list["update_by"].Data = kc_env.get_user()
        else:
            kc_model.create_custom_property(meta_model, "update_by", "String", kc_env.get_user())
        

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    data = {
            "namespace": "CH_tsukikoQuad",
            "properties": {"namespace": "CH_tsukikoQuad", 
                           "asset_name": "tsukikoQuad",
                           "variation": "TEST",
                           "take": 2,
                           "version": 1, 
                           "category": "CH"},
            "meta": [
                     "namespace",
                     "asset_name",
                     "variation",
                     "take",
                     "version",
                     "category",
                     "update_at",
                     "update_by"]   
            }
    piece_data = {
            "parent_name": "root",
            "meta_model_name": "<namespace>:meta",
            "color": {
                1: (255, 0, 0),
                2: (0, 255, 0),
                3: (0, 0, 255),
                4: (255, 255, 0),
                5: (0, 255, 255),
                6: (255, 0, 255),
                7: (255, 255, 255),
                8: (0, 0, 0)
                }
            }

    x = AssetAddProperties(piece_data=piece_data, data=data)
    x.execute()
