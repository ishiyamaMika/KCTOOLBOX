import pymxs
# pymxs can not use quiet?
import MaxPlus

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


def rps_import(rps_path):
    pymxs.runtime.renderpresets.LoadAll(0, rps_path)


def remove_render_elements(ignore):
    manager = pymxs.runtime.maxOps.GetCurRenderElementMgr()
    for i in range(manager.numRenderElements())[::-1]:
        element = manager.getRenderElement(i)
        name = element.elementname
        if True not in [l in name for l in ignore]:
            print("remove: {}".format(name))
            manager.RemoveRenderElement(element)


def rename_element_paths(root_directory, group_name, ext="png"):
    manager = pymxs.runtime.maxOps.GetCurRenderElementMgr()
    for i in range(manager.numRenderElements()):
        element = manager.getRenderElement(i)
        name = element.elementname

        directory = "{}/{}/{}_{}".format(root_directory,
                                         group_name,
                                         group_name, 
                                         name)
        path = "{}/{}_{}_0000.{}".format(directory,
                                         group_name,
                                         name,
                                         ext)

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
    # print dir(pymxs.runtime)
    # print(get_element_names())
    root_directory = "E:/aaaaa/bbbbb/cccc"
    rename_element_paths(root_directory, "TEST")
