#-*-coding:utf-8-*-

import os
import sys

try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)


import KcLibs.mobu.kc_relation_util as kc_relation_util
from pyfbsdk import FBConstraintRelation, FBSystem, FBModelPlaceHolder, FBCharacterFace, FBConnect, FBModel, FBCamera, FBConstraint, FBMaterial, FBLight
class kcRelation:
    def __init__(self, obj, force=False):
        if isinstance(obj, FBConstraintRelation):
            self.constraint = obj
        else:
            self.constraint = self.check_current_constraint(obj, force)   
    
    def check_current_constraint(self, name, force=False):
        if force:
            return FBConstraintRelation(name)
        for current in FBSystem().Scene.Constraints:
            if name == current.LongName:
                return current
        return FBConstraintRelation(name)

    def find_animation_node(self, parent, name):
        for node in parent.Nodes:
            if node.Name == name:
                return node
        return False
  
    def check_type(self, node):
        check_arr = [isinstance(node, FBModel), isinstance(node, FBCamera), isinstance(node, FBCharacterFace), 
                     isinstance(node, FBLight), isinstance(node, FBMaterial), isinstance(node, FBConstraint)]

        if True in check_arr:
            return True
        else:
            return False
        
    def set_box_gbl(self, box, gbl):
        if FBSystem().Version == 7500.0:
            box.PropertyList.Find("UseGlobalTransforms").Data = gbl
        else:
            box.UseGlobalTransforms = gbl


    def set_source_box(self, model, gbl, x=0, y=0):
        if self.check_type(model):
            source_box = kc_relation_util.find_box_by_model(self.constraint, model, True)
            if not source_box:
                source_box = self.constraint.SetAsSource(model)
            self.constraint.SetBoxPosition(source_box, x, y)
            self.set_box_gbl(source_box, gbl)
            return source_box
        return False
    
    def set_target_box(self, model, gbl, x=100, y=0):
        if self.check_type(model):
            target_box = kc_relation_util.find_box_by_model(self.constraint, model, False)
            if not target_box:
                target_box = self.constraint.ConstrainObject(model)
            self.constraint.SetBoxPosition(target_box, x, y)
            self.set_box_gbl(target_box, gbl)
            return target_box
        return False
            
    def connect_box(self, src, out_channel, in_channel, dst):
        src_out = self.find_animation_node(src.AnimationNodeOutGet(), out_channel)
        dst_in = self.find_animation_node(dst.AnimationNodeInGet(), in_channel)
        if src_out and dst_in:
            FBConnect(src_out, dst_in)
            return True
        return False
    
    def set_func_box(self, func_name_arr, x=50, y=0, data=False):
        func_box = self.constraint.CreateFunctionBox(*func_name_arr)
        if not func_box is None:
            self.constraint.SetBoxPosition(func_box, x, y)
            if data:
                while len(data) != 0:
                    self.set_func_data(func_box, data.pop(0), data.pop(0))
            return func_box
        else:
            return False

    def set_func_data(self, func_box, channel, data):
        func_box_in = self.find_animation_node(func_box.AnimationNodeInGet(), channel)
        if isinstance(data, float) or isinstance(data, int):
            data = [data]
        try:
            func_box_in.WriteData(data)
            return True
        except:
            return False
    
    def move_from_box(self, src_box, dst_box, x=300, y=0, x_step=0, y_step=0):
        if isinstance(dst_box, list):
            [self.move_from_box(src_box, l, x=x+(i*x_step), y=y+(i*y_step)) for i, l in enumerate(dst_box)]
        else:
            pos = self.constraint.GetBoxPosition(src_box)
            self.constraint.SetBoxPosition(dst_box, pos[1] + x, pos[2] + y)
        
if __name__ == "__builtin__":
    from pyfbsdk import FBModelNull, FBApplication
    #FBApplication().FileNew()
    def Lcl2Lcl():
        x = kcRelation("Lcl2Lcl")
        model = FBModelNull("src")
        src = x.set_source_box(model, False)
        model = FBModelNull("dst")
        dst = x.set_target_box(model, False)
        x.move_from_box(src, dst, x=800)
        x.connect_box(src, "Lcl Translation", "Lcl Translation", dst)

    def Gbl2Lcl():
        x = kcRelation("Gbl2Lcl")
        model = FBModelNull("src")
        src = x.set_source_box(model, True)
        model = FBModelNull("dst")
        dst = x.set_target_box(model, False)
        x.move_from_box(src, dst, x=800)
        x.connect_box(src, "Translation", "Lcl Translation", dst)

    def Lcl2Gbl():
        x = kcRelation("Lcl2Gbl")
        model = FBModelNull("src")
        src = x.set_source_box(model, False)
        model = FBModelNull("dst")
        dst = x.set_target_box(model, True)
        x.move_from_box(src, dst, x=800)
        x.connect_box(src, "Lcl Translation", "Translation", dst)

    def Gbl2Gbl():
        x = kcRelation("Gbl2Gbl")
        model = FBModelNull("src")
        src = x.set_source_box(model, True)
        model = FBModelNull("dst")
        dst = x.set_target_box(model, True)
        x.move_from_box(src, dst, x=800)
        x.connect_box(src, "Translation", "Translation", dst)

    #Gbl2Gbl()
    #Gbl2Lcl()
    #Lcl2Gbl()
    #Lcl2Lcl()
    def face_test():
        import lib.rig.motionbuilder.charaface as face_lib
        faces = face_lib.get_face_infos()
        src = faces["faceshift_Character face"].face
        dst = faces["this is test"].face
        x = kcRelation("TEST")
        x.set_source_box(src, True)
        x.set_source_box(src, True)
        model = FBModelNull("test")
        x.set_source_box(model, True)
    face_test()


