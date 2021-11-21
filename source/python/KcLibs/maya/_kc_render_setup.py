#-*- coding: utf8-*-

import os
import sys
import json
import copy
import maya.cmds as cmds

import maya.app.renderSetup.model.override as override
import maya.app.renderSetup.model.connectionOverride as connectionOverrideModel
import maya.app.renderSetup.model.selector as selector
import maya.app.renderSetup.model.collection as collection

import maya.app.renderSetup.model.renderLayer as renderLayer
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.app.renderSetup.model.override as overrideModel

mod = "%s/source/python" % os.environ["KEICA_TOOL_PATH"]
if not mod in sys.path:
    sys.path.append(mod)

import KcLibs.maya.kc_material as kc_material
import KcLibs.maya.kc_light as kc_light
import KcLibs.maya.kc_mesh as kc_mesh
reload(kc_material)
reload(kc_light)
reload(kc_mesh)

_RENDER_SETUP_ = None



def update_instance():
    global _RENDER_SETUP_
    _RENDER_SETUP_ = renderSetup.instance()

update_instance()

def get_layer_list():
    return _RENDER_SETUP_.getRenderLayers()

def get_master_layer():
    for each in get_layer_list():
        print dir(_RENDER_SETUP_)
        print each.name()

def _append_namespace(value, namespace, key=None):
    def _split_and_merge(value_, namespace):
        if value_ == "":
            return value_

        elif "|" in value_:
            value_s = value_.split("|")
            if ":" in value_:
                pass
                value_ls = []
                for value__ in value_s:
                    if value__ == "":
                        continue
                    value__s = value__.split(":")

                    value_ls.append("{}:{}".format(namespace, value__s[1]))

                return "|{}".format("|".join(value_ls))

            else:
                return "|{}".format("|".join(["{}:{}".format(namespace, l) for l in value_s][1:]))

        if ":" in value_:
            value_s = value_.split(":")
            return "|{}:{}".format(namespace, value_s[1])
        else:
            return "|{}:{}".format(namespace, value_)

    if isinstance(value, dict):
        dic = {}
        for k, v in value.items():
            dic[k] = _append_namespace(v, namespace, k)
        return dic

    elif isinstance(value, (str, unicode)):
        if "defaultRenderGlobals" in value:
            pass
        elif key == "staticSelection":
            return _split_and_merge(value, namespace)
            if "|" in value:
                value_s = value.split("|")
                return "|{}".format("|".join(["{}:{}".format(namespace, l) for l in value_s][1:]))
        elif key == "connectionStr":
            print key, value
            if ".message" in value:
                return _split_and_merge(value, namespace)[1:]
            else:
                return value

        return value

    elif isinstance(value, list):
        lst = []
        for each in value:
            lst.append(_append_namespace(each, namespace))
        return lst

    return value

def export_all_layer(path, use_namespace=False, namespace=""):
    def _export_file(file_name, layer=None):
        with open(file_name, "w+") as file:
            json.dump(_RENDER_SETUP_.encode(None), fp=file, indent=2, sort_keys=True)
    _export_file(path)
    js = json.load(open(path, "r"), "utf8")

    if use_namespace:
        js_list = []
        for j in js["renderSetup"]["renderLayers"]:
            js_list.append(_append_namespace(j, namespace))

        js_ = js_list
    else:
        js_ = js["renderSetup"]["renderLayers"]
    json.dump(js_, open(path, "w"), "utf8", indent=2)


def import_layer(path, mode="append", use_namespace=False, namespace=None):
    js = json.load(open(path, "r"), "utf8")
    new_js = []
    for j in js:
        if use_namespace:
            name_s = j["renderSetupLayer"]["name"].split("_")
            j["renderSetupLayer"]["name"] = "{}_{}".format(namespace, "_".join(name_s[1:]))
            new_js.append(_append_namespace(j, namespace))

    if use_namespace:
        js = new_js

    js_ = {"renderSetup": {}}
    js_["renderSetup"]["renderLayers"] = js
    
    if mode == "append":
        mode = renderSetup.DECODE_AND_RENAME

    elif mode == "override":
        mode = renderSetup.DECODE_AND_OVERWRITE

    else:
        mode = renderSetup.DECODE_AND_MERGE

    renderSetup.instance().decode(js_, mode, None)

def get_layer(name, switch_to=False):
    for each in _RENDER_SETUP_.getRenderLayers():
        if each.name() == name:
            if switch_to:
                _RENDER_SETUP_.switchToLayer(each)
            return each
    return False


def get_override(collection, name):
    for override in collection.getOverrides():
        if override.name() == name:
            return override
    return False


def create_layer(name):
    layer = get_layer(name)
    if layer:
        return layer

    return _RENDER_SETUP_.createRenderLayer(name)


def create_layer_with_collections(name, **kwargs):
    layer = create_layer(name)
    if not "collections" in kwargs:
        return layer

    for collection_info in kwargs["collections"]:
        if collection_info["type"] == "material":
            set_material_override(layer, collection_info)
        elif collection_info["type"] == "render_setting":
            set_render_settings_override(layer, collection_info)
        elif collection_info["type"] == "light":
            set_light_override(layer, collection_info)
        elif collection_info["type"] == "connection":
            set_connection_override(layer, collection_info)
            if collection_info["attribute"] == "primaryVisibility":
                copy_ = copy.deepcopy(collection_info)
                copy_["attribute"] = "castsShadows"
                copy_["value"] = True
                # copy_["name"] = copy_["name"].replace("priVis_", "")
                copy_["name"] = "castSdw_ov"
                set_connection_override(layer, copy_)
        else:
            collection_name = collection_info.get("collection_name", "{}_collection".format(layer.name()))
            create_collection(layer, 
                              collection_name, 
                              collection_info.get("static_models", None),
                              pattern=collection_info.get("pattern", None), 
                              force=collection_info.get("force", False))

def get_layer_info(layer_name, namespace=""):
    layer = get_layer(layer_name, switch_to=True)
    layer_info = {}
    layer_info["namespace"] = namespace
    layer_info["name"] = layer_name.replace("{}_".format(namespace), "")
    layer_info["is_active"] = False

    material_types = ["surfaceShader",
                      "anisotropic",
                      "blinn",
                      "lambert",
                      "layeredShader",
                      "phong",
                      "phongE",
                      "shadingMap",
                      "useBackground"]

    cols = []
    li_info = {}
    for col in layer.getCollections():
        dic = {}
        dic["info"] = {}
        dic["name"] = col.name()
        dic["mesh_pattern"] = col.getSelector().getPattern()
        dic["is_modified"] = False
        dic["meshes"] = kc_mesh.get_mesh_parent(list(col.getSelector().getStaticNames()))
        dic["texture_pattern"] = False
        if col.kTypeName == "lightsCollection":
            dic["info"]["light_group"] = True
            for c in col.getCollections():
                li_names = c.getSelector().getStaticNames()
                li_names = list(li_names)
                if len(li_names) > 0:
                    li_name = li_names[0]
                    if "light_name_line" in li_info:
                        li_info["light_name_line"] += ";{}".format(li_name)
                    else:
                        li_info["light_name_line"] = li_name

                    li_info["light_type_combo"] = cmds.objectType(li_name)
                    li_info["light_group"] = True
                    for ov in c.getOverrides():
                        print ov.kTypeName
                        if "intensity" in ov.name():
                            li_info["light_intensity_spin"] = ov.getAttrValue()
            continue

        for ov in col.getOverrides():
            if ov.kTypeName == "materialOverride":
                dic["info"]["material_group"] = True
                shading_engine = cmds.listConnections(ov.attrValuePlugName(), s=True, d=False, type="shadingEngine") or []
                if len(shading_engine) > 0:
                    materials =  cmds.listConnections(shading_engine, s=True, d=False) or []
                    for mat in materials:
                        if cmds.objectType(mat) in material_types:
                            dic["info"]["mat_name_line"] = mat
                            dic["info"]["mat_type_combo"] = cmds.objectType(mat)
                            dic["info"]["mat_color_group"] = True

                            color = kc_material.get_material_color(mat)
                            dic["info"]["mat_r_spin"] = color[0]
                            dic["info"]["mat_g_spin"] = color[1]
                            dic["info"]["mat_b_spin"] = color[2]

                        file_node = cmds.listConnections(mat, s=True, d=False, type="file") or []
                        if len(file_node) > 0:
                            dic["info"]["mat_texture_group"] = True
                            dic["info"]["mat_texture_line"] = cmds.getAttr("{}.fileTextureName".format(file_node[0]))
        
        cols.append(dic)

    layer_info["info"] = li_info
    layer_info["collections"] = cols
    return layer_info


def set_light_override(layer, override):
    col = create_light_collection(layer)
    ov02_name = "{}_collection".format(override["name"])
    ov02 = create_collection(col, ov02_name)
    if not ov02:
        ov02 = col.createCollection(ov02_name)

    ov03_name = "{}_{}".format(ov02.name(), override["attribute"])
    ov03 = get_override(ov02, ov03_name)
    if not cmds.objExists(override["node"]):
        override["node"] = kc_light.create(override["light_type"], override["node"], intensity=0.0)
    
    if "depthmap_shadow" in override and override["depthmap_shadow"]:
        cmds.setAttr("{}.useDepthMapShadows".format(override["node"]), 1)
        if "depthmap_shadow_value" in override:
            cmds.setAttr("{}.dmapResolution".format(override["node"]), override["depthmap_shadow_value"])
        if cmds.objExists(override["node"]):
            trans = cmds.listRelatives(override["node"], p=True)[0]
            if cmds.getAttr("{}.rx".format(trans)) == 0.0:
                cmds.setAttr("{}.rx".format(trans), -90)
                cmds.setAttr("{}.ty".format(trans), 10)


    if not ov03:
        ov03 = ov02.createOverride(ov03_name, overrideModel.AbsOverride.kTypeId)
        ov03.finalize("{}.{}".format(override["node"], override["attribute"]))

    selector = ov02.getSelector()
    selector.staticSelection.set([override["node"]])
    cmds.setAttr("{}.attrValue".format(ov03.name()), override["value"])




def create_render_collection(layer):
    if layer.hasRenderSettingsCollectionInstance():
        for col in layer.getCollections():
            if col.kTypeName == "renderSettingsCollection":
                return col

    # col = collection.create("RenderSettingsCollection", collection.RenderSettingsCollection.kTypeId)
    col = layer.renderSettingsCollectionInstance()
    # layer.attachCollection(0, col)
    # print dir(layer)
    col.getSelector().setStaticSelection("defaultRenderGlobals\ndefaultResolution\ndefaultRenderQuality")
    return col


def create_light_collection(layer):
    if layer.hasLightsCollectionInstance():
        for col in layer.getCollections():
            if col.kTypeName == "lightsCollection":
                return col

    col = layer.lightsCollectionInstance()

    return col


def set_connection_override(layer, override):
    collection_name = override.get("collection_name", "{}_collection".format(layer.name()))
    col = create_collection(layer, collection_name, override.get("static_models", None), pattern=override.get("pattern", None), force=override.get("force", False))
    name = col.name()
    col2 = create_collection(col, "{}_all".format(collection_name), pattern="*")
    col2.getSelector().setFilterType(selector.Filters.kShapes)
    ov = get_override(col2, override["name"])

    if not ov:
        ov = col2.createOverride(override["name"], overrideModel.AbsOverride.kTypeId)
        if override.get("static_models", None):
            if isinstance(override["static_models"], list):
                root = override["static_models"][0]
            else:
                root = override["static_models"]
            if cmds.objectType(root) == "mesh":
                pass
            else:
                print cmds.listRelatives(root, type="shape")
                root = cmds.listRelatives(root, type="shape")[0]

            ov.finalize("{}.{}".format(root, override["attribute"]))
        #ov.finalize("{}.{}".format(override["node"], override["attribute"]))
    #selector = ov.getSelector()
    #selector.staticSelection.set([override["node"]])
    cmds.setAttr("{}.attrValue".format(ov.name()), override["value"])

def create_collection(layer, name, static_models=None, pattern=None, force=False):
    info = {}
    col = False
    if not force:
        for col in layer.getCollections():
            if col.name() == name:
                return col

    col = layer.createCollection(name)
    if static_models is not None:
        model_list = []
        if isinstance(static_models, (str, unicode)):
            static_models = [static_models]
        for model in static_models:
            if not cmds.objExists(model):
                continue
            if cmds.objectType(model) == "mesh":
                res = cmds.listRelatives(model, p=True, f=True)
                if len(res) == 1:
                    model_list.append(res[0])
            else:
                model_list.append(model)
        if len(model_list) > 0:
            col.getSelector().setStaticSelection("\n".join(model_list))

    if pattern is not None:
        col.getSelector().setPattern(pattern)

    return col


def set_material_override(layer, override):
    """

    :param layer:
    :param override: {name:
                       static_models: None,
                       pattern: None,
                       force: False,
                       color: [0, 0, 0],
                       collection_name: layer_collection,
                       material_type: lambert,
                       material_name: collection_mat,
                       file_path: path}
    :return:
    """
    collection_name = override.get("collection_name", "{}_collection".format(layer.name()))
    col = create_collection(layer, collection_name, override.get("static_models", None), pattern=override.get("pattern", None), force=override.get("force", False))

    name = col.name()
    ov = get_override(col, override["name"])
    if not ov:
        ov = col.createOverride(override["name"], connectionOverrideModel.MaterialOverride.kTypeId)

    color = override.get("color", None)
    if color is not None:
        color = kc_material.cast_color_to(color, to_1=True)
        #if color[0] > 1.0 or color[1] > 1.0 or color[2] > 1.0:
        #    color[0] = color[0] / 255.0
        #    color[1] = color[1] / 255.0
        #    color[2] = color[2] / 255.0
    material_name = override.get("material_name", "{}_mat".format(name))
    if cmds.objExists(material_name):
        material = material_name
        shading_engine = kc_material.get_shading_engine(material_name)
        if color is not None:
            kc_material.set_material_color(material, color)

    else:
        material, shading_engine = kc_material.create(material_name,
                                                      override["material_type"],
                                                      color=override.get("color", None),
                                                      file_path=override.get("file_path", None))

    ov.setMaterial(shading_engine)
    # info.setdefault("overrides", []).append({"material": material, "shading_engine": shading_engine})


def set_render_settings_override(layer, override):
    col = create_render_collection(layer)

    ov = get_override(col, override["name"])
    if not ov:
        ov = col.createOverride(override["name"], overrideModel.AbsOverride.kTypeId)
        # renderSettingsの場合はnodeを省略できるが仕様の統一のために冗長な書き方をしている
        ov.finalize("{}.{}".format(override.get("node", "defaultRenderGlobals"), override["attribute"]))

    if isinstance(override["value"], (str, unicode)):
        cmds.setAttr("{}.attrValue".format(ov.name()), override["value"], type="string")
    else:
        cmds.setAttr("{}.attrValue".format(ov.name()), override["value"])

if __name__ == "__main__":
    def create_get_layer__TEST():
        create_layer("test")
        get_layer("test")

    def create_collection__TEST():
        layer = create_layer("test")
        meshes = cmds.ls(type="mesh", l=True)
        overrides = []
        overrides.append({"type": "material", "name": "color", "color": [255, 0, 255], "material_type": "surfaceShader"})
        overrides.append({"type": "render_setting", "name": "start_frame", "node": "defaultRenderGlobals", "attribute": "startFrame", "value": 30})
        overrides.append({"type": "render_setting", "name": "end_frameXX", "node": "defaultRenderGlobals", "attribute": "endFrame", "value": 45})

        file_path = u"X:\\images\\icon\\CheckBack.png"
        create_collection(layer, "test_col", static_models=meshes, force=True, overrides=overrides)
        overrides = []
        overrides.append({"type": "render_setting", "name": "start_frame", "node": "defaultRenderGlobals", "attribute": "startFrame", "value": 10})
        overrides.append({"type": "render_setting", "name": "end_frameXX", "node": "defaultRenderGlobals", "attribute": "endFrame", "value": 30})
        overrides.append({"type": "render_setting", "name": "end_frameXX", "node": "defaultRenderGlobals", "attribute": "imageFilePrefix", "value": "X:\\test\\<layer>"})
        overrides.append({"type": "material", "name": "texture", "file_path": file_path, "material_type": "surfaceShader"})
        overrides.append({"type": "light", "name": "lightzzzz", "node": "|ambientLight1|ambientLightShape1", "value": 4, "attribute": "intensity"})
        layer2 = create_layer("test2")
        create_collection(layer2, "test_sdw2", static_models=meshes, force=True, overrides=overrides)

    def create_collection02__TEST():
        layer = create_layer("test")
        meshes = cmds.ls(type="mesh", l=True)
        print meshes
        overrides = []
        # overrides.append({"type": "material", "name": "color", "color": [255, 255, 255], "material_type": "surfaceShader"})
        overrides.append({"type": "render_setting", "name": "start_frame", "attribute": "defaultRenderGlobals.startFrame", "value": 30})
        create_collection(layer, "test_col", static_models=meshes, force=False, overrides=overrides, render_setting_only=True)
        create_render_collection(layer, "start_frame", "defaultRenderGlobals.startFrame", 25)

    def create_light_collection__TEST():
        layer = create_layer("test")
        l = cmds.ls(type="light", l=True)
        print l[0]
        create_light_collection(layer, "amb_light", l[0], "intensity", 0.4)

    def create_layer_with_collections__TEST():
        # (name, static_models, ** kwargs)
        file_path = u"X:\\images\\icon\\CheckBack.png"
        meshes = cmds.ls(type="mesh", l=True)
        print "--", meshes
        l = cmds.ls(type="light", l=True)
        overrides = []
        overrides.append({"type": "material", "collection_name": "Ikon_texture_collection", "name": "Ikon_texture_ov", "file_path": file_path, "material_type": "surfaceShader", "static_models": meshes})
        overrides.append({"type": "material", "collection_name": "Ikon_model_collection", "name": "Ikon_model_mat_ov", "static_models": meshes, "color": [100, 100, 0], "material_type": "surfaceShader"})
        overrides.append({"type": "render_setting", "name": "start_frame_ov", "node": "defaultRenderGlobals", "attribute": "startFrame",  "value": 20})
        overrides.append({"type": "render_setting", "name": "end_frame_ov", "node": "defaultRenderGlobals", "attribute": "endFrame",  "value": 20})
        overrides.append({"type": "render_setting", "name": "renderer_ov", "node": "defaultRenderGlobals", "attribute": "currentRenderer",  "value": "mayaSoftware"})
        plane = cmds.polyPlane()
        overrides.append({"type": "render_setting", "name": "raytracing_ov", "node": "defaultRenderQuality", "attribute": "enableRaytracing",  "value": True})
        overrides.append({"type": "connection", "node": "defaultRenderQuality", "collection_name": "priVis_collection", "name": "primary_visibility_ov", "attribute": "primaryVisibility",  "value": False, "static_models": plane[0]})

        #overrides.append({"type": "light", "name": "{}".format(l[0].split("|")[-1]), "node": l[0], "value": 2, "attribute": "intensity"})
        #overrides.append({"type": "light", "name": "{}".format(l[1].split("|")[-1]), "node": l[1], "value": 0, "attribute": "intensity"})

        create_layer_with_collections("test", collections=overrides)

    def get_layer_info__TEST():
        info = get_layer_info("test01_COL", "test01")
        path = "H:/daily/20181218/renderSetup/info/tools/aaa.json"
        import json
        json.dump(info, open(path, "w"), "utf8", indent=4)
        return info
    
    def import_layer__TEST():
        path = "X:/Project/_952_SA/03_asset/00_master/maya/_info/render_preset/Ikon_renderSet_.json"
        import_layer(path)

    #print create_layer_with_collections__TEST()
    #print 1

    get_master_layer()

