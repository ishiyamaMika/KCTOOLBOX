#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.mobu.kc_model as kc_model

from pyfbsdk import *

def get_all():
    return FBSystem().Scene.Cameras

def get_switcher_data(include_object=True):
    cams = [l for l in get_all() if not l.SystemCamera]
    anim_node = FBCameraSwitcher().AnimationNode
    if not anim_node:
        return []
    
    switcher_data = []
    keys = FBCameraSwitcher().AnimationNode.Nodes[0].FCurve.Keys
    for i, key in enumerate(keys):
        if i+1 < len(keys):
            next_key_frame = keys[i+1].Time.GetFrame() - 1
        else:
            next_key_frame = FBPlayerControl().LoopStop.GetFrame()

        index = int(key.Value) - 1

        frame = key.Time.GetFrame()
        data = {"name": cams[index].LongName,
                "start": frame,
                "end": next_key_frame}

        if include_object:
            data["object"] = cams[index]
        switcher_data.append(data)
        
    return switcher_data

def set_switcher(data_set, clear_all=False):
    cam_switcher = FBCameraSwitcher()
    anim_node = cam_switcher.AnimationNode

    if clear_all:
        nodes = anim_node.Nodes
        for node in nodes:
            fcurve = node.FCurve
            if not fcurve:
                continue

            fcurve.EditBegin()
            fcurve.EditClear()
            fcurve.EditEnd()

    cams = {cam.LongName: {"id": i+1, "object": cam} for i, cam in enumerate([l for l in FBSystem().Scene.Cameras if not l.SystemCamera])}

    for data in data_set:
        if data["name"] in cams:
            index = cams[data["name"]]["id"]
        else:
            continue

        t = FBTime(0, 0, 0, data["start"])
        anim_node.Nodes[0].KeyAdd(t, index)
        
    for key in anim_node.Nodes[0].FCurve.Keys:
        key.Interpolation = FBInterpolation.kFBInterpolationConstant
        key.LeftDerivative = 0
        key.RightDerivative = 0
        key.TangentClampMode = FBTangentClampMode.kFBTangentClampModeClamped
        key.TangentConstantMode = FBTangentConstantMode.kFBTangentConstantModeNormal



    FBSystem().Scene.Evaluate()


def change_cam(cam, select=False, pane=0):
    camera_switcher = False

    if cam == "switcher":
        camera_switcher = True

    elif not isinstance(cam, FBCamera):
        cam = kc_model.to_object(cam)
        if not cam:
            return False

    if FBSystem().Version >= 16000.0:
        if camera_switcher:
            FBSystem().Scene.Renderer.SetCameraSwitcherInPane(pane, True)
        else:
            FBSystem().Scene.Renderer.SetCameraSwitcherInPane(pane, False)
            FBSystem().Scene.Renderer.SetCameraInPane(cam, pane)
    else:
        if camera_switcher:
            FBSystem().Scene.Renderer.UseCameraSwitcher = True
        else:
            FBSystem().Scene.Renderer.UseCameraSwitcher = False
            FBApplication().SwitchViewerCamera(cam)

    if select and not camera_switcher and not cam.Name.startswith("Producer"):
        cam.Selected = True

    FBSystem().Scene.Evaluate()
    

if __name__ in ["__builtin__", "builtins"]:
    #data = get_switcher_data()
    #for d in data:
    #    print("{}-{} {}".format(d["start"], d["end"], d["name"]))
    #print(data)
    x = [{'name': 'Cam_A9000:Cam_A9000', 'start': 0, 'end': 64}, {'name': 'Cam_A9050:Cam_A9050', 'start': 65, 'end': 216}]
    # print(set_switcher(x, True))

    # change_cam("Cam_A9000:Cam_A0000")
    set_switcher(x)

