#-*- coding: utf8 -*-

import os
import sys
from decimal import Decimal, ROUND_HALF_UP

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

from puzzle2.PzLog import PzLog

import KcLibs.mobu.kc_camera as kc_camera
import KcLibs.mobu.kc_key as kc_key
TASK_NAME = "write_note"

def main(event={}, context={}):

    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    switcher = kc_camera.get_switcher_data()
    path = FBApplication().FBXFileName
    d, f = os.path.split(path)
    d = os.path.dirname(d)
    f, ext = os.path.splitext(f)

    cut_timing_text_path = "{}/{}_CutTiming.txt".format(d, f)
    readme_text_path = "{}/{}_readme.txt".format(d, f)
    bg_position_text_path = "{}/{}_BG_position.txt".format(d, f)

    save_flg = False

    if switcher:
        with open(cut_timing_text_path, "w") as f:
            f.write(u"■Cut Timing\n\n")
            for cam in switcher:
                f.write(u"{} {}-{}\n".format(cam["name"].split(":")[0], cam["start"], cam["end"]))
                logger.debug(u"{} {}-{}\n".format(cam["name"].split(":")[0], cam["start"], cam["end"]))
                logger.details.add_detail(u"{} {}-{}\n".format(cam["name"].split(":")[0], cam["start"], cam["end"]))

            logger.debug(u"Cut Timingを書き出しました: {}".format(cut_timing_text_path))
            save_flg = True

    with open(readme_text_path, "w") as f:
        pass

    def _round(value):
        return Decimal(value).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

    def _rem_0(value):
        value_str = str(value)
        if value_str.endswith(".000"):
            return value_str.split(".")[0]
        return value_str

    with open(bg_position_text_path, "w") as f:
        for model in data.get("BG_models", []):
            trs_all = kc_key.get_all(model, False)
            f.write(u"\n■BG Transform\n{}\n\n".format(model.LongName))
            for i, each in enumerate(trs_all):
                if i == 0:
                    name = "Translation"
                    default = [0, 0, 0]
                elif i == 1:
                    name = "Rotation"
                    default = [0, 0, 0]
                else:
                    name = "Scaling"
                    default = [1, 1, 1]
                each = [_round(l) for l in each]
                if each == default:
                    continue

                f.write(u"{}\n{}\n\n".format(name, ", ".join([_rem_0(l) for l in each])))
                logger.debug(u"{}\n{}\n".format(name, "\n".join([_rem_0(l) for l in each])))
                logger.details.add_detail(u"{}\n{}\n\n".format(name, "\n".join([_rem_0(l) for l in each])))

    if save_flg:
        logger.details.set_header(u"設定ファイルを書き出しました")
    else:
        logger.details.set_header(u"設定ファイルを書き出せませんでした")
        return_code = 1

    return {"return_code": return_code}


if __name__ in ["__main__", "__builtin__", "builtins"]:
    main()
