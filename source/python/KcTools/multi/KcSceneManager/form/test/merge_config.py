# -*- coding: utf8 -*-

import os
import sys
import json


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import *



class HOGE(object):
    def __init__(self):
        self.project = KcProject()
        self.project.set("ZIM", "default")

    def list_asset_table(self, config_assets):
        assets = {l["namespace"]: l for l in self.project.get_assets()}
        config_assets_dict = {l["namespace"]: l for l in config_assets}

        a = set(assets.keys())
        b = set(config_assets_dict.keys())

        both = a & b
        a_only = a - b
        b_only = b - a

        print(both)
        print(a_only)
        print(b_only)

        merge_assets = {}
        add_namespace = []

        scene_assets = []

        for asset in both:
            add = config_assets_dict[asset]
            add["type"] = "both"
            scene_assets.append(add)

        for asset in a_only:
            add = assets[asset]
            add["type"] = "scene"
            scene_assets.append(add)

        for asset in b_only:
            add = config_assets_dict[asset]
            add["type"] = "scene"
            scene_assets.append(add)

        sorted(scene_assets, key=lambda x: x["namespace"])

        return scene_assets


x = HOGE()

config_assets = [
            {
                "category": "CH", 
                "selection": True, 
                "namespace": "CH_tsukikoQuad", 
                "update_at": "2021/11/19 03:05:35", 
                "asset_name": "tsukikoQuad", 
                "version": 2.0, 
                "take": 2.0, 
                "update_by": "amek", 
                "type": "both", 
                "true_namespace": "CH_tsukikoQuad"
            }, 
            {
                "category": "CH", 
                "namespace": "CH_tsukikoQuad_02", 
                "update_at": "2021/11/19 03:05:35", 
                "asset_name": "tsukikoQuad", 
                "version": 2.0, 
                "take": 2.0, 
                "update_by": "amek", 
                "type": "both", 
                "true_namespace": "CH_tsukikoQuad"
            }
        ]

results = x.list_asset_table(config_assets)