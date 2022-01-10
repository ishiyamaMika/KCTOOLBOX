import os
import sys
import json
import pprint

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.max.kc_file_io as file_io
# import KcLibs.mobu.kc_transport_time as kc_transport_time

reload(file_io)
_PIECE_NAME_ = "FileMerge"

class FileMerge(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(FileMerge, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        path = self.data["path"]
        if "replace_ext" in self.piece_data:
            path = path.replace(*self.piece_data["replace_ext"])

        if file_io.file_merge(path):
            if self.logger: 
                self.logger.debug("file open: {}".format(path))

        else:
            if self.logger: 
                self.logger.debug("file open failed: {}".format(path))
            flg = False
        
        return flg, self.pass_data, u"file imported: {}".format(os.path.basename(path)), "file name:\n{}".format(path)

if __name__ == "__main__":

    piece_data = {}
    data = {"path": "X:/Project/_942_ZIZ/3D/s99/c999/3D/import/ZIM_s99c999_anim_CH_tsukikoQuad.max"}
    x = FileMerge(piece_data=piece_data, data=data)
    print  x.execute()
