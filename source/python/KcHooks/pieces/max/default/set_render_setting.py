import os
import sys
import json
import pymxs
import glob

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.max.kc_file_io as kc_file_io
import KcLibs.max.kc_transport_time as kc_transport_time
import KcLibs.max.kc_render as kc_render

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

    def get_frames(self, directory, filters=None):
        def _cast(numbers):
            if len(numbers) == 0:
                return False
            elif len(numbers) == 1:
                return str(numbers[0])
            else:
                return "{}-{}".format(numbers[0], numbers[-1])
        modified_keys = []
        self.details.append("pattern: {}".format("{}/import/*_koma.json".format(directory)))
        for f in glob.glob("{}/import/*_koma.json".format(directory)):
            if "_cam_" in os.path.basename(f):
                continue
            
            if filters is not None:
                check = os.path.basename(f).replace("_koma.json", "")
                flg = False
                for each in filters:
                    if each in check:
                        flg = True
                        break
                
                if self.logger:
                    self.logger.debug("filter {}: {}".format(flg, check))
                if not flg:
                    continue

            self.details.append(f)
            js = json.load(open(f), "utf8")
            try:
                info, data = js["info"], js["data"]
            except:
                continue
            self.details.append(info["category"])
            if info["category"] != "koma data":
                continue

            modified_keys.extend(data["modified"])

        modified_keys = list(set(modified_keys))
        modified_keys.sort()

        lsts = []
        lst = list()
        for i, number in enumerate(modified_keys):
            if i == 0:
                lst.append(number)
                continue
        
            before = modified_keys[i-1]
            if number -1 == before:
                lst.append(number)
            else:
                lsts.append(lst)
                lst = list()
                lst.append(number)
            
        lsts.append(lst)

        render_frames = ",".join([_cast(l) for l in lsts if len(l) > 0])
        self.details.append(render_frames)
        return render_frames

    def execute(self):
        flg = True
        header = ""
        detail = ""

        kc_transport_time.set_scene_time(self.data["start"], self.data["end"], self.data["fps"])
        options = {}
        result = ""
        if "path" in self.data:
            render_frames = self.get_frames(os.path.dirname(self.data["path"]), self.data.get("filters", None))
            if self.logger: 
                self.logger.debug("render frames: {}".format(render_frames))
            else:
                print(result)

            options["render_frames"] = render_frames

        kc_render.setup(self.data["start"], 
                        self.data["end"], 
                        self.data["width"], 
                        self.data["height"], 
                        **options)

        header = "update render settings"
        detail = "start: {}\nend: {}\nwidth: {}\nheight: {}\nframes: {}\nkoma files: {}".format(self.data["start"], 
                                                                                                self.data["end"], 
                                                                                                self.data["width"], 
                                                                                                self.data["height"], 
                                                                                                result, 
                                                                                                "\n".join(self.details))

        self.pass_data["render_setup"] = {
                                          "start": self.data["start"],
                                          "end": self.data["end"],
                                          "width": self.data["width"],
                                          "height": self.data["height"],
                                          "options": options
                                         }

        return flg, self.pass_data, header, detail

if __name__ == "__main__":

    piece_data = {}

    path = "X:/Project/_942_ZIZ/3D/s99/c999/3D/master/ZIM_s99c500_anim.max"
    data = {"start": 12, "end": 50, "fps": 24, "width": 720, "height": 360, "path": path}
    x = SetRenderSetting(piece_data=piece_data, data=data)
