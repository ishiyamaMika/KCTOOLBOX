from pyfbsdk import *

def get_fps():
    return FBPlayerControl().GetTransportFpsValue()

def get_scene_time():
    fps = get_fps()
    start_frame = FBPlayerControl().LoopStart
    in_frame = FBPlayerControl().ZoomWindowStart
    out_frame= FBPlayerControl().ZoomWindowStop
    end_frame = FBPlayerControl().LoopStop

    return {"loop_start": int(FBTime.GetTimeString(start_frame).replace("*", "")),
            "zoom_start": int(FBTime.GetTimeString(in_frame).replace("*", "")),
            "zoom_stop": int(FBTime.GetTimeString(out_frame).replace("*", "")), 
            "loop_stop": int(FBTime.GetTimeString(end_frame).replace("*", "")), 
            "fps": fps}

def set_fps(fps):
    FBPlayerControl().SetTransportFps(FBTimeMode.kFBTimeModeCustom, float(fps))


def set_scene_time(loop_start, loop_stop, zoom_start=-1, zoom_stop=-1, fps=-1):
    if fps is not -1:
        set_fps(fps)

    FBPlayerControl().LoopStop = FBTime(0, 0, 0, loop_stop)
    FBPlayerControl().LoopStart = FBTime(0, 0, 0, loop_start)


    time_span = FBTimeSpan(FBTime(0, 0, 0, loop_start), FBTime(0, 0, 0, loop_stop))
    FBSystem().CurrentTake.LocalTimeSpan = time_span

    if zoom_start != -1:
        FBPlayerControl().ZoomWindowStart = FBTime(0, 0, 0, zoom_start)

    if zoom_stop != -1:
        FBPlayerControl().ZoomWindowStop = FBTime(0, 0, 0, zoom_stop)

def set_zoom_time(start, stop, fps=-1):
    if fps is not -1:
        set_fps(fps)

    scene_time = get_scene_time()
    if stop > scene_time["loop_stop"]:
        FBPlayerControl().LoopStop = FBTime(0, 0, 0, stop)

    if start < scene_time["loop_start"]:
        FBPlayerControl().LoopStart = FBTime(0, 0, 0, start)


    FBPlayerControl().ZoomWindowStart = FBTime(0, 0, 0, start)
    FBPlayerControl().ZoomWindowStop = FBTime(0, 0, 0, stop)

if __name__ == "__builtin__":
    set_scene_time(10, 40, 20, 30, 24)
    print get_scene_time()

