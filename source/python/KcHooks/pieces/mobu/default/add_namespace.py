#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

_PIECE_NAME_ = "AddNamespace"

class AddNamespace(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(AddNamespace, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        if not "namespace" in self.data:
            return False, self.pass_data, u"ネームスペースが設定されていません", detail

        if self.data["namespace"] == "":
            return False, self.pass_data, u"ネームスペースが設定されていません", detail

        m_list = FBModelList()
        FBGetSelectedModels(m_list)
        for m in m_list:
            m.Selected = False

        for each in FBSystem().Scene.RootModel.Children:
            if each.Name == "Reference":
                continue

            m_list = FBModelList()
            FBGetSelectedModels(m_list, each, False, False)
            for m in m_list:
                if self.piece_data.get("force", False):
                    m.LongName = "{}:{}".format(self.data["namespace"], m.Name)
                else:
                    if ":" in m.LongName:
                        continue
                    else:
                        m.LongName = "{}:{}".format(self.data["namespace"], m.Name)

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    piece_data = {"force": True}
    data = {"namespace": "Mia"}

    x = AddNamespace(piece_data=piece_data, data=data)
    x.execute()
