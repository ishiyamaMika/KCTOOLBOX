#-*-coding: utf8-*-

import os
import sys
import re
import yaml
import copy
import subprocess
import json
import datetime
import fnmatch

mods = ["{}/source/python".format(os.environ["KEICA_TOOL_PATH"]), "{}/python".format(os.environ["CENTRUM_PATH"])]

for mod in mods:
    if mod not in sys.path:
        sys.path.append(mod)

import KcLibs.win.kc_sg as kc_sg


def split_by(path):
    dic = {}
    for d in os.listdir(path):
        full_path = "{}/{}".format(path, d)
        if not os.path.isdir(full_path):
            continue
        files = [l for l in os.listdir(full_path) if not os.path.isdir("{}/{}".format(full_path, l)) and l != "Thumbs.db"]
        files.sort()
        if len(files) == 0:
            continue

        name_s = d.split("_")
        if "Line" in d and not "__" in d:
            continue
        type_ = "_".join(name_s[1:])
        if "__" in d:
            d_s = d.split("__")
            temp = d_s[1]
            temp_s = temp.split("_")
            type_ = "_".join(temp_s[1:])
        name = name_s[0] 
        dic.setdefault(name, {})
        dic[name][type_] = {}
        if len(files) > 0:
            dic[name][type_]["path"] = "{}/{}".format(full_path, files[0])
        dic[name][type_]["duration"] = (len(files))/24.0

        dic[name][type_]["name"] = d
        dic[name][type_]["folder"] = name

    return dic

def sort_by_order(ls, order):
    a = []
    set_a = set(ls)
    set_b = set([l.split("{")[0] for l in order])
    not_exists = list(set_a - set_b)

    for o in order:
        if "{" in o:
            o_ = o.split("{")[0]
        else:
            o_ = o
        for l in ls:
            if o_ == l:
                if "{" in o:
                    a.append(o)
                else:
                    a.append(l)

    a.extend(not_exists)
    return a

def create_ae_config(path, width, height, folder):
    dic = split_by(path)
    yml_path = "{}/source/python/KcTools/aftereffects/autoComp/base_comp.yml".format(os.environ["KEICA_TOOL_PATH"])
    y = yaml.load(open(yml_path, "r"))

    order = y["order"]
    comps = []
    for k, v in dic.items():
        comp_info = {} 
        comp_info["info"] = {
                            "name": "{}_comp".format(k),
                            "width": width, 
                            "height": height,
                            "folder": folder
                            }

        keys = sort_by_order(v.keys(), order)
        if len(keys) > 0:
            comp_info["info"]["duration"] = v[keys[0].split("{")[0]]["duration"]
        else:
            continue
        layers = []
        for key in keys:
            layer = copy.deepcopy(y["settings"].get(key, {}).get("common", {}))
            if re.match(".*[0-9]{2}$", k):
                true_name = k[:-2]
            else:
                true_name = k

            override = copy.deepcopy(y["settings"].get(key, {}))
            ov_settings = {}
            for kk in override.keys():
                if fnmatch.fnmatch(true_name, kk):
                    ov_settings = override[kk]
                    break

            #ov_settings = copy.deepcopy(y["settings"].get(key, {}).get(true_name, {}))
            layer.update(ov_settings)
            if "enabled" not in layer:
                layer["enabled"] = True
            key_ = key.split("{")[0]

            # layer["name"] = "{}_{}".format(k, key_)
            layer.update(v[key_])
            layers.append(layer)
        layers.append({"primitive": "solid", "color": [1, 1, 1], "enabled": True})
        comp_info["layers"] = layers[::-1]
        comps.append(comp_info)

    return {"compositions": comps}


if os.environ["KEICA_TOOL_PATH"][0] == "H":
    debug = True
else:
    debug = False


print(debug)

if len(sys.argv) < 2:
    print("you need to set shot directory: exit")
    sys.exit()

shot_name = sys.argv[-1]
match = re.match("(ep00)(s.*)(c[0-9]{3}[A-Z]{1})", shot_name)
if not match:
    match = re.match("(ep00)(s.*)(c[0-9]{3})", shot_name)

if not match:
    print("shot name pattern failed: {}".format(sys.argv[-1]))
    sys.exit()

episode, scene, cut = match.groups()
root_directory = "X:/Project/_952_SA/04_animation/CP/{}/{}/{}".format(episode, scene, cut)
footage_path = "{}/footage".format(root_directory)

if not os.path.exists(footage_path):
    print("footage folder not exists: exit")
    sys.exit()    

shot = os.path.basename(root_directory)
scene = os.path.basename(os.path.dirname(root_directory))

shot_name = "ep00{}{}".format(scene, shot)

shot_info = kc_sg.get_scene_info(shot_name)

if not shot_info:
    print("shot name not in shotgun: exit")
    sys.exit()

print(shot_name)

data = create_ae_config(footage_path, shot_info["width"], shot_info["height"], shot_name)
now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

if debug:
    data_path = "X:/usr/hattori/autoCompTest/{}_{}.json".format(shot_name, now)
    if not os.path.exists(os.path.dirname(data_path)):
        os.makedirs(os.path.dirname(data_path))

else:
    data_path = "{}/{}_{}.json".format(root_directory, shot_name, now)
json.dump(data, open(data_path, "w"), "utf8", indent=4)

env_copy = os.environ.copy()
env_copy["__AUTOCOMP_DATA_PATH__"] = data_path.replace("/", "\\")
env_copy["__AUTOCOMP_SAVE_PATH__"] = data_path.replace("/", "\\").replace(".json", ".aep")
ae_path = os.environ["__AE_PATH__"].replace("/", "\\")
jsx_path = "{}\\source\\python\\KcTools\\aftereffects\\autoComp\\src\\auto_comp.jsx".format(os.environ["KEICA_TOOL_PATH"])
jsx_path = jsx_path.replace("/", "\\")
print("save data:", env_copy["__AUTOCOMP_SAVE_PATH__"])
subprocess.Popen([ae_path, "-r", jsx_path], env=env_copy, shell=False).wait()
print("done")

