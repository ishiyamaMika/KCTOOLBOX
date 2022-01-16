import os
import sys
import time
import shutil

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

from KcLibs.core.KcProject import KcProject
_PIECE_NAME_ = "AchiveFile"

class AchiveFile(Piece):
    def __init__(self, **args):
        super(AchiveFile, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        path = self.data["path"]

        if os.path.exists(path):
            file_meta = time.localtime(os.stat(path).st_mtime)
            file_time = "{:04d}{:02d}{:02d}{:02d}{:02d}".format(file_meta[0], 
                                                                file_meta[1], 
                                                                file_meta[2],
                                                                file_meta[3], 
                                                                file_meta[4])

            d, f = os.path.split(path)
            f, ext = os.path.splitext(f)
            archive_path = "{}/archives".format(d)

            if not os.path.exists(archive_path):
                os.makedirs(archive_path)

            copy_path = "{}/{}_{}{}".format(archive_path, file_time, f, ext)

            try:
                shutil.copy2(path, copy_path)
                header = "archived: {}".format(copy_path)
            except:
                if self.logger:
                    self.logger.debug("copy failed: {}".format(copy_path))
                header = "archive failed: {}".format(copy_path)
            
            if "max" in self.data:
                files = os.listdir(archive_path)
                files.sort(reverse=True)
                if len(files) > self.data["max"]:
                    for each in files[self.data["max"]:]:
                        try:
                            os.remove("{}/{}".format(archive_path, each))
                            self.logger.debug("file remove successed: {}".format(each))
                        except:
                            if self.logger:
                                self.logger.debug("file remove failed: {}".format(each))

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    piece_data = {}
    path = "F:/works/keica/junk/test_.py"
    data = {"path": path, "max": 10}

    x = AchiveFile(piece_data=piece_data, data=data)
    x.execute()

    print x.pass_data
