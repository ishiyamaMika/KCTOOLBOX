import os
import sys
import json
import pprint
import pymxs
import glob

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.max.kc_file_io as kc_file_io
# import KcLibs.mobu.kc_transport_time as kc_transport_time

reload(kc_file_io)
_PIECE_NAME_ = "SetRenderSetting"

class SetRenderSetting(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(SetRenderSetting, self).__init__(**args)
        self.name = _PIECE_NAME_
        self.details = []

    def get_frames(self, directory):
        def _cast(numbers):
            if len(numbers) == 1:
                return str(numbers[0])
            else:
                return "{}-{}".format(numbers[0], numbers[-1])

        modified_keys = []
        self.details.append("pattern: {}".format("{}/import/*_koma.json".format(directory)))
        for f in glob.glob("{}/import/*_koma.json".format(directory)):
            self.details.append(f)
            if "_cam_" in os.path.basename(f):
                continue
            js = json.load(open(f), "utf8")
            try:
                info, data = js["info"], js["data"]
            except:
                continue
            if info["category"] != "koma data":
                continue

            for node, keys in data["modified"].items():
                for trs in keys["list"]:
                    for k, v in trs.items():
                        for v2 in v:
                            if v2 is None:
                                continue
                            if v2["changed"]:
                                if v2["frame"] not in modified_keys:
                                    modified_keys.append(v2["frame"])

        modified = list(set(modified_keys))
        modified.sort()

        lst = list()
        lsts = []
        for i, number in enumerate(modified):
            if i == 0:
                lst.append(number)
                continue

            before = modified[i-1]
            if number - 1 == before:
                lst.append(number)
            else:
                lsts.append(lst)
                lst = list()
                lst.append(number)

        results = ",".join([_cast(l) for l in lsts])

        return results

    def execute(self):
        flg = True
        header = ""
        detail = ""

        pymxs.runtime.rendStart = self.data["start"]
        pymxs.runtime.rendEnd = self.data["end"]
        pymxs.runtime.renderWidth = self.data["width"]
        pymxs.runtime.renderHeight = self.data["height"]
        result = self.get_frames(os.path.dirname(self.data["path"]))
        pymxs.runtime.rendPickupFrames = result

        header = "update render settings"
        detail = "start: {}\nend: {}\nwidth: {}\nheight: {}\nframes: {}\nkoma files: {}".format(self.data["start"], 
                                                                                                self.data["end"], 
                                                                                                self.data["width"], 
                                                                                                self.data["height"], 
                                                                                                result, 
                                                                                                "\n".join(self.details))
        return flg, self.pass_data, header, detail

if __name__ == "__main__":

    piece_data = {}
    data = {"start": 12, "end": 50, "width": 720, "height": 360}

    x = SetRenderSetting(piece_data=piece_data, data=data)
    x.execute()
