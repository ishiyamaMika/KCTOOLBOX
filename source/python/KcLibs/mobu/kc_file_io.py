#-*-coding: utf8-*-

import os
import sys
import re

from pyfbsdk import *


def file_save(file_path, embed=False, selection=False):
    file_path = str(file_path)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    option = FBFbxOptions(False)
    option.SetAll(FBElementAction.kFBElementActionSave, True)
    option.EmbedMedia = embed
    option.SaveSelectedModelsOnly = selection
    option.ShowFileDialog = False

    if not FBApplication().FileSave(file_path, option):
        return False

    return True

def file_open(file_path):
    file_path = str(file_path)
    try:
        FBApplication().FileOpen(file_path)
        return True
    except:
        return False

def file_new():
    FBApplication().FileNew()

def get_file_path():
    return FBApplication().FBXFileName

def file_merge(file_path, namespace=None, padding=2):
    def _get_namespaces():
        return [l.LongName.split(":")[0] for l in FBSystem().Scene.RootModel.Children if l.LongName.find(":") != -1 if not "_Ctrl" in l.LongName.split(":")[0]]

    before = _get_namespaces()

    current_takes = [l for l in FBSystem().Scene.Takes]
    options = FBFbxOptions(True)
    options.TakeSpan = FBTakeSpanOnLoad.kFBLeaveAsIs
    options.BaseCameras = False
    options.CameraSwitcherSettings = False
    options.CurrentCameraSettings = False
    options.GlobalLightingSetting = False
    options.TransportSettings = False

    if FBApplication().FileAppend(file_path, False, options):
        if not namespace:
            return

        pattern = "(.*)_([0-9]*)$"
        namespaces = {}
        for b in before:
            search = re.search(pattern, b)
            if search:
                current_namespace, number = search.groups()
                number = int(number)
                namespaces.setdefault(current_namespace, []).append(number)
            else:
                namespaces.setdefault(b, []).append(1)
            
        after = _get_namespaces()

        a = set(before)
        b = set(after)

        current = list(b - a)
        if len(current) > 0:
            current = current[0]

            if namespace in namespaces:
                number = namespaces[namespace]
                number.sort()
                number = number[-1] + 1
                pattern = "{}_" + "{{:0{}d}}".format(padding)
                namespace = pattern.format(namespace, number)

            for comp in FBSystem().Scene.Components:
                comp_s = comp.LongName.split(":")
                if len(comp_s) == 1:
                    continue

                if comp_s[0] != current:
                    continue

                comp.ProcessNamespaceHierarchy(FBNamespaceAction.kFBReplaceNamespace, current, namespace, False)  

        delete_takes = [l for l in FBSystem().Scene.Takes if not l in current_takes]
        for d in delete_takes:
            d.FBDelete()
        return True
    return False


if __name__ == "__builtin__":
    FBApplication().FileNew()
    namespace = "CH_tsukikoQuad"
    f = "E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/tsukikoQuad/MB/CH_tsukikoQuad_t02_01.fbx"
    f = "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/tsukikoQuad/MB/CH_tsukikoQuad_t06_01.fbx"
    # for i in range(2):
    namespace = "CH_tsukikoQuad_03"
    file_merge(f, namespace)