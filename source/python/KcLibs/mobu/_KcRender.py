#-*-coding: utf8-*-

import os
import sys
import shutil
import datetime

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.mobu.kc_model as kc_model    
import KcLibs.mobu.kc_transport_time as kc_transport_time    
import KcLibs.mobu.kc_camera as kc_camera    

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

            return width, height

        def _revert_resolution(cam, width, height):
            cam.ResolutionWidth = width
            cam.ResolutionHeight = height

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
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = "{}/KcToolBox/temp/mov/{}_{}".format(os.environ["TEMP"].split(";")[0], now, os.path.basename(path))

        # grabber_options.OutputFileName = str(path)
        grabber_options.OutputFileName = str(temp_path)

        if not os.path.lexists(os.path.dirname(temp_path)):
            os.makedirs(os.path.dirname(temp_path))

        app = FBApplication()

        selected_pane = FBSystem().Scene.Renderer.GetSelectedPaneIndex()
        if cam == "switcher":
            kc_camera.change_cam("switcher", pane=selected_pane)
        else:
            if isinstance(cam, str):
                cam = kc_model.find_model_by_name(cam)
                if not cam:
                    return False
                kc_camera.change_cam(cam, selected_pane)
            
            if self.render_scale != 1:
                width, height = _change_resolution(cam, self.render_scale)

            kc_camera.change_cam(cam, pane=selected_pane)
        """
        try:
            app.SwitchViewerCamera(cam)
        except:
            try:
                FBSystem().Scene.Renderer.SetCameraInPane(cam, selected_pane)
            except:
                return False
        """

        FBSystem().Scene.Evaluate()

        app.FileRender(grabber_options)
        if self.render_scale != 1 and cam != "switcher":
            _revert_resolution(cam, width, height)

        if not os.path.lexists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        
        shutil.copy2(temp_path, path)
        os.remove(temp_path)
        print("copy: {} to {}".format(temp_path, path))

        return True

if __name__ in ["__builtin__", "builtins"]:
    cam = "switcher"
    path = "K:/DTN/LO/LO/movie/master/test.mov"
    render = KcRender()
    render.render_scale = 0.5
    render.start = 0
    render.end = 200
    print(render.execute(cam, path))
