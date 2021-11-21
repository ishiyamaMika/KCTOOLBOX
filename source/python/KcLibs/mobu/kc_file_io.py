#-*-coding: utf8-*-

import os
import sys

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

def get_file_path():
    return FBApplication().FBXFileName