import os
import copy   
import random

base = {
    "scene": -1,
    "cut": -1,
    "assets": [],
    "start": 1,
    "end": 1000, 
    "paths": {
        "mobu": {
            "edit": "X:/keica/test_s{:03d}c{:04d}_edit_v01.fbx",
            "master": "X:/keica/test_s{:03d}c{:04d}_master.fbx"
        }
    }
}   
import json
root = "F:/works/keica/data/KcSceneManagerTest/ZIZ/s{:02d}_c{:04d}.json"
root = "E:/works/client/keica/data/SceneManagerTest/ZIZ/s{:02d}_c{:04d}.json"

def asset_(name):
    return {"name": name, "selection": random.randint(0, 100) > 50}

for i in range(1, 10):
    for ii in range(1, 1000):
        path = root.format(i, ii)
        data = copy.deepcopy(base)
        data["scene"] = i
        data["cut"] = ii
        data["start"] = random.randint(0, 100)
        data["end"] = data["start"] + random.randint(0, 1000)
        data["assets"] = [asset_(l) for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if random.randint(0, 10) > 7]
        data["paths"]["mobu"]["edit"] = data["paths"]["mobu"]["edit"].format(i, ii)
        data["paths"]["mobu"]["master"] = data["paths"]["mobu"]["master"].format(i, ii)

        info = {"name": "SceneManager"}
        if random.randint(0, 500) > 400:
            info["user"] = os.environ.get("KEICA_USERNAME", os.environ["USERNAME"])
        else:
            info["user"] = "others"

        json.dump({"info": info, "data": data}, open(path, "w"), "utf8", indent=4)