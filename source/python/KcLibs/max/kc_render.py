import pymxs
# pymxs can not use quiet?
import MaxPlus
import os
def setup(start, end, width, height, **kwargs):
    """warning: you must close render dialog before you use this function.

    Args:
        start (int): render start frame
        end (int): render end frame
        width (int): render width
        height (int): render height
    """

    

    pymxs.runtime.rendStart = start
    pymxs.runtime.rendEnd = end
    pymxs.runtime.renderWidth = width
    pymxs.runtime.renderHeight = height
    if "render_frames" in kwargs:
        pymxs.runtime.rendPickupFrames = kwargs["render_frames"]
        pymxs.runtime.rendTimeType = 4
    else:
        pymxs.runtime.rendTimeType = 3
    
    if "output_path" in kwargs:
        pymxs.runtime.rendSaveFile = True
        pymxs.runtime.rendOutputFilename = kwargs["output_path"]
        if not os.path.lexists(os.path.dirname(kwargs["output_path"])):
            os.makedirs(os.path.dirname(kwargs["output_path"]))
   

    MaxPlus.Core.EvalMAXScript("renderSceneDialog.update()")
    

def rps_import(rps_path):
    pymxs.runtime.renderpresets.LoadAll(0, rps_path)


def remove_render_elements(ignore):
    manager = pymxs.runtime.maxOps.GetCurRenderElementMgr()
    for i in range(manager.numRenderElements())[::-1]:
        element = manager.getRenderElement(i)
        name = element.elementname
        if True not in [l in name for l in ignore]:
            manager.RemoveRenderElement(element)


def rename_element_paths(root_directory, group_name, ext="png"):
    manager = pymxs.runtime.maxOps.GetCurRenderElementMgr()
    for i in range(manager.numRenderElements()):
        element = manager.getRenderElement(i)
        name = element.elementname


        group_and_name = "{}_{}".format(group_name, name)
        name_list = []
        for each in group_and_name.split("_"):
            if each in name_list:
                continue
            name_list.append(each)
        
        group_and_name = "_".join(name_list)

        directory = "{}/{}/{}".format(root_directory,
                                         group_name,
                                         group_and_name)

        path = "{}/{}_.{}".format(directory,
                                  group_and_name,
                                  ext)

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        manager.SetRenderElementFilename(i, path)


def get_element_names():
    names = []
    manager = pymxs.runtime.maxOps.GetCurRenderElementMgr()
    for i in range(manager.numRenderElements()):
        element = manager.getRenderElement(i)
        names.append(element.elementname)
    return names


if __name__ == "__main__":
    # rps_import("X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_Tool/rps/CH_usagizakiSS_RenderElements.rps")
    # remove_render_elements(["_mask"])
    # print(get_element_names())
    # root_directory = "E:/aaaaa/bbbbb/cccc"
    # rename_element_paths(root_directory, "TEST")
    pymxs.runtime.rendSaveFile = True
    pymxs.runtime.rendOutputFilename = "E:/aaaddda/bbbffb/cccwwwwc_0000.png"
    path = "E:/aaasadwffa/bbbb/ccsdsdcc_0000.png"
    # cmd = 'rendOutputFilename = "{}"'.format(path)
    # MaxPlus.Core.EvalMAXScript(cmd)

    setup(0, 10, 720, 360, output_path=path)