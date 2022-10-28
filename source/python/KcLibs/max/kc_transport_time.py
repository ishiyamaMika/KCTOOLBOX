import pymxs
import os
import MaxPlus

def get_scene_time():
    start = int(pymxs.runtime.animationRange.start)
    end = int(pymxs.runtime.animationRange.end)
    fps = int(pymxs.runtime.frameRate)
    return start, end, fps

def set_scene_time(start, end, fps):
    MaxPlus.Core.EvalMAXScript("frameRate  = {}".format(fps))
    MaxPlus.Core.EvalMAXScript("animationRange = interval {} {}".format(start, end))

if __name__ == "__main__":
    # get_scene_time()
    set_scene_time(5, 100,30)
    print(get_scene_time())
print(pymxs.runtime.rendTimeType)
pymxs.runtime.rendTimeType = 4