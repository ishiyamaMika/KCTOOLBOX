import pymxs

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

