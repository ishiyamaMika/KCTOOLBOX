from inspect import trace
import os
import sys
import time
import shutil
import datetime

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()
from KcLibs.core.KcProject import KcProject


from puzzle.Piece import Piece


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

        if "signal" in self.pass_data:
            signal = self.pass_data["signal"]
        else:
            signal = False

        if os.path.exists(path):
            if self.piece_data.get("is_directory", False):
                file_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
                archive_path = "{}/archives/{}".format(self.data["path"], file_time)
                fs = [l for l in os.listdir(self.data["path"]) \
                      if not os.path.isdir(u"{}/{}".format(self.data["path"], l))]

                is_directory = True
            else:
                is_directory = False
                file_meta = time.localtime(os.stat(path).st_mtime)
                file_time = "{:04d}{:02d}{:02d}{:02d}{:02d}".format(file_meta[0], 
                                                                    file_meta[1], 
                                                                    file_meta[2],
                                                                    file_meta[3], 
                                                                    file_meta[4])
                d, f = os.path.split(path)
                f, ext = os.path.splitext(f)
                archive_path = "{}/archives".format(d)
                fs = [f]

            if not os.path.exists(archive_path):
                os.makedirs(archive_path)

            successed = []
            error = []
            if signal:
                signal.emit("archive start:")
            for f in fs:
                f_, ext = os.path.splitext(f)
                if is_directory:
                    source_path = "{}/{}".format(self.data["path"], f)
                    destination_path = "{}/{}{}".format(archive_path, f_, ext)
                else:
                    source_path = self.data["path"]
                    destination_path = "{}/{}_{}{}".format(archive_path, file_time, f_, ext)
                source_f = os.path.basename(source_path)
                
                source_f_name = os.path.basename(source_path)
                destination_f_name = os.path.basename(destination_path)
                try:
                    if self.piece_data.get("move", False):
                        os.move(source_path, destination_path)
                    else:
                        shutil.copy2(source_path, destination_path)
                    successed.append(destination_f_name)
                    if signal:
                        signal.emit("archive successed: {} > {}".format(source_f_name, destination_f_name))                    
                except:
                    if self.logger:
                        self.logger.debug("copy failed: {}".format(destination_f_name))
                    error.append(destination_f_name)
                    if signal:
                        signal.emit("archive error: {} > {}".format(source_f_name, destination_f_name))                    
                        continue

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
                detail = u"successed:\n"
                detail += u"\n".join(successed)
                if len(error) == 0:
                    header = u"archived: {}".format(archive_path)
                else:
                    header = u"archive failed: {}".format(archive_path)
                    detail += u"\n".join(error)

        return flg, self.pass_data, header, detail

if __name__ == "__main__":

    def is_file():
        piece_data = {}
        path = "F:/works/keica/junk/test_.py"
        data = {"path": path, "max": 10}

        x = AchiveFile(piece_data=piece_data, data=data)
        x.execute()

        print x.pass_data
    
    def is_directory():
        piece_data = {"is_directory": True}
        path = "F:/works/keica/junk/TEST/render"
        data = {"path": path, "max": 10}

        x = AchiveFile(piece_data=piece_data, data=data)
        x.execute()

        print x.pass_data
    
    is_directory()

