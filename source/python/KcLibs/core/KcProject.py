#-*-coding: utf-*-
import os
import sys
import codecs
import json
import re
import copy

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])

if not mod in sys.path:
    sys.path.append(mod)


import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()

import yaml

from Sticky.Sticky import FieldValueGenerator, StickyConfig
from puzzle.Puzzle import Puzzle

class KcProject(object):
    def __init__(self):
        self.puzzle = Puzzle()
        self.field_generator = FieldValueGenerator()
        self.sticky = StickyConfig()
        self.project_variations = self.get_project_variations()

    def get_project_variations(self):
        app_directory = kc_env.get_app_config("env", "projects")
        projects = [l for l in os.listdir(app_directory) if l != "_base_.yml"]
        project_variations = {}
        template = "(.*)_(.*).yml"
        for project in projects:
            search = re.search(template, project)
            if search:
                project, variation = search.groups()
                project_variations.setdefault(project, []).append(variation)
        return project_variations

    def set(self, name, variation="default"):
        self.name = name
        self.variation = variation
        self.set_project_config()

    def set_project_config(self):
        self.config_directory = kc_env.get_app_config("env", "projects")
        self.config = self.get_config(self.config_directory)

    def get_config(self, directory):
        config_path = "{}/{}_{}.yml".format(directory, self.name, self.variation)
        if not os.path.exists(config_path):
            config_path = "{}/{}_default.yml".format(directory, self.name)

            if not os.path.exists(config_path):
                config_path = "{}/_base_.yml".format(directory)

        files = self.sticky.get_override_file_list(config_path)

        config_data = {}
        for f in files:
            override_info, override_data = self.sticky.read(f)
            config_data = self.sticky.values_override(config_data, override_data, use_field_value=False)

        extra_fields = {"<{}>".format(k): v for (k, v) in config_data.get("extra_fields", {}).items()}
        extra_fields_ = {}
        for k, v in extra_fields.items():
            extra_fields_[k] = self.field_generator.generate(v, extra_fields)

        config_data["extra_fields"] = extra_fields_
        return config_data

    def set_tool_config(self, app, tool_name):
        self.tool_config_directory = kc_env.get_app_config(app, tool_name)
        self.tool_config = self.get_config(self.tool_config_directory)

    def get_cameras(self):
        piece_data = self.config["puzzle"]["get_cameras"]
        self.puzzle.pass_data = {}

        self.puzzle.play(piece_data, {}, {})

        return self.puzzle.pass_data.get("cameras", [])

    def get_assets(self):
        piece_data = self.config["puzzle"]["get_assets"]
        self.puzzle.pass_data = {}

        self.puzzle.play(piece_data, {"main": {"meta": self.config["asset"]["meta"]}}, {})

        return self.puzzle.pass_data.get("assets", [])

    def path_generate(self, template, fields):
        fields_ = copy.deepcopy(fields)
        for k, v in fields_.items():
            if not "<" in k:
                key = "<{}>".format(k)
                if key in self.config["general"]["padding"]:

                    padding = "{{:0{}d}}".format(self.config["general"]["padding"][key])
                    if isinstance(v, (int, float)):
                        fields_[key] = padding.format(int(v))
                    else:
                        fields_[key] = v
                else:
                    fields_[key] = str(v)

        fields_["<project>"] = self.name

        fields_.update(self.config["extra_fields"])

        return self.field_generator.generate(template, fields_)

    def path_split(self, template, path):
        return self.field_generator.get_field_value(template, path)

if __name__ in ["__main__", "__builtin__"]:
    x = KcProject()
    x.set("ZIM", "home")
    x.set_tool_config("multi", "KcSceneManager")

    import pprint
    pprint.pprint(x.config)
    print
    print
    pprint.pprint(x.tool_config)
    template = "<asset_root>/<category>/<asset_name>/MB/<category>_<asset_name>_t<take>_<version>.fbx"
    print x.path_generate(template, 
                          {"category": "CH", 
                           "asset_name": "hanakoQuad", 
                           "take": 1, 
                           "version": 1})

    print x.get_cameras()

    
    assets = x.get_assets() + x.get_cameras()

    print
    print 
    print 
    print 
    config_assets =  [
            {
                "category": "ch", 
                "selection": True, 
                "namespace": "CH_tsukikoQuad", 
                "update_at": "2021/11/18 01:17:16", 
                "take": 2.0, 
                "update_by": "amek", 
                "type": "config"
            }, 
            {
                "category": "cam", 
                "selection": True, 
                "name": "cam_root", 
                "config": {
                    "plot": False, 
                    "export": False
                }, 
                "namespace": "cam_s01c001", 
                "number": 1, 
                "type": "both"
            }
        ]

    pprint.pprint(assets)
    print

    a = set([l["namespace"] for l in assets])
    b = set([l["namespace"] for l in config_assets])

    both = a & b
    a_only = a - b
    b_only = b - a

    for i, asset in enumerate(assets):
        i = len(assets) - 1 - i
        asset = assets[i]
        for b in both:
            if b == asset["namespace"]:
                assets.pop(i)

    merge_assets = {}
    add_namespace = []
    for asset in assets + config_assets:
        if asset["namespace"] in add_namespace:
            continue

        if asset["namespace"] in both:
            asset["type"] = "both"
        elif asset["namespace"] in a_only:
            asset["type"] = "scene"
        else:
            asset["type"] = "config"

        merge_assets.setdefault(asset["category"], []).append(asset)
        add_namespace.append(asset["namespace"])

    keys = merge_assets.keys()
    keys.sort()

    list_assets = []
    for key in keys:
        datas = merge_assets[key]
        sorted(datas, key=lambda x: x["namespace"])
        list_assets.extend(datas)
    print 
    print 
    pprint.pprint(list_assets)