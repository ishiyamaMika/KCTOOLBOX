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
_PIECE_NAME_ = "FileOpen"

class FileOpen(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(FileOpen, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        path = self.data["path"]
        if "replace_ext" in self.piece_data:
            path = path.replace(*self.piece_data["replace_ext"])

        if kc_file_io.file_open(path):
            if self.logger: 
                self.logger.debug("file open: {}".format(path))
                file_path = path

        else:
            if self.logger: 
                self.logger.debug("file open failed: {}".format(path))
            flg = False

        return flg, self.pass_data, u"file opened: {}".format(os.path.basename(path)), "file name:\n{}".format(file_path)

if __name__ == "__builtin__":

    piece_data = {}
    data = {"path": "E:/works/client/keica/data/assets/Mia.v1.1.fbx"}

    x = FileOpen(piece_data=piece_data, data=data)
    x.execute()
