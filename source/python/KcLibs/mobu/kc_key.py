#-*-coding:utf-8-*-

import traceback
from pyfbsdk import *

if FBSystem().Version <= 12000.0:
    from pyfbsdk import FBModelTransformationMatrix
else:
    from pyfbsdk import FBModelTransformationType

from functools import wraps
import os
def comp_property_list(function):
    @wraps(function)
    def _deco(*args, **kwargs):
        print "comp_property_list--start"
        a = _get_property_list_data()
        res = function(*args, **kwargs)
        _comp_property(a, _get_property_list_data(False))

        return res

    return _deco

def _comp_property(a, b):
    ls = []
    for name, dic in a.items():
        ls.append("\n---------------------------%s------------------------------" % name)
        if not name in b:
            ls.append("<%s>name is not in b" % name)
            continue
        for k, v in dic.items():
            if not k in b[name].keys():
                ls.append("*[%s] key not exists in b" % k)
            elif b[name][k] != v:
                ls.append("***[%s] value not same: a:%s b:%s" % (k, v, b[name][k]))
            else:
                ls.append("[%s] value is same: a:%s b:%s" %(k, v, b[name][k]))
    tx_path = "%s\\plot_info.txt" % os.environ["TEMP"]
    tx = open(tx_path, "w")
    tx.write("\n".join(ls))
    tx.close()

def _get_property_list_data(src=True):
    m_list = FBModelList()
    FBGetSelectedModels(m_list)
    dic = {}
    for m in m_list:
        dic.setdefault(m.LongName, {})
        if src:
            print "src model:", m.LongName
        else:
            print "dst model:", m.LongName
        for attr in m.PropertyList:
            try:
                value = attr.Data
            except:
                value = " err"
            dic[m.LongName][attr.Name] = value
    return dic

def _set_vector(node, xyz, gbl, mode):
    value = FBVector3d(*xyz)
    node.SetVector(value, mode, gbl)
    FBSystem().Scene.Evaluate()


def set_trs(node, xyz, gbl):
    if FBSystem().Version >= 13000.0:
        _set_vector(node, xyz, gbl, FBModelTransformationType.kModelTranslation)
    else:
        _set_vector(node, xyz, gbl, FBModelTransformationMatrix.kModelTranslation)


def set_rot(node, xyz, gbl):
    if FBSystem().Version >= 13000.0:
        _set_vector(node, xyz, gbl, FBModelTransformationType.kModelRotation)
    else:
        _set_vector(node, xyz, gbl, FBModelTransformationMatrix.kModelRotation)


def set_scl(node, xyz, gbl):
    if FBSystem().Version >= 13000.0:
        _set_vector(node, xyz, gbl, FBModelTransformationType.kModelScaling)
    else:
        _set_vector(node, xyz, gbl, FBModelTransformationMatrix.kModelScaling)

def set_all(node, TRS=[], gbl=True):
    set_trs(node, TRS[0], gbl), set_rot(node, TRS[1], gbl), set_scl(node, TRS[2], gbl)

def add_trs(node, xyz, frame):
    frame = _change_to_FBTime(frame, -1)
    node.Translation.SetAnimated(True)
    for i, v in enumerate(xyz):
        if not v is None:
            node.Translation.GetAnimationNode().Nodes[i].FCurve.KeyAdd(frame, v)
    FBSystem().Scene.Evaluate()


def add_rot(node, xyz, frame):
    node.Rotation.SetAnimated(True)
    frame = _change_to_FBTime(frame, -1)
    for i, v in enumerate(xyz):
        if not v is None:
            node.Rotation.GetAnimationNode().Nodes[i].FCurve.KeyAdd(frame, v)
    FBSystem().Scene.Evaluate()


def add_scl(node, xyz, frame):
    node.Scaling.SetAnimated(True)
    frame = _change_to_FBTime(frame, -1)
    for i, v in enumerate(xyz):
        if not v is None:
            node.Scaling.GetAnimationNode().Nodes[i].FCurve.KeyAdd(frame, v)
    FBSystem().Scene.Evaluate()


def _change_tangent(fcurve_keys, time_range, tangent_name):
    for i, k in enumerate(fcurve_keys):
        if time_range == "all":
            _tangent_to(k, tangent_name)
            
        elif time_range[0] <= get_frame(k.Time) <= time_range[1]:
            _tangent_to(k, tangent_name)


def _tangent_to(key, tangent_name):
    if tangent_name == "linear":
        key.Interpolation = FBInterpolation.kFBInterpolationLinear
        

def trs_tangent_to(node, time_range, tangent_name, axis=[True, True, True]):
    for i in range(3):
        if axis[i]:
            try:
                keys = node.Translation.GetAnimationNode().Nodes[i].FCurve.Keys
                _change_tangent(keys, time_range, tangent_name)
            except:
                pass
    FBSystem().Scene.Evaluate()


def rot_tangent_to(node, time_range, tangent_name, axis=[True, True, True]):
    for i in range(3):
        if axis[i]:
            try:
                keys = node.Rotation.GetAnimationNode().Nodes[i].FCurve.Keys
                _change_tangent(keys, time_range, tangent_name)
            except:
                pass
    FBSystem().Scene.Evaluate()


def scl_tangent_to(node, time_range, tangent_name, axis=[True, True, True]):
    for i in range(3):
        if axis[i]:
            try:
                keys = node.Scaling.GetAnimationNode().Nodes[i].FCurve.Keys
                _change_tangent(keys, time_range, tangent_name)
            except:
                print traceback.format_exc()

    FBSystem().Scene.Evaluate()


def all_tangent_to(node, time_range, tangent_name, axis=[True, True, True]):
    for i in range(3):
        if axis[i]:
            trs_tangent_to(node, time_range, tangent_name)    
            rot_tangent_to(node, time_range, tangent_name)            
            scl_tangent_to(node, time_range, tangent_name)  
    FBSystem().Scene.Evaluate()          

def check_all_tangent(model, target_frame, axis=[True, True, True]):
    all_value = []
    all_value.append(check_trs_tangent(model, target_frame, axis))
    all_value.append(check_rot_tangent(model, target_frame, axis))
    all_value.append(check_scl_tangent(model, target_frame, axis))
    return all_value

def check_trs_tangent(model, target_frame, axis=[True, True, True]):
    value = [False, False, False]
    for i in range(3):
        if axis[i]:
            try:
                model.Translation.GetAnimationNode().Nodes[i].FCurve.Keys
                err = False
            except:
                err = True
            if not err:
                for ii, k in enumerate(model.Translation.GetAnimationNode().Nodes[i].FCurve.Keys):
                    if get_frame(k.Time) == target_frame:
                        value[i] = k.Interpolation
                        break
    
    return value

def check_rot_tangent(model, target_frame, axis=[True, True, True]):
    value = [False, False, False]
    for i in range(3):
        if axis[i]:
            try:
                model.Rotation.GetAnimationNode().Nodes[i].FCurve.Keys
                err = False
            except:
                err = True
            if not err:
                for ii, k in enumerate(model.Rotation.GetAnimationNode().Nodes[i].FCurve.Keys):
                    if get_frame(k.Time) == target_frame:
                        value[i] = k.Interpolation
                        break
    
    return value

def check_scl_tangent(model, target_frame, axis=[True, True, True]):
    value = [False, False, False]
    for i in range(3):
        if axis[i]:
            try:
                model.Scaling.GetAnimationNode().Nodes[i].FCurve.Keys
                err = False
            except:
                err = True
            if not err:
                for ii, k in enumerate(model.Scaling.GetAnimationNode().Nodes[i].FCurve.Keys):
                    if get_frame(k.Time) == target_frame:
                        value[i] = k.Interpolation
                        break
    
    return value


def _get_vector(node, gbl, mode):
    value = FBVector3d()
    node.GetVector(value, mode, gbl)
    return value


def get_trs(node, gbl):
    if FBSystem().Version >= 13000.0:
        return _get_vector(node, gbl, FBModelTransformationType.kModelTranslation)
    else:
        return _get_vector(node, gbl, FBModelTransformationMatrix.kModelTranslation)            


def get_rot(node, gbl):
    if FBSystem().Version >= 13000.0:
        return _get_vector(node, gbl, FBModelTransformationType.kModelRotation)
    else:
        return _get_vector(node, gbl, FBModelTransformationMatrix.kModelRotation)            


def get_scl(node, gbl):
    if FBSystem().Version >= 13000.0:
        return _get_vector(node, gbl, FBModelTransformationType.kModelScaling)
    else:
        return _get_vector(node, gbl, FBModelTransformationMatrix.kModelScaling)   


def get_all(node, gbl):
    return get_trs(node, gbl), get_rot(node, gbl), get_scl(node, gbl)


def remove_trs(node, time_range):
    for i in range(len(time_range)):
        time_range[i] = _change_to_FBTime(time_range[i], i)
    for i in range(3):
        try:
            node.Translation.GetAnimationNode().Nodes[i].FCurve.KeyDeleteByTimeRange(*time_range)
        except:
            print traceback.format_exc()

    FBSystem().Scene.Evaluate()


def remove_rot(node, time_range):
    for i in range(len(time_range)):
        time_range[i] = _change_to_FBTime(time_range[i], i)
    for i in range(3):
        try:
            node.Rotation.GetAnimationNode().Nodes[i].FCurve.KeyDeleteByTimeRange(*time_range)
        except:
            print traceback.format_exc()
    FBSystem().Scene.Evaluate()


def remove_scl(node, time_range):
    for i in range(len(time_range)):
        time_range[i] = _change_to_FBTime(time_range[i], i)
    for i in range(3):
        try:
            node.Scaling.GetAnimationNode().Nodes[i].FCurve.KeyDeleteByTimeRange(*time_range)
        except:
            print traceback.format_exc()
    FBSystem().Scene.Evaluate()


def remove_all(node):
    remove_trs(node, [_get_start(), "infinity", True])
    remove_rot(node, [_get_start(), "infinity", True])
    remove_scl(node, [_get_start(), "infinity", True])
    FBSystem().Scene.Evaluate()


def get_key_count(model):
    all_trs = []
    for trs in ["t", "r", "s"]:
        each = []
        for i, v in enumerate(["x", "y", "z"]):
            if trs == "t":
                if not model.Translation.GetAnimationNode():
                    each.append(0)

                elif model.Translation.GetAnimationNode().Nodes[i]:
                    each.append(model.Translation.GetAnimationNode().Nodes[i].KeyCount)
            if trs == "r":
                if not model.Rotation.GetAnimationNode():
                    each.append(0)

                elif model.Rotation.GetAnimationNode().Nodes[i]:
                    each.append(model.Rotation.GetAnimationNode().Nodes[i].KeyCount)
            if trs == "s":
                if  not model.Scaling.GetAnimationNode():
                    each.append(0)

                elif model.Scaling.GetAnimationNode().Nodes[i]:
                    each.append(model.Scaling.GetAnimationNode().Nodes[i].KeyCount)
        all_trs.append(each)
    return all_trs

def _get_start():
    return FBSystem().CurrentTake.LocalTimeSpan.GetStart()


def _change_to_FBTime(value, index):
    if isinstance(value, FBTime):
        return value
    elif isinstance(value, bool):
        return value
    elif isinstance(value, str):
        if value == "infinity":
            if index == 0:
                return FBTime.MinusInfinity
            else:
                return FBTime.Infinity
        else:
            return _change_to_FBTime(int(value), index)
    elif isinstance(value, int):
        return FBTime(0, 0, 0, value)



#@comp_property_list
def plot_selected(fps=False, keep_one_key=True, all_take=False, set_animatable_scale=True):
    """
    failed on 2013..plot only 30fps

    """
    if keep_one_key:
        m_list = FBModelList()
        FBGetSelectedModels(m_list)
        for m in m_list:
            if not m.Translation.IsAnimated():
                m.Translation.SetAnimated(True)
            if not m.Rotation.IsAnimated():
                m.Rotation.SetAnimated(True)
            if not m.Scaling.IsAnimated() and set_animatable_scale:
                m.Scaling.SetAnimated(True)
    tmp_fps = FBPlayerControl().GetTransportFpsValue()
    if not fps:
        fps = FBPlayerControl().GetTransportFpsValue()
    elif tmp_fps != fps:
        FBPlayerControl().SetTransportFps(FBTimeMode.kFBTimeModeCustom, float(fps))
    tTake = FBSystem().CurrentTake
    FBSystem().Scene.Evaluate()
    pOption = FBPlotOptions()
    pOption.PlotAllTakes = all_take
    pOption.PlotOnFlame = True
    pOption.ConstantKeyReducerKeepOneKey = keep_one_key
    pOption.UseConstantKeyReducer = False
    #pOption.PlotTranslationOnRootOnly = False
    #pOption.PreciseTimeDiscontinuities = False
    pOption.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll  
    
    if FBSystem().Version >= 14000.0:
        pOption.PlotPeriod = FBTime ( 0, 0, 0, 1)
    elif FBSystem().Version > 13000.0:
        pOption.PlotPeriod = FBTime ( 0, 0, 0, 1, 0, FBTimeMode.kFBTimeModeCustom, float(fps))
    else:
        pOption.PlotPeriod = FBTime ( 0, 0, 0, 1)
    try:
        FBSystem().CurrentTake.PlotTakeOnSelected(pOption)
    except:
        FBSystem().CurrentTake.PlotTakeOnSelectedProperties(pOption.PlotPeriod)
    FBSystem().Scene.Evaluate()

def all_key_list(model):
    return [trs_key_list(model), rot_key_list(model), scl_key_list(model)]

def all_keyinfo_list(model):
    return [trs_key_infos(model), rot_key_infos(model), scl_key_infos(model)]

def trs_key_list(model):
    all_keys = []
    if not model.Translation.GetAnimationNode():
        return []
    for i in range(3):
        each_keys = []
        if model.Translation.GetAnimationNode().Nodes[i]:
            for k in model.Translation.GetAnimationNode().Nodes[i].FCurve.Keys:
                if len(each_keys) < get_frame(k.Time):
                    for ii in range(get_frame(k.Time) - len(each_keys)):
                        each_keys.append(None)
                each_keys.append(k.Value)
        all_keys.append(each_keys)
    return all_keys

def max_len(animation_node):
    return max(len(animation_node.Nodes[0].FCurve.Keys), len(animation_node.Nodes[1].FCurve.Keys), len(animation_node.Nodes[2].FCurve.Keys))

def trs_key_infos(model):
    all_keys = []
    if not model.Translation.GetAnimationNode():
        return []

    for i in range(3):
        if model.Translation.GetAnimationNode().Nodes[i]:
            k_infos = []
            for k in model.Translation.GetAnimationNode().Nodes[i].FCurve.Keys:
                k_info = KeyInfo("trs", i, get_frame(k.Time), k.Time)

                k_info.value = k.Value                        
                k_infos.append(k_info)
                
        all_keys.append(k_infos)
    return all_keys

def rot_key_infos(model):
    all_keys = []
    if not model.Rotation.GetAnimationNode():
        return []

    for i in range(3):
        if model.Rotation.GetAnimationNode().Nodes[i]:
            k_infos = []
            for k in model.Rotation.GetAnimationNode().Nodes[i].FCurve.Keys:
                k_info = KeyInfo("trs", i, get_frame(k.Time), k.Time)

                k_info.value = k.Value                        
                k_infos.append(k_info)
                
        all_keys.append(k_infos)
    return all_keys

def scl_key_infos(model):
    all_keys = []
    if not model.Scaling.GetAnimationNode():
        return []

    for i in range(3):
        if model.Scaling.GetAnimationNode().Nodes[i]:
            k_infos = []
            for k in model.Scaling.GetAnimationNode().Nodes[i].FCurve.Keys:
                k_info = KeyInfo("trs", i, get_frame(k.Time), k.Time)

                k_info.value = k.Value                        
                k_infos.append(k_info)
                
        all_keys.append(k_infos)
    return all_keys


class KeyInfo:
    def __init__(self, trs, xyz, frame, fb_time, value=None):
        self.frame = frame
        self.value = value
        self.trs = trs
        self.xyz = xyz
        self.fb_time = fb_time

def rot_key_list(model):
    all_keys = []
    if not model.Rotation.GetAnimationNode():
        return []
    for i in range(3): 
        each_keys = []
        if model.Rotation.GetAnimationNode().Nodes[i]:
            for k in model.Rotation.GetAnimationNode().Nodes[i].FCurve.Keys:
                if len(each_keys) < get_frame(k.Time):
                    for ii in range(get_frame(k.Time) - len(each_keys)):
                        each_keys.append(None)
                each_keys.append(k.Value)
        all_keys.append(each_keys)
    return all_keys

def scl_key_list(model):
    all_keys = []
    if not model.Scaling.GetAnimationNode():
        return []
    for i in range(3):
        each_keys = []
        if model.Scaling.GetAnimationNode().Nodes[i]:
            for k in model.Scaling.GetAnimationNode().Nodes[i].FCurve.Keys:
                if len(each_keys) < get_frame(k.Time):
                    for ii in range(get_frame(k.Time) - len(each_keys)):
                        each_keys.append(None)
                each_keys.append(k.Value)
        all_keys.append(each_keys)
    return all_keys

def get_frame(fb_time):
    if FBSystem().Version >= 13000.0:
        return fb_time.GetFrame()
    else:
        return fb_time.GetFrame(True)

def copy_local_animation(src, dst, trs=[True, True, True], delete_base=False):
    if trs[0]:
        copy_local_translation(src, dst, delete_base)
    if trs[1]:
        copy_local_rotation(src, dst, delete_base)
    if trs[2]:
        copy_local_scaling(src, dst, delete_base)



def copy_local_translation(src, dst, delete_base=False):
    remove_trs(dst, [_get_start(), "infinity", True])
    if src.Translation.GetAnimationNode() is None:
        return
       
    mx = max_len(src.Translation.GetAnimationNode())
    xyz_keys = trs_key_infos(src)

    dst.Translation.SetAnimated(True)
    for i in range(mx):
        if len(xyz_keys[0]) > i:
            dst.Translation.GetAnimationNode().Nodes[xyz_keys[0][i].xyz].FCurve.KeyAdd(xyz_keys[0][i].fb_time, xyz_keys[0][i].value)
        if len(xyz_keys[1]) > i:
            dst.Translation.GetAnimationNode().Nodes[xyz_keys[1][i].xyz].FCurve.KeyAdd(xyz_keys[1][i].fb_time, xyz_keys[1][i].value)
        if len(xyz_keys[2]) > i:
            dst.Translation.GetAnimationNode().Nodes[xyz_keys[2][i].xyz].FCurve.KeyAdd(xyz_keys[2][i].fb_time, xyz_keys[2][i].value)
    if delete_base:
        remove_trs(src, [_get_start(), "infinity", True])
        src.Translation = FBVector3d(0, 0, 0)

def copy_local_rotation(src, dst, delete_base=False):
    if src.Rotation.GetAnimationNode() is None:
        return

    remove_rot(dst, [_get_start(), "infinity", True])
    mx = max_len(src.Rotation.GetAnimationNode())
    xyz_keys = rot_key_infos(src)
    dst.Rotation.SetAnimated(True)

    for i in range(mx):
        if len(xyz_keys[0]) > i:
            dst.Rotation.GetAnimationNode().Nodes[xyz_keys[0][i].xyz].FCurve.KeyAdd(xyz_keys[0][i].fb_time, xyz_keys[0][i].value)
        if len(xyz_keys[1]) > i:
            dst.Rotation.GetAnimationNode().Nodes[xyz_keys[1][i].xyz].FCurve.KeyAdd(xyz_keys[1][i].fb_time, xyz_keys[1][i].value)
        if len(xyz_keys[2]) > i:
            dst.Rotation.GetAnimationNode().Nodes[xyz_keys[2][i].xyz].FCurve.KeyAdd(xyz_keys[2][i].fb_time, xyz_keys[2][i].value)
    if delete_base:
        remove_rot(src, [_get_start(), "infinity", True])
        src.Rotation = FBVector3d(0, 0, 0)

def copy_local_scaling(src, dst, delete_base=False):
    if src.Scaling.GetAnimationNode() is None:
        return

    remove_scl(dst, [_get_start(), "infinity", True])
    mx = max_len(src.Scaling.GetAnimationNode())
    xyz_keys = scl_key_infos(src)
    dst.Scaling.SetAnimated(True)
    for i in range(mx):
        if len(xyz_keys[0]) > i:
            dst.Scaling.GetAnimationNode().Nodes[xyz_keys[0][i].xyz].FCurve.KeyAdd(xyz_keys[0][i].fb_time, xyz_keys[0][i].value)
        if len(xyz_keys[1]) > i:
            dst.Scaling.GetAnimationNode().Nodes[xyz_keys[1][i].xyz].FCurve.KeyAdd(xyz_keys[1][i].fb_time, xyz_keys[1][i].value)
        if len(xyz_keys[2]) > i:
            dst.Scaling.GetAnimationNode().Nodes[xyz_keys[2][i].xyz].FCurve.KeyAdd(xyz_keys[2][i].fb_time, xyz_keys[2][i].value)
    if delete_base:
        remove_scl(src, [_get_start(), "infinity", True])
        src.Scaling = FBVector3d(0, 0, 0)



#        if len(xyz_keys[1]) > i:
#            print xyz_keys[1][i].xyz, xyz_keys[1][i].frame, xyz_keys[1][i].value
#        
#        if len(xyz_keys[2]) > i:
#            print xyz_keys[2][i].xyz, xyz_keys[2][i].frame, xyz_keys[2][i].value


#    dst.Translation.Key()
#    for i in range(3):
#        curve = src.Translation.GetAnimationNode().Nodes[i].FCurve.Keys
#        print dir(curve)
        
#        dst.Translation.GetAnimationNode().Nodes[i].FCurve.Keys = curve
#EditBegin   

def copy_to_other_take(src, src_take, dst_take, offset_frame, trs=[True, True, True]):
    t_util.select_take(src_take)
    if src.Translation.GetAnimationNode() is None:
        return

    mx = max_len(src.Translation.GetAnimationNode())
    xyz_keys = trs_key_infos(src)
    t_util.select_take(dst_take)

    src.Translation.SetAnimated(True)
    for i in range(mx):
        if len(xyz_keys[0]) > i:
            src.Translation.GetAnimationNode().Nodes[xyz_keys[0][i].xyz].FCurve.KeyAdd(xyz_keys[0][i].fb_time.__add__(FBTime(offset_frame)), xyz_keys[0][i].value)
        if len(xyz_keys[1]) > i:
            src.Translation.GetAnimationNode().Nodes[xyz_keys[1][i].xyz].FCurve.KeyAdd(xyz_keys[1][i].fb_time.__add__(FBTime(offset_frame)), xyz_keys[1][i].value)
        if len(xyz_keys[2]) > i:
            src.Translation.GetAnimationNode().Nodes[xyz_keys[2][i].xyz].FCurve.KeyAdd(xyz_keys[2][i].fb_time.__add__(FBTime(offset_frame)), xyz_keys[2][i].value)


_KEY_ATTRS_ = ["TangentMode", "TangentClampMode", "TangentConstantMode", "TangentBreak", "Continuity", "Bias", "Interpolation", 
               "RightBezierTangent", "RightDerivative", "LeftBezierTangent", "LeftDerivative", "LeftTangentWeight", 
               "MarkedForManipulation", "RightTangentWeight",  
               "Tension"]

def get_key_attrs(key):
    dic = {"value": key.Value, "frame": key.Time.GetFrame()}
    for attr in _KEY_ATTRS_:
        value = getattr(key, attr)
        class_name = value.__class__.__name__
        if class_name.startswith("FB"):
            dic[attr] = {"type": class_name, "value": value.name}
        else:
            dic[attr] = value

    return dic

def set_key_attrs(key, attrs):
    """
    TangentMode.kFBxxxxxxxのようなアトリビュートをすべて文字列で取得するために
    globals()を使う
    """
    for k in _KEY_ATTRS_:
        dic = attrs[k]
        if isinstance(dic, dict):
            mode = getattr(globals()[dic["type"]], dic["value"])
            setattr(key, k, mode)
        else:
            setattr(key, k, dic)

def curve_gen(models, axis_ls=["tx", "ty", "tz", "rx", "ry", "rz"]):
    if isinstance(models, FBModel):
        models = [models]

    for model in models:
        for category in ["Translation", "Rotation", "Scaling"]:
            anim_node = getattr(model, category).GetAnimationNode()
            if anim_node is None:
                continue
            for i, axis in enumerate(["x", "y", "z"]):
                check = "%s%s" % (category[0].lower(), axis)
                if not check in axis_ls:
                    continue

                yield model, category, i, anim_node.Nodes[i].FCurve


def get_curves(model, axis_ls=["tx", "ty", "tz", "rx", "ry", "rz"]):
    base_curve = {}
    for m, category, i, curve in curve_gen(model, axis_ls):
        base_curve.setdefault(m, {}).setdefault(category, {})[i] = curve
    return base_curve

def scale_keys(curve, scale=1.0, invert=False):
    if invert:
        scale = 1 / scale
        #scale = abs(scale)
    if scale != 1:
        curve.EditBegin()
        for key in curve.Keys:
            key.Value = key.Value * scale

        curve.EditEnd()

    FBSystem().Scene.Evaluate()




if __name__ == "__builtin__":
    from pyfbsdk import*
    #model = FBFindModelByName("src")
    #y = FBFindModelByName("dst")    
    #copy_local_animation(model, y, [True, True, False])
    #plot_selected(30.0)
    plot_selected()
    print "DONE"

