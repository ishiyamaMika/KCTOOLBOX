import os
import sys
import pprint
import pymxs
import subprocess
import shutil

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.max.kc_model as kc_model
_PIECE_NAME_ = "RenderScene"

class RenderScene(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(RenderScene, self).__init__(**args)
        self.name = _PIECE_NAME_
        
        self.ffmpeg = "{}\\bin\\ffmpeg-20191126-59d264b-win64-static\\bin\\ffmpeg.exe".format(os.environ["KEICA_TOOL_PATH"].replace("/", "\\"))


    def png_to_movie(self, src_path, dst_path, fps):
        # cmd = '{} -i "{}" -vcodec libx264 -pix_fmt yuv420p -q 0 -framerate {} "{}"'.format(self.ffmpeg, src_path, fps, dst_path)
        cmd = '{} -i "{}" -q 0 -framerate {} "{}"'.format(self.ffmpeg, src_path, fps, dst_path)
        cmd = cmd.replace("/", "\\")
        if self.logger:
            self.logger.debug("output_path: {}".format(dst_path))
            self.logger.debug(cmd)
        print cmd
        subprocess.Popen(cmd, shell=True).wait()


    def execute(self):
        flg = True
        header = ""
        detail = ""

        camera = kc_model.to_object(self.data["camera"])
        if camera is None:
            header = "no camera exists: {}".format(self.data["camera"])
        else:
            d, f = os.path.split(self.data["movie_path"])
            f, ext = os.path.splitext(f)
            temp_directory1 = "{}/temp/src".format(d)
            temp_name = "{}_.png".format(f)
            temp_directory2 = "{}/temp/dst".format(d)

            if not os.path.exists(temp_directory1):
                os.makedirs(temp_directory1)
            if not os.path.exists(temp_directory2):
                os.makedirs(temp_directory2)                

            pymxs.runtime.viewport.setCamera(camera)
            pymxs.runtime.ForceCompleteRedraw()
            pymxs.runtime.CreatePreview(start=self.data["start"], 
                                        end=self.data["end"],
                                        fps=self.data["fps"], 
                                        filename="{}/{}".format(temp_directory1, temp_name),
                                        percentSize=self.piece_data["scale_percent"],
                                        rndLevel=pymxs.runtime.Name("flat"))

            for i, each in enumerate(os.listdir(temp_directory1)):
                src = "{}/{}".format(temp_directory1, each)
                if self.data["start"] == 0:
                    dst = "{}/{}".format(temp_directory2, each)
                else:
                    dst = "{}/{}_{:04d}.png".format(temp_directory2, f, i)
                try:
                    shutil.copy2(src, dst)
                except:
                    import traceback
                    print traceback.format_exc()
                    print "copy failed: {} > {}".format(src, dst)

            if os.path.exists(self.data["movie_path"]):
                try:
                    os.remove(self.data["movie_path"])
                except:
                    pass

            self.png_to_movie("{}/{}_%04d.png".format(temp_directory2, f), self.data["movie_path"], self.data["fps"])

            if os.path.exists(self.data["movie_path"]):
                header = "max scene preview successed"
                detail = "camera: {camera}\nstart: {start}\nend: {end}\nfps: {fps}\npath: {movie_path}".format(**self.data)
                # try:
                #     shutil.rmtree("{}/temp".format(d))
                # except:
                #     pass
            else:
                header = "max scene preview failed"
                detail = "camera: {camera}\nstart: {start}\nend: {end}\nfps: {fps}\npath: {movie_path}".format(**self.data)
            

        return flg, self.pass_data, header, detail

if __name__ == "__main__":

    piece_data = {"scale_percent": 50}
    data = {
            "shot_name": "s99c999", 
            "end": 60, 
            "render_scale": 0.5, 
            "camera": "cam_s99c999:Merge_Camera",
            "start": 40, 
            "movie_path": "X:/Project/_942_ZIZ/3D/s99/c999/movie_convert/max/ZIM_s99c999_MB.mov", 
            "fps": 24, 
            "path": "X:/Project/_942_ZIZ/3D/s99/c999/3D/master/ZIM_s99c999_anim.max"
        }

    x = RenderScene(piece_data=piece_data, data=data)
    x.execute()
