#-*-coding: utf8-*-

import maya.cmds as cmds
import maya.mel as mm
import math

def cast_color_to(value, to_1=False, to_255=False):
    if to_255:
        return [round(l*255.0) for l in value]

    elif to_1:
        return [l/255.0 for l in value]
        # return [value[0]*255.0, value[1]*255.0, value[2]*255.0]

def get_materials():
    materials = list(set([mat for mat in cmds.ls(materials=True, l=True) if "particle" not in mat]))
    return [{"name": mat, "type": cmds.objectType(mat)} for mat in materials]

def get_material_color_attr(material):
    if cmds.attributeQuery("specularColor", node=material, exists=True):
        return "{}.specularColor".format(material)

    elif cmds.attributeQuery("color", node=material, exists=True):
        return "{}.color".format(material)


    elif cmds.attributeQuery("outColor", node=material, exists=True):
        return "{}.outColor".format(material)
    else:
        return False

def get_material_color(material):
    if cmds.attributeQuery("color", node=material, exists=True):
        value = cmds.getAttr("{}.color".format(material))[0]
        return cast_color_to(value, to_255=True)

    elif cmds.attributeQuery("outColor", node=material, exists=True):
        value = cmds.getAttr("{}.outColor".format(material))[0]
        return cast_color_to(value, to_255=True)

    else:
        return [0, 0, 0]

def set_material_color(material, value):
    def _check(attr):
        if cmds.getAttr(attr, lock=True):
            print "attr was locked: pass"
            return True
        connections = cmds.listConnections(attr, s=True, d=False) or []
        if len(connections) > 0:
            print "attr was connected: pass"
            return True

        return False

    attr = get_material_color_attr(material)

    if not attr:
        cmds.warning("attribute color or outColor was not exists.change color failed.{}".format(material))
    else:
        if _check(attr):
            pass
        else:
            cmds.setAttr(attr, value[0], value[1], value[2], type="double3")


def create_file_node(name, file_path):
    def _connect_file_node(file_, p2d_):
        lst = [
                "coverage",
                "translateFrame",
                "rotateFrame",
                "mirrorU",
                "mirrorV",
                "stagger",
                "wrapU",
                "wrapV",
                "repeatUV",
                "offset",
                "rotateUV",
                "noiseUV",
                "vertexUvOne",
                "vertexUvTwo",
                "vertexUvThree",
                "vertexCameraOne",
                ["outUV", "uv"],
                ["outUvFilterSize", "uvFilterSize"]]

        for l in lst:
            if isinstance(l, str):
                l = [l, l]

            cmds.connectAttr("{}.{}".format(p2d_, l[0]), "{}.{}".format(file_, l[1]), f=True)

    file_node = cmds.shadingNode("file", name=name, asTexture=True)
    p2d_node = cmds.shadingNode("place2dTexture", asUtility=True)
    _connect_file_node(file_node, p2d_node)
    import os
    print file_node, file_path, os.path.exists(file_path)
    cmds.setAttr("{}.fileTextureName".format(file_node), file_path, type="string")
    return file_node, p2d_node


def create(name, material_type, mesh=None, color=None, **kwargs):
    node = cmds.shadingNode(material_type, name=name, asShader=True)
    
    if color is not None:
        set_material_color(node, color)

    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="{}SG".format(name))
    cmds.connectAttr("{}.outColor".format(node), "{}.surfaceShader".format(shading_group))
    
    if "file_path" in kwargs and kwargs["file_path"] is not None:
        file_node, p2d_node = create_file_node("{}_file".format(name), kwargs["file_path"])
        cmds.connectAttr("{}.outColor".format(file_node), "{}.outColor".format(node))

    if mesh is None:
        return node, shading_group

    cmds.sets(mesh, e=True, forceElement=shading_group)
    return node, shading_group


def replace_material_type(material_dict, delete=True):
    """
    type: surfaceShader, blinn, lambart and more .....
    {
     "type": "surfaceShader", 
     "replace_node": name of exist material, 
     "color": [0, 0, 0], 
     "name": name of replaced node
    }
    """
    if isinstance(material_dict, list):
        for mat in material_dict:
            replace_material_type(mat)
    else:
        if "type" in material_dict:
            replace_node = cmds.shadingNode(material_dict["type"], name=material_dict["name"], asShader=True)
        else:
            replace_node = material_dict["replace_node"]

        #cmds.replaceNode(material_dict["name"], replace_node)
        mm.eval(r'replaceNode "{}" "{}";'.format(material_dict["name"], replace_node))
        if "color" in material_dict:
            set_material_color(replace_node, material_dict["color"])

        # mm.eval('evalDeferred("showEditor(\\"{}\\")")'.format(replace_node))
        if delete:
            cmds.delete(material_dict["name"])
            cmds.rename(replace_node, material_dict["name"])
        cmds.select(material_dict["name"])

        mm.eval('evalDeferred("showEditor(\\"{}\\")")'.format(material_dict["name"]))

def remove_unused():
    mm.eval("MLdeleteUnused();")

def select_face_from_material(name):
    cmds.scriptEditorInfo(suppressInfo=True)
    cmds.scriptEditorInfo(suppressWarnings=True)
    cmds.scriptEditorInfo(suppressResults=True)

    cmds.select(name, r=True)
    cmds.hyperShade(objects=name)
    cmds.ls(sl=True)
    cmds.filterExpand(sm=34)

    return cmds.ls(sl=True)

def change_material_connections(src, dst):
    select_face_from_material(src)

    dst_con = cmds.listConnections(dst, d=True, s=False, type="shadingEngine") or []
    dst_sg = False
    if len(dst_con) > 0:
        dst_sg = dst_con[0]

    if not dst_sg:
        return False

    #cmds.select(faces)


    cmds.sets(e=True, forceElement=dst_sg)

    # cmds.delete(src)

def get_shading_engine(material):
    sgs = cmds.listConnections(material, d=True, s=False, type="shadingEngine")
    if len(sgs) == 0:
        return False
    return sgs[0]



if __name__ == "__main__":
    """
    cmds.file(u'X:/usr/hattori/test/material/aoi_from_fbx.mb', o=True, f=True)
    dic = {}
    dic["name"] = "skin"
    dic["type"] = "lambert"
    dic["color"] = [255, 255, 255]
    print "\n\n\n\n\n"
    print 1, cmds.listConnections(dic["name"], s=True, d=False)
    print 2, cmds.listConnections(dic["name"], d=True, s=False)
    print 3, cmds.listConnections(dic["name"], p=True)
    print 4, cmds.listConnections(dic["name"], c=True)

    #print replace_material_type(dic)

    print 1, cmds.listConnections(dic["name"], s=True, d=False)
    print 2, cmds.listConnections(dic["name"], d=True, s=False)
    print 3, cmds.listConnections(dic["name"], p=True)
    print 4, cmds.listConnections(dic["name"], c=True)
    """

    src = "RORAI_coat_inner"
    dst = "Rollei_Fuku_coat_inner"
    #print select_face_from_material("RORAI_face")
    #print change_material_connections("RORAI_face", "Rollei_face")

    # print get_material_color("col_mat")
    print 111
    """
    change_material_connections(src, dst)

    select_mesh(dic["name"])
    """


