import os
import sys
import pprint
import pymxs

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.max.kc_model as kc_model
_PIECE_NAME_ = "RenderScene"

class RenderScene(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(RenderScene, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        camera = kc_model.to_object(self.data["camera"])
        if camera is None:
            header = "no camera exists: {}".format(self.data["camera"])
        else:
            if not os.path.exists(os.path.dirname(self.data["movie_path"])):
                os.makedirs(os.path.dirname(self.data["movie_path"]))

            pymxs.runtime.viewport.setCamera(camera)
            pymxs.runtime.CreatePreview(start=self.data["start"], 
                                        end=self.data["end"],
                                        fps=self.data["fps"], 
                                        filename=self.data["movie_path"],
                                        percentSize=self.piece_data["scale_percent"])

            if os.path.exists(self.data["movie_path"]):
                header = "max scene preview successed"
                detail = "camera: {camera}\nstart: {start}\nend: {end}\nfps: {fps}\npath: {movie_path}".format(**self.data)
            else:
                header = "max scene preview failed"
                detail = "camera: {camera}\nstart: {start}\nend: {end}\nfps: {fps}\npath: {movie_path}".format(**self.data)
        
        return flg, self.pass_data, header, detail

if __name__ == "__main__":

    piece_data = {"scale_percent": 50}
    data = {
            "shot_name": "s99c999", 
            "end": 60, 
            "render_scale": 0.5, 
            "camera": "cam_s99c999:Merge_Camera",
            "start": 0, 
            "movie_path": "X:/Project/_942_ZIZ/3D/s99/c999/movie_convert/max/ZIM_s99c999_MB.avi", 
            "fps": 24, 
            "path": "X:/Project/_942_ZIZ/3D/s99/c999/3D/master/ZIM_s99c999_anim.max"
        }

    x = RenderScene(piece_data=piece_data, data=data)
    x.execute()
