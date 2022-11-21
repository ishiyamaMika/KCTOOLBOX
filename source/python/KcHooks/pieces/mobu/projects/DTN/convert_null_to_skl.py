import os
import sys

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

from pyfbsdk import *
from puzzle2.PzLog import PzLog

import KcLibs.mobu.kc_key as kc_key
import KcLibs.mobu.kc_file_io as kc_file_io

TASK_NAME = "convert_null_to_skl"
DATA_KEY_REQUIRED = ["namespace"]


def swap_model(model, logger=None):
    if not isinstance(model, FBModelNull):
        return False

    parent = model.Parent
    original_name = model.LongName
    model.LongName = "{}_original".format(original_name)

    children = [l for l in model.Children]

    skl = FBModelSkeleton(original_name)
    if parent:
        parent.ConnectSrc(skl)

    kc_key.copy_local_animation(model, skl)
    logger.details.add_detail(u"{}をsklに変換しました".format(original_name))

    for child in children:
        skl.ConnectSrc(child)

    model.FBDelete()

def main(event={}, context={}):
    """
    key required from data: namespace
    """

    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0
    convert_list = []

    for root in FBSystem().Scene.RootModel.Children:
        m_list = FBModelList()
        FBGetSelectedModels(m_list, root, False)
        m_list = [l for l in m_list]

        for m in m_list:
            swap_model(m, logger)

    logger.details.set_header(u"propのnullをsklに変換しました: {}".format("\n".join(convert_list)))

    path = FBApplication().FBXFileName
    d, f = os.path.split(path)
    f, ext = os.path.splitext(f)

    save_path = "{}/{}_skl{}".format(d, f, ext)
    
    kc_file_io.file_save(save_path)
    return {"return_code": return_code}


if __name__ in ["__builtin__", "__main__", "builtins"]:
    data = {"": ""}
    main(event={"data": data})