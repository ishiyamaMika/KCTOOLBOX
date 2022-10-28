# -*-coding: utf8 -*-

from pyfbsdk import *
class KeyInfo:
    def __init__(self, trs, xyz, frame, fb_time, value=None):
        self.frame = frame
        self.value = value
        self.trs = trs
        self.xyz = xyz
        self.fb_time = fb_time

def get_frame(fb_time):
    if FBSystem().Version >= 13000.0:
        return fb_time.GetFrame()
    else:
        return fb_time.GetFrame(True)      

def get_all_keys(model):
    def _get_trs_key(model, trs="Translation"):
        all_keys = {}

        trs_object = getattr(model, trs)
        if not trs_object.GetAnimationNode():
            return {}
        for i in range(3):
            each_keys = []
            anim_node = trs_object.GetAnimationNode().Nodes[i]
            if anim_node is None:
                #all_keys.append(each_keys)
                continue

            temp_key = None
            for k in anim_node.FCurve.Keys:
                frame = get_frame(k.Time)
                all_keys.setdefault(frame, [None, None, None])
                keyframe = {}
                keyframe["type"] = "{}{}".format(trs[0], ["x", "y", "z"][i])
                keyframe["axis"] = i
                # keyframe["frame"] = get_frame(k.Time)
                keyframe["value"] = k.Value
                if temp_key is None:
                    keyframe["changed"] = None
                else:
                    if temp_key["changed"] is None:
                        keyframe["changed"] = True
                    else:
                        keyframe["changed"] = temp_key["value"] != keyframe["value"]

                all_keys[frame][i] = keyframe
                temp_key = keyframe
        return all_keys

    if isinstance(model, (list, FBModelList)):
        all_ = {}
        for m in model:
            dic = get_all_keys(m)
            all_[m.LongName] = dic[m.LongName]
        return all_
    else:
        all_keys = {}
        for trs in ["Translation", "Rotation", "Scaling"]:
            all_keys[trs] = _get_trs_key(model, trs)


        a = all_keys["Translation"].keys()
        b = all_keys["Rotation"].keys()
        c = all_keys["Scaling"].keys()
        mix = a + b + c
        mix.sort()
        min_ = mix[0]
        max_ = mix[-1]

        keyframe_set = {}
        keyframe_set["min"] = min_
        keyframe_set["max"] = max_
        keyframe_set["list"] = []
        for i in range(min_, max_+1):
            keys = {}
            for trs in ["Translation", "Rotation", "Scaling"]:
                if i in all_keys[trs]:
                    keys[trs] = all_keys[trs][i]
                else:
                    keys[trs] = []
            keyframe_set["list"].append(keys)

        return {model.LongName: keyframe_set}

def get_changed_frames(infos):
    changed = []

    for k, v in infos.items():
        for i, key in enumerate(v["list"]):
            frame = i + v["min"]
            for trs in ["Translation", "Rotation", "Scaling"]:
                for k in key[trs]:
                    if k["changed"]:
                        changed.append(v["min"] + i)

    changed = list(set(changed))
    changed.sort()
    return changed


if __name__ == "__builtin__":
    m_list = FBModelList()
    FBGetSelectedModels(m_list)

    infos = get_all_keys(m_list)
    print(get_changed_frames(infos))
    print("") 
    for info, key in infos.items():
        print(info, get_changed_frames({info: key}))
