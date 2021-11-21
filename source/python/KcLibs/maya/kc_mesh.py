#-*-coding: utf8-*-

import maya.cmds as cmds
import maya.mel as mm

def set_poly_smooth(division=2, meshes=None):
    cmds.displaySmoothness(divisionsU=0, divisionsV=0, pointsWire=4, pointsShaded=1, polygonObject=1)
    meshe_list = get_mesh_parent(meshes)
    for mesh in meshe_list:
        connections = [l for l in cmds.listConnections(mesh, s=True, d=False) or [] if cmds.objectType(l) == "polySmoothFace"]
        if len(connections) > 0:
            for con in connections:
                cmds.setAttr("{}.divisions".format(con), division)
        else:
            cmds.refresh()
            cmds.polySmooth(mesh, mth=0, sdt=2, ovb=1, ofb=3, ofc=0, ost=1, ocr=0,
                            dv=division, bnr=1, c=1, kb=1, ksb=1, khe=0, kt=1,
                            kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=1)

    return meshes

def get_mesh_parent(meshes):
    if not meshes:
        meshes = cmds.ls(sl=True)
    mesh_list = []
    for each in meshes:
        if cmds.objectType(each) == "mesh":
            parent = cmds.listRelatives(each, p=True, f=True)
            mesh_list.extend(cmds.listRelatives(parent[0], c=True, ni=True, shapes=True, f=True)or [])
        else:
            mesh_list.extend([l for l in cmds.listRelatives(each, c=True, ni=True, shapes=True, f=True) or [] if cmds.objectType(l) == "mesh"])

    return mesh_list

def detach_bind(meshes):
    if meshes is not None:
        cmds.select(meshes, r=True)

    mm.eval('doDetachSkin "2" { "1","1" };')

def bind(meshes, joints):
    cmds.select(cmds.ls(meshes), r=True)
    cmds.select(cmds.ls(joints), add=True)
    mm.eval("SmoothBindSkin")


def remove_unused_influences(meshes):
    cmds.select(clear=True)
    if not meshes:
        meshes = cmds.ls(sl=True)
    for mesh in meshes:
        try:
            cmds.select(mesh, add=True)
            print "select:", mesh
        except:
            print "select failed:", mesh
    mm.eval("removeUnusedInfluences")

def copy_weight(src, dst):
    """
    src_skin = cmds.listConnections("{}.inMesh".format(src), s=True, d=False)
    dst_skin = cmds.listConnections("{}.inMesh".format(dst), s=True, d=False)

    if src_skin == 0 or dst_skin == 0:
        return False
    print src_skin
    print dst_skin
    src_skin = src_skin[0]
    dst_skin = dst_skin[0]
    """
    print cmds.objectType(src)
    if not cmds.objExists(src):
        print "src not exists: ", src
        return
    if cmds.objectType(src) == "mesh":
        src = cmds.listRelatives(src, p=True, f=True)[0]
    if not cmds.objExists(dst):
        print "src not exists: ", dst
        return
    if cmds.objectType(dst) == "mesh":
        dst = cmds.listRelatives(dst, p=True, f=True)[0]
    print "src:", src
    print "dst:", dst
    cmds.select(src, r=True)
    cmds.select(dst, add=True)
    cmds.copySkinWeights(influenceAssociation="oneToOne",
                         noMirror=True,
                         surfaceAssociation="closestPoint")


if __name__ == "__main__":
    def test01():
        cmds.file(r"H:\works\keica\data\skin_smooth\Leica.ma", o=True, f=True)
        mesh_list = cmds.listRelatives("Mesh", ad=True, f=True)
        joint_list = [l for l in cmds.listRelatives("Hips", ad=True, f=True)]
        import KcLibs.maya.kc_file_io as kc_file_io
        import shutil
        reload(kc_file_io)
        print mesh_list
        print joint_list
        detach_bind(mesh_list)
        set_poly_smooth(1, mesh_list)
        cmds.bakePartialHistory(all=True)
        print "bind------"
        bind(mesh_list, joint_list)

        current = cmds.file(sn=True, q=True)
        temp_path = "{}/keica/temp/temp.ma".format(os.environ["TEMP"])
        if not os.path.exists(os.path.dirname(temp_path)):
            os.makedirs(os.path.dirname(temp_path))
        shutil.copy2(current, temp_path)
        kc_file_io.reference_file("TEMP", temp_path)

        for mesh in mesh_list:
            temp = "|".join(["TEMP:{}".format(l) for l in mesh.split("|") if l != ""])
            try:
                copy_weight(temp, mesh)
                print "---done"
            except:
                print "---failed"

        cmds.file(removeReference=True, referenceNode=cmds.ls(type="reference")[0])

        remove_unused_influences(mesh_list)

    def test02():
        # kc_file_io.reference_file("TEMP", temp_path)
        mesh_list = get_mesh_parent(cmds.listRelatives("Mesh", ad=True, f=True))
        print mesh_list
        for mesh in mesh_list:
            temp = "TEMP:{}".format(mesh)
            print mesh, temp
            try:
                copy_weight(temp, mesh)
                print "---done"
            except:
                import traceback
                print traceback.format_exc()
                print "---failed"

    test01()
    print "done"

