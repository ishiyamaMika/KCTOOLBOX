# -*-coding: utf8-*-

import maya.cmds as cmds


def create(type_, name, intensity=1.0, **kwargs):
    light = False
    if type_ == "ambientLight":
        light = cmds.ambientLight(n=name, intensity=intensity)
    elif type_ == "pointLight":
        light = cmds.pointLight(n=name, intensity=intensity)
    elif type_ == "spotLight":
        light = cmds.spotLight(n=name, intensity=intensity)
    elif type_ == "directionalLight":
        light = cmds.directionalLight(n=name, intensity=intensity)
    else:
        print "out of type presets: {}".format(type_)
    return light

