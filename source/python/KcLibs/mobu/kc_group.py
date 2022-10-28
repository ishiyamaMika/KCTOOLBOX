#-*-coding: utf8-*-

from pyfbsdk import *

def get_group(name):
    if isinstance(name, FBGroup):
        return name

    for g in FBSystem().Scene.Groups:
        if g.LongName == name:
            return g

    return False

def get_parent(_group):
    for i in range(_group.GetDstCount()):
        if _group.GetDst(i):
            if isinstance(_group.GetDst(i), FBGroup):
                return _group.GetDst(i)
    return None

def get_group_hierachy(group):
    group = get_group(group)
    if not group:
        return []

    parent = get_parent(group)
    i = 0
    parents = []
    if not parent is None:
        while not parent is None:
            parents.append(parent)
            parent = get_parent(parent)
            i+=1
    
    parents = parents[::-1]
    parents.append(group)
    return parents


if __name__ == "__builtin__":
    for group in FBSystem().Scene.Groups:
        print(group.Name, "/".join([l.LongName for l in get_group_hierachy(group)]) )