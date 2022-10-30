#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_transport_time as kc_transport_time

from puzzle2.PzLog import PzLog

TASK_NAME = "change_camera"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    cameras = []
    for cam in FBSystem().Scene.Cameras:
        if cam.SystemCamera:
            continue
        if cam.LongName.startswith("{}:".format(self.data["namespace"])):
            app = FBApplication()
            app.SwitchViewerCamera(cam)
            kc_transport_time.set_zoom_time(self.data["start"], 
                                            self.data["stop"],
                                            self.data["fps"])
            FBSystem().Scene.Evaluate()

    return {"return_code": return_code}


if __name__ == "__builtin__":
    piece_data = {"include_model": True}
    data = {"namespace": "cam_s01c006A", "start": 10, "stop": 30, "fps": 8}
    print(main({"data": data}))

