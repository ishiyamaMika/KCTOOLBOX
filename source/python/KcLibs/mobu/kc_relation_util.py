#-*-coding:utf-8-*-

import os
import sys
####################################################################
tool_path = "%s\\python" % os.environ["KEICA_TOOL_PATH"]
if not tool_path in sys.path:
    sys.path.append(tool_path)
####################################################################


from pyfbsdk import FBModelPlaceHolder, FBConstraintRelation, FBBoxPlaceHolder
import KcLibs.mobu.kc_model as kc_model
import KcLibs.mobu.kc_key as kc_key

def find_animation_node(parent, name):
    for node in parent.Nodes:
        if node.Name == name:
            return node
    return False

def get_fcurve_box_value(box):
    node = find_animation_node(box.AnimationNodeOutGet(), "Value")
    values = []
    if node:
        for key in node.FCurve.Keys:
            print 
            values.append(kc_key.get_key_attrs(key))
    return values

def set_fcurve_box_values(box, values):
    node = find_animation_node(box.AnimationNodeOutGet(), "Value")
    if not node:
        return False

    curve = node.FCurve

    curve.EditBegin()
    index = len(curve.Keys)
    
    curve.KeyDeleteByIndexRange(0, index-1)
    for value in values:
        t = FBTime(0, 0, 0, value["frame"])
        curve.KeyAdd(t, value["value"])
    
    for i, key in enumerate(curve.Keys):
        kc_key.set_key_attrs(key, values[i])

    curve.EditEnd()
    return True

def find_box_by_name(const, name):
    for box in const.Boxes:
        if box.Name == name:
            return box
    return False

def find_box_model_by_name(const, name): 
    for box in const.Boxes:
        if isinstance(box, FBModelPlaceHolder):
            if box.Model.LongName == name:
                return box
    return False

def find_box_by_model(const, model, src=True):
    if isinstance(model, str):
        model = kc_model.find_model_by_name(model)
        if not model:
            return False
            
    for box in const.Boxes:
        if isinstance(box, FBModelPlaceHolder):
            if box.Model == model:
                direction = check_direction(box)
                if src:
                    if direction == "src":
                        return box
                else:
                    if direction == "dst":
                        return box
        elif isinstance(box, FBBoxPlaceHolder):
            print dir(box), 
            if box.Box == model:
                direction = check_direction(box)
                if src:
                    if direction == "src":
                        return box
                else:
                    if direction == "dst":
                        return box

    return False

def get_src_direction_list(const):
    src = []
    dst = []
    both = []
    for box in const.Boxes:
        direction = check_direction(box)
        if direction == "src":
            src.append(box)
        elif direction == "dst":
            dst.append(box)
        elif direction == "both":
            both.append(box)
    return src, dst, both
    

def check_direction(box):
    in_channel = True
    out_channel = True
    for node in box.AnimationNodeInGet().Nodes:
        for i in range(node.GetSrcCount()):
            if node.GetSrc(i).GetOwner():
                if isinstance(node.GetSrc(i).GetOwner(), FBConstraintRelation):
                    in_channel = False
                    break
                
    for node in box.AnimationNodeOutGet().Nodes:
        for i in range(node.GetDstCount()):
            if node.GetDst(i).GetOwner():
                if isinstance(node.GetDst(i).GetOwner(), FBConstraintRelation):
                    out_channel = False
                    break

    if in_channel and out_channel:
        return "both"
    elif not in_channel and not out_channel:
        return False
    elif in_channel:
        return "dst"
    else:
        return "src"


def is_src_connected(const, box, channel):
    for node in box.AnimationNodeInGet().Nodes:
        if node.Name == channel:
            if node.GetSrcCount() > 0:
                return True
    return False

def is_dst_connected(const, box, channel):
    for node in box.AnimationNodeOutGet().Nodes:
        if node.Name == channel:
            if node.GetDstCount() > 0:
                return True
    return False
    
def src_connected_list(const, box, channel):
    for node in box.AnimationNodeInGet().Nodes:
        if node.Name == channel:
            arr = []
            for i in range(node.GetSrcCount()):
                print get_src_owner(node, i)
                arr.append(get_src_owner(node, i))
    return arr


def dst_connected_list(const, box, channel):
    for node in box.AnimationNodeOutGet().Nodes:
        if node.Name == channel:
            arr = []
            for i in range(node.GetDstCount()):
                arr.append(get_dst_owner(node, i))
    return arr
    
def get_src_owner(box, src_index):
    if isinstance(box, FBModelPlaceHolder):
        return [box.GetSrc(src_index).GetOwner(), box.GetSrc(src_index).UserName, box.GetSrc(src_index).GetOwner().Model]
    else:
        return [box.GetSrc(src_index).GetOwner(), box.GetSrc(src_index).UserName]

def get_dst_owner(box, dst_index):
    if isinstance(box, FBModelPlaceHolder):
        return [box.GetDst(dst_index).GetOwner(), box.GetDst(dst_index).UserName, box.GetDst(dst_index).GetOwner().Model]
    else:
        return [box.GetDst(dst_index).GetOwner(), box.GetDst(dst_index).UserName]




if __name__ == "__builtin__":
    #create relation named "test"
    from pyfbsdk import *
    def get_fcurve_values__TEST():
        """
        Fcurveだけのリレーションが１つシーンにある状態で
        """
        for const in FBSystem().Scene.Constraints:
            if not isinstance(const, FBConstraintRelation):
                continue
            for box in const.Boxes:
                break

        print get_fcurve_box_value(box)

    def set_fcurve_values__TEST():
        """
        Fcurveが2つだけのリレーションが１つシーンにある状態で
        """
        for const in FBSystem().Scene.Constraints:
            if not isinstance(const, FBConstraintRelation):
                continue

        a = const.Boxes[0]
        b = const.Boxes[1]
        dic = get_fcurve_box_value(a)
        set_fcurve_box_values(b, dic)
                


    set_fcurve_values__TEST()