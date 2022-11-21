# -*- coding: utf8 -*-

import os
import sys
import datetime
import re
import shutil

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import KcProject

from puzzle2.PzLog import PzLog

TASK_NAME = "renumber_files"


def main(event={}, context={}):
    """
    pass_data: signal, mode, frame_offset
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    header = ""
    detail = ""

    if not os.path.exists(data["source_directory"]):
        logger.details.set_header(u"フォルダが存在しません: {}".format(data["source_directory"]))
        return {"return_code": 1}
    
    if not os.path.exists(data["destination_directory"]):
        os.makedirs(data["destination_directory"])
    
    files = [l for l in os.listdir(data["source_directory"]) \
             if not os.path.isdir(u"{}/{}".format(data["source_directory"], l))]

    renumber = []

    dst_files = [l for l in os.listdir(data["destination_directory"]) \
                if not os.path.isdir(u"{}/{}".format(data["destination_directory"], l))]

    if len(dst_files) > 0:
        if len(files) != len(dst_files):
            detail = "WARNING: file count is not same."

    if "signal" in data:
        signal = data["signal"]
    else:
        signal = False

    frame = 0
    files.sort()
    successed = []
    error = []
    mode = data.get("mode", "move")
    if not data.get("frame_offset"):
        start_frame_offset = 0
    else:
        # override value by first file name
        start_frame_offset = -1

    for i, f in enumerate(files):
        source_path = "{}/{}".format(data["source_directory"], f)
        if os.path.isdir(source_path):
            continue

        match = re.match(".*_([0-9]*).*", f)
        if match:
            number = match.groups()[0]
            if start_frame_offset == -1:
                logger.details.add_detail("frame_offset: True: {}".format(number))
                start_frame_offset = int(number)

            padding = "{:0" + str(len(number)) + "d}"
            cell_category = os.path.basename(data["destination_directory"])
            f_, ext = os.path.splitext(f)
            new_f = "{}_{}{}".format(cell_category, padding.format(frame), ext)

            logger.debug("old: {}".format(f))
            logger.debug("new: {}".format(new_f))
            logger.details.add_detail("old   : {}".format(f))
            logger.details.add_detail("new   : {}".format(new_f))
            logger.details.add_detail("frame : {}".format(int(number)))
            logger.details.add_detail("offset: -{}".format(start_frame_offset))

            renumber.append("{}@{}".format(frame, int(number) - start_frame_offset))
            destination_path = "{}/{}".format(data["destination_directory"], new_f)
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
                logger.debug("{} successed: {} > {}".format(mode, f, new_f))
                if signal:
                    signal.emit(u"{} successed: {} > {}".format(mode, source_path, destination_path))
            else:
                error.append(u"src: {}\ndst: {}\n".format(f, new_f))
                logger.debug("{} failed: {} > {}".format(mode, f, new_f))
                    flg = False
                if signal:
                    signal.emit(u"{} failed: {} > {}".format(mode, f, new_f))                                                

            frame += 1

    if flg:
        d, f = os.path.split(data["destination_directory"])
        renumber_path = "{}/{}_renumber.txt".format(d, f)
        with open(renumber_path, "w") as f:
            f.write("\n".join(renumber))
            print("\n".join(renumber))
            logger.debug("renumber path: {}".format(renumber_path))
    
    detail = u"sucessed: \n{}".format(u"\n".join(successed))
    if len(error) > 0:
        header = u"コピーに失敗しました"
        detail += u"\nfailed: {}".format(u"\n".join(error))
    else:
        header = u"コピー, リネームしました"

    return flg, data, header, detail

if __name__ == "__main__":
    piece_data = {"include_model": True}
    data = {"source_directory": "F:/works/keica/junk/TEST/render",
            "destination_directory": "F:/works/keica/junk/TEST/sozai"}

    x = RenumberFiles(piece_data=piece_data, data=data)
    x.execute()

    print(x.pass_data)
