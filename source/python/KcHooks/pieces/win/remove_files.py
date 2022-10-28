#-*-coding: utf8-*-
import os
import sys
import glob

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

from KcLibs.core.KcProject import KcProject
_PIECE_NAME_ = "RemoveFiles"

class RemoveFiles(Piece):
    def __init__(self, **args):
        super(RemoveFiles, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        for each in self.piece_data["patterns"]:
            if each["root"] not in self.data:
                if self.logger:
                    self.logger.debug("root is not exists: {}".format(each["root"]))
                    self.logger.debug("root is not keys: {}".format(", ".join(self.data.keys())))
                continue
            remove_path = os.path.normpath(os.path.join(self.data[each["root"]], each["target"]))
            files = glob.glob(remove_path)
            if self.logger:self.logger.debug("root path: {}".format(remove_path))
            for f in files:
                try:
                    os.remove(f)
                    detail += "removed: {}\n".format(f)
                    if self.logger: 
                        self.logger.debug("removed: {}".format(f))
                except:
                    detail += "remove failed: {}\n".format(f)
                    if self.logger: 
                        self.logger.debug("remove failed: {}".format(f))
        if detail == "":
            header = u"削除するkomaファイルがありませんでした"
        else:
            header = u"既存のkomaファイルを削除しました"

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    piece_data = {"patterns": [{"root": "path", "target": "../import/*_koma.json"}]}
    path = "X:/Project/_942_ZIZ/3D/s99/c999/3D/master/ZIM_s99c999_anim.max"
    data = {"path": path}

    x = RemoveFiles(piece_data=piece_data, data=data)
    x.execute()

    print(x.pass_data)
