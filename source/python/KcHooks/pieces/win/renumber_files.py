# -*- coding: utf8 -*-

import os
import sys
import datetime
import re
import shutil

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()

from puzzle.Piece import Piece

from KcLibs.core.KcProject import KcProject
_PIECE_NAME_ = "RenumberFiles"

class RenumberFiles(Piece):
    def __init__(self, **args):
        super(RenumberFiles, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        if not os.path.exists(self.data["source_directory"]):
            return flg, self.pass_data, header, detail
        
        if not os.path.exists(self.data["destination_directory"]):
            os.makedirs(self.data["destination_directory"])
        
        files = [l for l in os.listdir(self.data["source_directory"]) \
                 if not os.path.isdir(u"{}/{}".format(self.data["source_directory"], l))]

        renumber = []

        dst_files = [l for l in os.listdir(self.data["destination_directory"]) \
                 if not os.path.isdir(u"{}/{}".format(self.data["destination_directory"], l))]

        if len(dst_files) > 0:
            if len(files) != len(dst_files):
                detail = "WARNING: file count is not same."

        if "signal" in self.pass_data:
            signal = self.pass_data["signal"]
        else:
            signal = False

        frame = 0
        files.sort()
        successed = []
        error = []
        mode = self.piece_data.get("mode", "move")
        if not self.piece_data.get("frame_offset"):
            start_frame_offset = 0
        else:
            # override value by first file name
            start_frame_offset = -1

        for i, f in enumerate(files):
            source_path = "{}/{}".format(self.data["source_directory"], f)
            if os.path.isdir(source_path):
                continue

            match = re.match(".*_([0-9]*).*", f)
            if match:
                number = match.groups()[0]
                if start_frame_offset == -1:
                    print("frame_offset: True: {}".format(number))
                    start_frame_offset = int(number)

                padding = "{:0" + str(len(number)) + "d}"
                cell_category = os.path.basename(self.data["destination_directory"])
                f_, ext = os.path.splitext(f)
                new_f = "{}_{}{}".format(cell_category, padding.format(frame), ext)
                if self.logger:
                    self.logger.debug("old: {}".format(f))
                    self.logger.debug("new: {}".format(new_f))
                print("old   : {}".format(f))
                print("new   : {}".format(new_f))
                print("frame : {}".format(int(number)))
                print("offset: -{}".format(start_frame_offset))

                renumber.append("{}@{}".format(frame, int(number) - start_frame_offset))
                destination_path = "{}/{}".format(self.data["destination_directory"], new_f)
                if signal:
                    signal.emit(u"{} start: {} > {}".format(mode, f, new_f))

                if mode == "copy":
                    try:
                        shutil.copy2(source_path, destination_path)
                        success_flg = True
                    except:
                        success_flg = False
                else:
                    try:
                        shutil.move(source_path, destination_path)
                        success_flg = True
                    except:
                        success_flg = False
                
                if success_flg:
                    successed.append(u"src: {}\ndst: {}\n".format(f, new_f))
                    if self.logger:
                        self.logger.debug("{} successed: {} > {}".format(mode, f, new_f))
                    if signal:
                        signal.emit(u"{} successed: {} > {}".format(mode, source_path, destination_path))
                else:
                    error.append(u"src: {}\ndst: {}\n".format(f, new_f))
                    if self.logger:
                        self.logger.debug("{} failed: {} > {}".format(mode, f, new_f))
                        flg = False
                    if signal:
                        signal.emit(u"{} failed: {} > {}".format(mode, f, new_f))                                                

                frame += 1

        if flg:
            d, f = os.path.split(self.data["destination_directory"])
            renumber_path = "{}/{}_renumber.txt".format(d, f)
            with open(renumber_path, "w") as f:
                f.write("\n".join(renumber))
                print("\n".join(renumber))
                if self.logger:
                    self.logger.debug("renumber path: {}".format(renumber_path))
        
        detail = u"sucessed: \n{}".format(u"\n".join(successed))
        if len(error) > 0:
            header = u"コピーに失敗しました"
            detail += u"\nfailed: {}".format(u"\n".join(error))
        else:
            header = u"コピー, リネームしました"

        return flg, self.pass_data, header, detail

if __name__ == "__main__":
    piece_data = {"include_model": True}
    data = {"source_directory": "F:/works/keica/junk/TEST/render",
            "destination_directory": "F:/works/keica/junk/TEST/sozai"}

    x = RenumberFiles(piece_data=piece_data, data=data)
    x.execute()

    print(x.pass_data)
