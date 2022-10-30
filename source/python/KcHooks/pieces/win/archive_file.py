from inspect import trace
import os
import sys
import time
import shutil
import datetime

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import KcProject

from puzzle2.PzLog import PzLog

TASK_NAME = "archive_file"
DATA_KEY_REQUIRED = [""]

def main(event={}, context={}):
    """
    pass_data: signal
    piece_data: move, is_directory
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    header = "noting to archive"
    detail = ""
    path = data["path"]

    if "signal" in data:
        signal = data["signal"]
    else:
        signal = False

    if os.path.exists(path):
        if data.get("is_directory", False):
            file_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
            archive_path = "{}/archives/{}".format(data["path"], file_time)
            fs = [l for l in os.listdir(data["path"]) \
                    if not os.path.isdir(u"{}/{}".format(data["path"], l))]

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
            fs = [os.path.basename(path)]

        if not os.path.exists(archive_path):
            os.makedirs(archive_path)

        successed = []
        error = []
        if signal:
            signal.emit("archive start:")
        for f in fs:
            f_, ext = os.path.splitext(f)
            if is_directory:
                source_path = "{}/{}".format(data["path"], f)
                destination_path = "{}/{}{}".format(archive_path, f_, ext)
            else:
                source_path = data["path"]
                destination_path = "{}/{}_{}{}".format(archive_path, file_time, f_, ext)
                print(destination_path, f, ext, fs)
            source_f = os.path.basename(source_path)
            
            source_f_name = os.path.basename(source_path)
            destination_f_name = os.path.basename(destination_path)
            try:
                if data.get("move", False):
                    os.move(source_path, destination_path)
                else:
                    shutil.copy2(source_path, destination_path)
                successed.append(destination_f_name)
                if signal:
                    signal.emit("archive successed: {} > {}".format(source_f_name, destination_f_name))                    
            except:
                logger.debug("copy failed: {}".format(destination_f_name))
                error.append(destination_f_name)
                if signal:
                    signal.emit("archive error: {} > {}".format(source_f_name, destination_f_name))                    
                    continue

            if "max" in data:
                files = os.listdir(archive_path)
                files.sort(reverse=True)
                if len(files) > data["max"]:
                    for each in files[data["max"]:]:
                        try:
                            os.remove("{}/{}".format(archive_path, each))
                            logger.debug("file remove successed: {}".format(each))
                        except:
                            logger.debug("file remove failed: {}".format(each))

            detail = u"successed:\n"
            detail += u"\n".join(successed)
            if len(error) == 0:
                header = u"archived: {}".format(archive_path)
            else:
                header = u"archive failed: {}".format(archive_path)
                detail += u"\n".join(error)
    logger.details.set_header(header)
    logger.details.set_detail(detail)
    return {"return_code": return_code}


if __name__ in ["__main__", "__builtin__"]:
    def is_file():
        piece_data = {}
        path = "F:/works/keica/junk/test_.py"
        data = {"path": path, "max": 10}
        data.update(piece_data)
        main({"data": data})
    
    def is_directory():
        piece_data = {"is_directory": True}
        path = "F:/works/keica/junk/TEST/render"
        data = {"path": path, "max": 10}

        data.update(piece_data)
        main({"data": data})
  
    is_file()

