import os
import sys
import pymxs

# pymxs can not use quiet?
import MaxPlus

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.max.kc_model as kc_model

def file_open(path, prompts=False):
    path = path.replace("\\", "/")
    # return MaxPlus.FileManager.Open(path, quiet=True)
    cmd = 'loadMaxFile "{}" quiet: true'.format(path)
    return MaxPlus.Core.EvalMAXScript(cmd)
    # return pymxs.runtime.loadMaxFile(path, quiet=True)

def file_save(path):
    path = path.replace("\\", "/")
    # return MaxPlus.FileManager.Save(path, quiet=True)
    return MaxPlus.Core.EvalMAXScript('saveMaxFile "{}" quiet: true'.format(path))
    # return pymxs.runtime.saveMaxFile(path, quiet=True)
    
def get_file_path():
    return "{}/{}".format(pymxs.runtime.maxFilePath, pymxs.runtime.maxFileName)
    
def file_merge(path="", namespace=None, base_layer_name=None):
    # if pymxs.runtime.mergeMaxFile(path, neverReparent=True, quiet=True):
    # if MaxPlus.FileManager.Merge(path, quiet=True):
    if MaxPlus.Core.EvalMAXScript('mergeMaxFile "{}" quiet: true'.format(path)):
        if base_layer_name is not None:
            layer = pymxs.runtime.LayerManager.GetLayerFromName(base_layer_name)
            if layer:
                layer.setname(namespace)

        return True
    return False
   
def file_import(path, param=[{"name": "Mode", "value": "#exmerge"}]):
    def _fbx_import_settings(params):
        cmd = ""
        for param in params:
            cmd += 'FBXImporterSetParam "{}" {}\n'.format(param["name"], param["value"])
        return MaxPlus.Core.EvalMAXScript(cmd)

    if param:
        
        if not _fbx_import_settings(param):
            error = "import setting failed:"
            for l in param:
                error += "{} --- {}".format(l["name"], l["value"])
            print(error)

        # return MaxPlus.Core.EvalMAXScript('{}\nimportFile "{}" #noPrompt'.format(cmd, path))
    # else:
    return MaxPlus.Core.EvalMAXScript('importFile "{}" #noPrompt'.format(path))
    # return pymxs.runtime.importFile(path, quiet=True)


if __name__ == "__main__":
    """
    base_path = r"X:\Project\_942_ZIZ\2020_ikimono_movie\_work\14_partC_Japan\26_animation\_3D_assets\camera\base.max"
    file_open(base_path)

    tsukiko_path = r"X:\Project\_942_ZIZ\2020_ikimono_movie\_work\14_partC_Japan\26_animation\_3D_assets\CH\tsukikoQuad\CH_tsukikoQuad_rig_t05_01.max"
    file_merge(tsukiko_path, namespace="CH_tsukikoQuad_01", base_layer_name="CH_tsukikoQuad")
    export_path1 = r"X:\Project\_942_ZIZ\3D\s99\c999\3D\import\ZIM_s99c999_anim_CH_tsukikoQuad.fbx"
    # file_merge(path1, namespace="CH_tsukikoQuad_02", base_layer_name="CH_tsukikoQuad")
    file_import(export_path1)
    file_save(export_path1.replace(".fbx", ".max"))


    file_open(base_path)
    file_merge(tsukiko_path, namespace="CH_tsukikoQuad_02", base_layer_name="CH_tsukikoQuad")    

    export_path2 = r"X:\Project\_942_ZIZ\3D\s99\c999\3D\import\ZIM_s99c999_anim_CH_tsukikoQuad_02.fbx"
    file_import(export_path2)
    file_save(export_path2.replace(".fbx", ".max"))

    camera_path = r"X:\Project\_942_ZIZ\2020_ikimono_movie\_work\14_partC_Japan\26_animation\_3D_assets\camera\cam_t08_03.max"
    file_open(base_path)
    file_merge(camera_path, namespace="s99c999")

    file_save(camera_path.replace(".fbx", ".max"))

    file_open(base_path)
    for each in [export_path1, export_path2, camera_path]:
        file_merge(each.replace(".fbx", ".max"))

    path2 = r"E:\works\client\keica\data\junkscript\testABC.max"
    file_save(path2)
    """
    
    """
    path = "X:/Project/_942_ZIZ/3D/s99/c999/3D/import/ZIM_s99c999_anim_CH_tsukikoQuad.max"
    # print(file_merge(path))

    path = "X:/Project/_942_ZIZ/3D/s99/c999/3D/import/ZIM_s99c999_anim_CH_tsukikoQuad_02.max"
    # print(file_merge(path))
    export_cam_path = r"X:\Project\_942_ZIZ\3D\s99\c999\3D\import\ZIM_s99c999_cam_s99c999.fbx"
    # print(os.path.exists(export_cam_path))
    print(file_import(export_cam_path, param=[{"name": "Mode", "value": "#exmerge"}]))
    """
    
    path = r"X:\Project\_942_ZIZ\2020_ikimono_movie\_work\14_partC_Japan\26_animation\_3D_assets\CH\usagizakiSS\CH_usagizakiSS_rig_t01_02.max"
    # file_merge(path)
    path = "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_Tool/rps/CH_usagizakiSS_RenderElements.rps"

    rps_import(path)