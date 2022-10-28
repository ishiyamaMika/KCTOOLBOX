#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mods = ["{}/source/python".format(os.environ["KEICA_TOOL_PATH"]), 
       "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])]

for mod in mods:
    if not mod in sys.path:
        sys.path.append(mod)


from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_file_io as kc_file_io
_PIECE_NAME_ = "RenameNamespace"

class RenameNamespace(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(RenameNamespace, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        if self.data["category"] == "camera":
            return True, self.pass_data, u"cameraはリネームされません", ""

        namespace_s = self.data["namespace"].split("_")
        if not namespace_s[-1].isdigit():
            return True, self.pass_data, u"namespaceを変える必要がありません: {}".format(self.data["namespace"]), ""
        FBApplication().FileNew()
        kc_file_io.file_open(self.data["path"])

        for model in FBSystem().Scene.RootModel.Children:
            m_list = FBModelList()
            FBGetSelectedModels(m_list, model, False, True)
            renamed = []
            count = 0
            for m in m_list:
                long_name = m.LongName
                count += 1
                if ":" in long_name:
                    long_name_s = long_name.split(":")
                    namespace = long_name_s[0]
                    namespace_s = namespace.split("_")
                    if namespace_s[-1].isdigit():
                        temp = m.LongName
                        m.LongName = "{}:{}".format("_".join(namespace_s[:-1]), m.Name)
                        renamed.append(u"{} -> {}".format(temp, m.LongName))
            
            header = u"namespaceを変更しました: {}({})".format(self.data["namespace"], len(renamed))
            detail = u"renamed:\n{}".format("\n".join(renamed))
        kc_file_io.file_save(self.data["path"])

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {}

    data = {
            "path": "X:/Project/_942_ZIZ/3D/s99/c999/master/export/ZIM_s99c999_anim_CH_tsukikoQuad_02.fbx",
            "category": "CH",
            "namespace": "CH_tsukikoQuad_02"
            }

    x = RenameNamespace(piece_data=piece_data, data=data)
    print(x.execute())
