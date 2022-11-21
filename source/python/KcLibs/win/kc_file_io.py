import os
import json


def load_json(config_path):
    js = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            try:
                js = json.load(f)
            except ValueError:
                raise Exception("json load error: {}".format(config_path))

    return js


def dump_json(config_path, data):
    if not os.path.exists(os.path.dirname(config_path)):
        os.makedirs(os.path.dirname(config_path))

    try:
        json.dump(data, open(config_path, "w", encoding="utf8"), ensure_ascii=False, indent=4)
        return True
    except BaseException:
        json.dump(data, open(config_path, "w"), "utf8", indent=4)
        return False
