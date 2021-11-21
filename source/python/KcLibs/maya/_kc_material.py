#-*-coding: utf8-*-

import maya.cmds as cmds
import maya.mel as mm

def get_materials():
    return [{"name": mat, "type": cmds.objectType(mat)} for mat in cmds.ls(materials=True) if "particle" not in mat]


def set_material_color(material, value):
    def _check(attr):

        if cmds.getAttr(attr, lock=True):
            print "attr was locked: pass"
            return True
        connections = cmds.listConnections(attr, s=True, d=False)
        print connections
        if len(connections) > 0:
            print "attr was connected: pass"
            return True

        return False

    if cmds.attributeQuery("color", node=material, exists=True):
        name = "{}.color".format(material)
        if _check(name):
            pass
        else:
            cmds.setAttr(name, value[0], value[1], value[2], type="double3")

    elif cmds.attributeQuery("outColor", node=material, exists=True):
        name = "{}.outColor".format(material)
        if _check(name):
            pass
        else:
            cmds.setAttr(name, value[0], value[1], value[2], type="double3")
    else:
        cmds.warning("attribute color or outColor was not exists.change color failed.{}".format(material))


def replace_material_type(material_dict):
    if isinstance(material_dict, list):
        for mat in material_dict:
            replace_material_type(material_dict)
    else:
        if "type" in material_dict:
            replace_node = cmds.shadingNode(material_dict["type"], asShader=True)
        else:
            replace_node = material_dict["replace_node"]
        print "-----------", replace_node

        #cmds.replaceNode(material_dict["name"], replace_node)
        mm.eval(r'replaceNode "{}" "{}";'.format(material_dict["name"], replace_node))
        if "color" in material_dict:
            set_material_color(replace_node, material_dict["color"])

        # mm.eval('evalDeferred("showEditor(\\"{}\\")")'.format(replace_node))
        cmds.delete(material_dict["name"])
        cmds.select(replace_node)
        cmds.rename(replace_node, material_dict["name"])


def select_mesh(material):
    return
    cmds.hyperShade(object=material)




if __name__ == "__main__":
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

    print replace_material_type(dic)

    print 1, cmds.listConnections(dic["name"], s=True, d=False)
    print 2, cmds.listConnections(dic["name"], d=True, s=False)
    print 3, cmds.listConnections(dic["name"], p=True)
    print 4, cmds.listConnections(dic["name"], c=True)

    select_mesh(dic["name"])
