#-*- coding: utf8-*-
import os
import re
import maya.cmds as cmds
import traceback

def reference_file(ns, f_name):
    cmds.refresh()
    try:
        cam_path = cmds.file(f_name, r=True, gl=False, lrd='all', iv=True, force=True, namespace=ns)
        return True
    except:
        return False

def remove_anim_curve(anim_path):
    pattern = "createNode animCurve[A-Z]{2} -n (.*);"
    with open(anim_path) as f:
        l = f.readlines()
        for l_ in l:
            match = re.match(pattern, l)
            if match:
                print(match)



def animation_reference(anim_path, namespace):
    def _connect_anim_curve(namespace):
        curvs = cmds.ls(namespace + '_*', type='animCurve')
        results = []
        for curv in curvs:
            message = False
            cmds.setAttr(curv + '.preInfinity', 1)
            cmds.setAttr(curv + '.postInfinity', 1)
            conns = cmds.listConnections(curv, s=0, d=1, p=0)
            if conns is None:
                if not cmds.referenceQuery(curv, isNodeReferenced=True):
                    #cmds.delete(curv)
                    #message = "delete: %s" % curv
                    continue

                attr_string = curv.replace(namespace + '_', '', 1)
                max_index = attr_string.count('_')
                i = 0
                attr_string_s = attr_string.split("_")
                dst_attribute = False
                for i in range(len(attr_string_s)):
                    node = "%s:%s" % (namespace, "_".join(attr_string_s[:-i]))
                    attr = "_".join(attr_string_s[-i:])
                    
                    if cmds.objExists(node):
                        if cmds.attributeQuery(attr, exists=True, node=node):
                            dst_attribute = True
                        else:
                            """
                            WARNING:
                            一応アセットの末尾が数字の可能性も見てアトリビュートのチェックを行う
                            """
                            while attr[-1].isdigit():
                                attr = attr[:-1]
                                if cmds.attributeQuery(attr, exists=True, node=node):
                                    dst_attribute = True
                        break

                if not dst_attribute:
                    message = "%s (from anim file) target not exists?" % curv

                else:
                    src = "%s.o" % curv
                    dst = "%s.%s" % (node, attr)
                    attrs = "%s > %s" % (src, dst)

                    try:
                        cmds.connectAttr(src, dst, f=True)
                        message = "connected: %s" % attrs

                    except:
                        message = "connect failed: %s" % attrs
                        message += traceback.format_exc()
                
            else:
                message = False
            if message:
                results.append(message)
        
        return results

    # remove_anim_curve(anim_path)
    cmds.file(anim_path, r=True, dns=True)

    _connect_anim_curve(namespace)

def rename_file(path):
    if cmds.file(q=True, sn=True) != path:
        cmds.file(rename=path)
        return True
    else:
        return False

def reference_can_trace(rf_name):
    try:
        cmds.referenceQuery(rf_name, f=True)
        return True
    except:
        #import traceback
        #print(traceback.format_exc())
        return False

def save_file(path=False):
    tmp_path = path
    if path:
        path = path.replace("\\", "/")
        f, ext = os.path.splitext(path)
        rename_file(path)
    else:
        path = cmds.file(sn=True, q=True)
        f, ext = os.path.splitext(path)

    if path.endswith(".mb"):
        try:
            cmds.file(save=True, force=True, type='mayaBinary')
            print(path, "saved to mayaBinary")
        except:
            print(traceback.format_exc())
            if tmp_path:
                cmds.file(rename=tmp_path)
            else:
                cmds.file(rename=path)
            return False
    else:
        try:
            cmds.file(save=True, force=True, type='mayaAscii')
            print(path, "saved to mayaAscii")
        except:
            print(traceback.format_exc())
            if tmp_path:
                cmds.file(rename=tmp_path)
            else:
                cmds.file(rename=path)

            return False
    return True

def get_references():
    infos = []
    for ref_node in cmds.ls(type="reference"):
        info = {}
        info["node"] = ref_node
        if reference_can_trace(ref_node):
            info["without_copy_number"] = cmds.referenceQuery(ref_node, f=True, wcn=True)
            info["with_copy_number"] = cmds.referenceQuery(ref_node, f=True)
            info["is_loaded"] = cmds.referenceQuery(ref_node, il=True)

            namespace = cmds.file(cmds.referenceQuery(ref_node, f=True), namespace=True, q=True)
            has_parent = cmds.file(cmds.referenceQuery(ref_node, f=True), q=True, parentNamespace=True)
            if has_parent[0] != "":
                namespace = "%s:%s" % (has_parent[0], namespace)

            info["namespace"] = namespace

            info["trace"] = True
        else:
            info["trace"] = False
        infos.append(info)

    return infos    

def load_reference(ref_node):
    try:
        cmds.file(loadReference=True, referenceNode=ref_node)
        return True
    except:
        import traceback
        print(traceback.format_exc())
        return False

def remove_reference(ref_node, unload=False, delete=False):
    if ref_node:
        if unload:
            cmds.file(unloadReference=True, referenceNode=ref_node)
            return True
        if delete:
            cmds.file(removeReference=True, referenceNode=ref_node)
            return True
    return False

def replace_reference(src_ns, dst):
    print
    print(src_ns, dst)
    if isinstance(src_ns, list):
        for s in src_ns:
            replace_reference(s, dst)
    else:
        if os.path.splitext(dst)[1] == ".ma":
            f_format = "mayaAscii"
        else:
            f_format = "mayaBinary"
        load = cmds.referenceQuery(src_ns, il=True)

        cmds.file(dst, loadReference=src_ns, type=f_format, options="v=0")
        if not load:
            cmds.file(unloadReference=True, referenceNode=src_ns)

def load_fbx_plugin():
    if not cmds.pluginInfo("fbxmaya", q=True, l=True):
        cmds.loadPlugin("fbxmaya")

def file_import(path, mode="update"):
    if path.lower().endswith(".fbx"):
        load_fbx_plugin()

        cmds.file(path, 
                  i=True, 
                  type="FBX", 
                  ignoreVersion=True, 
                  ra=True, 
                  mergeNamespacesOnClash=False, 
                  options="v=0;",
                  pr=True)
        return True
        """
        cmds.FBXImportFillTimeline("-v", True)
        if mode == "update":
            cmds.FBXImportMode("-v", "exmerge")
        elif mode == "add":
            cmds.FBXImportMode("-v", "add")
        else:
            cmds.FBXImportMode("-v", "merge")

        cmds.FBXImport("-f", path)
        """
    return True


if __name__ == "__main__":
    reference_file 

    a = ["StudioRN", "X:/Project/_952_SA/03_asset/05_bg/Studio/Studio.ma"]
    b = ["ep00s01c001_bg_Studio_primaryRN", "X:/Project/_952_SA/04_animation/AN/ep00/s01/c001/_convert/ma/ep00s01c001_bg_Studio_primary.ma"]
    

    # remove_reference(a[0], delete=True)           
    remove_reference(b[0], delete=True)           
    # reference_file("Studio", a[1])
    cmds.file(b[1], importReference=True)
