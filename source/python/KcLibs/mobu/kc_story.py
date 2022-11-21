#-*-coding: utf8-*-
import sys
import os

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)



import KcLibs.mobu.kc_model as kc_model

def get_tracks(active=False):
    def _children(folder, lst, active=False):
        for track in folder.Components:
            if isinstance(track, FBStoryFolder):
                _children(track, lst)
            else:
                if active:
                    if not track.Mute:
                        if not track in lst:
                            lst.append(track)
                else:
                    if not track in lst:
                        lst.append(track)
        return lst
    active_list = []
    _children(FBStory().RootFolder, active_list, active)
    return active_list

def is_track_exists(name):
    for track in get_tracks():
        if track.Name == name:
            return track
    return False

def create_story_track(name, models, cam=False):
    track = is_track_exists(name)
    if not track:
        if cam:
            track = FBStoryTrack(FBStoryTrackType.kFBStoryTrackCamera)
        else:
            track = FBStoryTrack(FBStoryTrackType.kFBStoryTrackAnimation)
        track.Name = name

    details = [l for l in track.Details]

    for model in models:
        model_ = kc_model.to_object(model)
        if not model_ in details:
            track.Details.append(model_)
    FBSystem().Scene.Evaluate()
    return track

def create_clip(track, path, **kwargs):
    def _is_same(a, b):
        return os.path.normpath(a).lower() == os.path.normpath(b).lower()

    clip = False
    for clip_ in track.Clips:
        if _is_same(clip_.PropertyList.Find("ClipAnimationPath").Data, path):
            clip = clip_
            break
    if not clip:
        clip = FBStoryClip(str(path), track, FBTime(0, 0, 0, 0, 0))

    if "offset" in kwargs:
        clip.MoveTo(FBTime(0, 0, 0, kwargs["offset"]), True)

    FBSystem().Scene.Evaluate()
    return clip

def delete_tracks():
    tracks = get_tracks()
    for track in tracks[::-1]:
        track.FBDelete()

if __name__ in ["__builtin__", "builtins"]:
    # a = create_story_track("AAA", ["CH_tsukikoQuad:spineB_jt", "CH_tsukikoQuad:spineA_jt"])
    # print(create_clip(a, r"E:/works/client/keica/_942_ZIZ/3D/s01/c001/master/export/ZIM_s01c001_anim_LO_ABCDE_asasad_03.fbx", offset=19))

    delete_tracks()

    

