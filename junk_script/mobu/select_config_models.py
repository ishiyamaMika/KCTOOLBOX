import json
import glob
import os
from pyfbsdk import *

path = r"X:\Project\_942_ZIZ\2020_ikimono_movie\_work\14_partC_Japan\26_animation\_3D_assets\CH\usaoSS\MB\config\CH_usaoSS_plot.json"

current = FBApplication().FBXFileName
res = FBMessageBox("info", "type?", "plot", "export")

d, f = os.path.split(current)

if res == 1:
    path_ = "{}/config/*_plot.json".format(d)
elif res == 2:
    path_ = "{}/config/*_export.json".format(d)
else:
    path_ = False

if path_:
    paths = glob.glob(path_)    
    if len(paths) > 0:
        js = json.load(open(paths[0], "r"))

        for each in js["data"]:
            name = "{}:{}".format(each["namespace"], each["name"])
            comps = FBComponentList()
            
            FBFindObjectsByName(name, comps)
            for comp in comps:
                comp.Selected = True
            