import os
import sys
import MaxPlus

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])

if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env


def file_open(path, prompts=False):
    path = path.replace("\\", "/")
    MaxPlus.FileManager.Open(path, noPrompts=not prompts)


def file_save(path):
    path = path.replace("\\", "/")
    try:
        MaxPlus.FileManager.Save(path)
        return True
    except:
        return False

def get_file_path():
    return MaxPlus.FileManager.GetFileNameAndPath()

def file_merge(file_path="", namespace=None, padding=2, force=False):
    print(111)
    # MaxPlus.FileManager.import(file_path)
    if namespace is not None and not force:
        root_node = MaxPlus.Core.GetRootNode()
        count = root_node.GetNumChildren()
        for i in range(count):
            name = root_node.GetChild(i).GetName()  
            if not ":" in name:
                continue
            name_s = name.split(":")
            namespace_ = ":".join(name_s[:-1])
            if namespace == namespace_:
                return True
    
    return MaxPlus.FileManager.Merge(file_path)
    
    
                
    
def file_import(file_path, suppress_prompts=True):
    return MaxPlus.FileManager.Import(file_path, SuppressPrompts=suppress_prompts)


if __name__ == "__main__":
    path = r"E:\works\client\keica\_942_ZIZ\2020_ikimono_movie\_work\14_partC_Japan\26_animation\_3D_assets\CH\tsukikoQuad\CH_tsukikoQuad_rig_t05_01.max"
    print(file_merge(path, namespace="Mia"))
    print(1111)
    
    print(MaxPlus.INode.GetINodeByName("CH_tsukikoQuad:*"))