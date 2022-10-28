#-*- coding: utf8 -*-

import os
import sys
import json

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_file_io as file_io
reload(file_io)
_PIECE_NAME_ = "FileSave"


class FileSave(Piece):
    def __init__(self, **args):
        super(FileSave, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        if self.logger: self.logger.debug("file save: {}".format(self.data["path"]))

        flg = True
        
        path = self.data["path"]
        if not os.path.lexists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        
        file_io.file_save(path)
        header = u"ファイルを保存しました: {}".format(os.path.basename(path))
        detail = u"path\n{}".format(path)
        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {'path': "E:/works/client/keica/data/assets"}


    data = {'namespace': 'Mia',
            'properties': [{'name': 'category', 'value': 'CH'},
                {'name': 'plot', 'value': 'Mia_plot'},
                {'name': 'major', 'value': 1},
                {'name': 'namespace', 'value': 'Mia'},
                {'name': 'export', 'value': 'Mia_export'},
                {'name': 'minor', 'value': 1}]}


    x = FileSave(piece_data=piece_data, data=data)
    x.execute()


 