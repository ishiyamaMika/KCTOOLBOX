#-*-coding: utf8-*-

import os
import sys

from pyfbsdk import *



mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.mobu.kc_model as kc_model    
import KcLibs.mobu.kc_transport_time as kc_transport_time    

class KcRender(object):
    def __init__(self):
        self.start = False
        self.end = False
        self.fps = False
        self.bit_per_pixel = 24
        self.viewing = "model_only"
        self.cam_resolution = FBCameraResolutionMode().kFBResolutionCustom
        self.antialiasing = False
        self.render_audio = True
        self.show_camera_label = False
        self.show_safe_area = False
        self.show_time_code = True
        self.height = False
        self.width = False
        self.render_scale = 1

    def options(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
                print "options:", k, v

    def execute(self, cam, path, dialog=False):
        def _set_start_end_fps():
            frames = kc_transport_time.get_scene_time()
            if not self.start:
                self.start = frames["zoom_start"]
            if not self.end:
                self.end = frames["zoom_stop"]
            if not self.fps:
                self.fps = frames["fps"]

        def _set_viewing():
            if "model_only":
                return FBVideoRenderViewingMode().FBViewingModeModelsOnly
            elif "xray":
                return FBVideoRenderViewingMode().FBViewingModeXRay
            else:
                return FBVideoRenderViewingMode().FBViewingModeStandard

        def _set_bit_per_pixel():
            if self.bit_per_pixel == 24:
                return FBVideoRenderDepth.FBVideoRender24Bits
            else:
                return FBVideoRenderDepth.FBVideoRender32Bits

        def _set_span(start, end):
            span = FBTimeSpan()
            if not isinstance(start, FBTime):
                start = FBTime(0, 0, 0, start)
            if not isinstance(end, FBTime):
                end = FBTime(0, 0, 0, end)

            span = FBTimeSpan()
            span.Set(start, end)
            return span

        def _change_resolution(cam, scale):
            width = cam.ResolutionWidth
            height = cam.ResolutionHeight
            cam.ResolutionHeight = int(float(cam.ResolutionHeight) * float(scale))
            cam.ResolutionWidth = int(float(cam.ResolutionWidth) * float(scale))

            print "change cam to:", cam.ResolutionWidth, cam.ResolutionHeight
            return width, height

        def _revert_resolution(cam, width, height):
            cam.ResolutionWidth = width
            cam.ResolutionHeight = height
            print "revert cam to:", width, height

        if path == "":
            return False

        _set_start_end_fps()

        grabber_options = FBVideoGrabber().GetOptions()
        manager = FBVideoCodecManager()
        if dialog:
            manager.VideoCodecMode = FBVideoCodecMode.FBVideoCodecAsk
        else:
            manager.VideoCodecMode = FBVideoCodecMode.FBVideoCodecStored

        grabber_options.AntiAliasing = self.antialiasing
        grabber_options.BitsPerPixel = _set_bit_per_pixel()
        grabber_options.ViewingMode = _set_viewing()
        grabber_options.RenderAudio = self.render_audio
        grabber_options.TimeSteps = FBTime(0, 0, 0, 1)
        grabber_options.ShowCameraLabel = self.show_camera_label
        grabber_options.TimeSpan = _set_span(self.start, self.end)
        grabber_options.ShowTimeCode = self.show_time_code

        grabber_options.OutputFileName = str(path)

        if not os.path.lexists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        app = FBApplication()

        if isinstance(cam, (str, unicode)):
            cam = kc_model.find_model_by_name(cam)
            if not cam:
                print ""
                return False

        
        if self.render_scale != 1:
            width, height = _change_resolution(cam, self.render_scale)

        app.SwitchViewerCamera(cam)
        FBSystem().Scene.Evaluate()

        app.FileRender(grabber_options)
        if self.render_scale != 1:
            _revert_resolution(cam, width, height)

        return True

if __name__ == "__builtin__":
    cam = "cam_s01c006A:Merge_Camera"
    path = "E:/works/client/keica/data/test.mov"
    render = KcRender()
    render.render_scale = 0.5
    render.execute(cam, path)





