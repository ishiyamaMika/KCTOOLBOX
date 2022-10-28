import os
import sys
import json


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.max.kc_file_io as kc_file_io
# import KcLibs.mobu.kc_transport_time as kc_transport_time

reload(kc_file_io)
_PIECE_NAME_ = "CreateBaseScene"

class CreateBaseScene(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(CreateBaseScene, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = "open base file"
        detail = "path: {}".format(self.piece_data["base_path"])

        base_path = self.piece_data["base_path"]
        kc_file_io.file_open(base_path)
        
        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {}
    data = {"path": "E:/works/client/keica/data/assets/Mia.v1.1.fbx"}

    x = CreateBaseScene(piece_data=piece_data, data=data)
    x.execute()
