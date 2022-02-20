from pyfbsdk import FBSystem, FBGetSelectedModels, FBModelList, FBModel, FBPropertyType, FBModel, FBModelNull, FBModelMarker, FBCamera, FBLight, FBMaterial
if FBSystem().Version < 14000.0:
    from pyfbsdk import FBFindModelByName
else:
    from pyfbsdk import FBComponentList, FBFindObjectsByName

def find_model_by_name(name, ignore_namespace=False):
    models = find_models_by_name(name, ignore_namespace)
    if len(models) > 0:
        return  models[-1]

    return False


def find_models_by_name(name, ignore_namespace=False):
    def _filter(base, model, ignore_namespace):
        if ":" in base:
            if ":" in model.LongName:
                return True
        else:
            if ":" not in model.LongName:
                return True
            elif ignore_namespace:
                return True
        return False

    if FBSystem().Version < 14000.0:
        return FBFindModelByName(name)
    else:
        comp = FBComponentList()
        if ":" in name:
            FBFindObjectsByName(name, comp, True, True)
        else:
            FBFindObjectsByName(name, comp, False, True)

        new_comp = [l for l in comp if _filter(name, l, False)]
        if len(new_comp) == 0:
            new_comp = [l for l in comp if _filter(name, l, ignore_namespace)]

        if len(new_comp) == 0:
            return []
        else:
            return new_comp

def create_custom_property(model, name, createtype, value, animatable=False):
    if createtype == "double":
        model.PropertyCreate(name,FBPropertyType.kFBPT_double , "Double", True, True, None)
    elif createtype == "vector":
        model.PropertyCreate(name,FBPropertyType.kFBPT_Vector3D , "Vector", True, True, None)
    elif createtype == "number":
        model.PropertyCreate(name, FBPropertyType.kFBPT_float, "Number", True, True, None)
    else:
        model.PropertyCreate(name, FBPropertyType.kFBPT_charptr, "String", True, True, None)

    if animatable:
        for n in model.PropertyList:
            if n.Name == name:
                n.SetAnimated(animatable)
                if isinstance(value, int) or isinstance(value, float):
                    value = [value]
                n.GetAnimationNode().SetCandidate(value)

    prop = model.PropertyList.Find(name)
    prop.Data = value

    return prop

def unselected_all(model_only=False):
    if model_only:
        m_list = FBModelList()
        FBGetSelectedModels(m_list)
        for m in m_list:
            m.Selected = False
    else:
        for comp in FBSystem().Scene.Components:
            go_flag = False
            try:
                comp.PropertyList
                go_flag = True
            except:
                go_flag = False
            if go_flag == True:
                for lowerlevel in comp.PropertyList:
                    try:
                        if lowerlevel.IsFocused == True:
                            lowerlevel.SetFocus(False)

                    except:
                        pass

                comp.Selected = False

        FBSystem().Scene.Evaluate()                

def to_object(name):
    if isinstance(name, list):
        ls = [l for l in _change_name_to_obj(name) if l != False]
        if len(ls) == 0:
            return False
        else:
            return ls
    else:
        return _change_name_to_obj(name)

def _change_name_to_obj(name):
    if isinstance(name, list) or isinstance(name, FBModelList):
        objs = []
        for n in name:
            objs.append(to_object(n))
        return objs
    elif isinstance(name, FBModel):
        return name
    else:
        model = find_model_by_name(str(name))
        if model:
            return model
#        else:
#            err_ls.append(name)
    return False

def get_root_models():
    m_list = FBModelList()
    FBGetSelectedModels(m_list)
    root = []
    for m in m_list:
        name = m
        parent = m.Parent
        if parent:
            while parent:
                name = parent
                parent = parent.Parent
        if not name in root:
             root.append(name)
    return root

def is_in_schematic_view(model):
    if isinstance(model, FBModel):
        return True
    elif isinstance(model, FBModelNull):
        return True
    elif isinstance(model, FBModelMarker):
        return True
    elif isinstance(model, FBCamera):
        return True
    elif isinstance(model, FBLight):
        return True

    return False


def find_material_by_name(name):
    for material in FBSystem().Scene.Materials:
        if material.Name == name:
            return material

    return False


def select(models):
    select_models = []
    if not isinstance(models, list):
        models = [models]

    for model in models:
        obj = to_object(model)
        if obj:
            obj.Selected = True
            select_models.append(obj)

    return select_models


def unselected_all():
    m_list = FBModelList()
    FBGetSelectedModels(m_list)
    for m in m_list:
        m.Selected = False


def select_geo_from_namespaces(namespaces):
    for model in FBSystem().Scene.RootModel.Children:
        print model.Name
        m_list = FBModelList()
        FBGetSelectedModels(m_list, model, False)
        for m in m_list:
            print m.LongName
            if not ":" in m.LongName:
                continue
        
            namespace = ":".join(m.LongName.split(":")[:-1])
            print m.LongName
            print namespace
            if not namespace in namespaces:
                continue
        
            if m.ClassName() != "FBModel":
                continue
        
            m.Selected = True

def get_selected_namespaces():
    m_list = FBModelList()
    FBGetSelectedModels(m_list)
    namespaces = []
    for m in m_list:
        namespace = ":".join(m.LongName.split(":")[:-1])
        namespaces.append(namespace)
    
    return namespaces


if __name__ == "__builtin__":
    print "-------------------------"
    print
    # m_list = FBModelList()
    # FBGetSelectedModels(m_list)
    # create_custom_property(m_list[0], "TEST", "String", "testABC", False)

    # print to_object(["eye_L_dmy", "eye_R_dmy"])

    select_geo_from_namespaces(["CH_usaoSS", "PP_grassOhishiba_10"])
