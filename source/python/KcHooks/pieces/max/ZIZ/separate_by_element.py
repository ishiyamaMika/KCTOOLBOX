import os
import sys
import time
import MaxPlus
import pymxs
import copy

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece
import KcLibs.max.kc_file_io as kc_file_io
import KcLibs.max.kc_render as kc_render
reload(kc_render)
_PIECE_NAME_ = "SeparateByElement"

class SeparateByElement(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(SeparateByElement, self).__init__(**args)
        self.name = _PIECE_NAME_
        self.details = []

    def change_shell_state(self, type_):
        if type_ == "col":
            key_shell = [0, 0] # [1, 1]
            col_shell = [0, 0] # [1, 1]

        elif type_ == "tex":
            key_shell = [0, 0] # [1, 1]
            col_shell = [1, 1] # [1, 1]

        elif type_ == "ID_mask":
            key_shell = [1, 1] # [0, 0]
            col_shell = [0, 0] # [1, 1]        

        elif type_ == "line":
            key_shell = [0, 0] # [1, 1]
            col_shell = [0, 0] # [1, 1]        

        else: # sdw
            key_shell = [0, 0] # [1, 1]
            col_shell = [0, 0] # [0, 0]

        key_materials = []
        for material in pymxs.runtime.sceneMaterials:
            if hasattr(material, "renderMtlIndex"):
                key_materials.append(material.name)
        
        for material in key_materials:
            cmd = """
                  root_value = 0
                  next_value = 0
                  Mats = for m in sceneMaterials where (matchPattern m.name pattern:"{}") collect m
                  for m in Mats do (try(
                    m.renderMtlIndex = {}
                    m.viewportMtlIndex = {}
                    m[1].renderMtlIndex = {}
                    m[1].viewportMtlIndex = {}
                    print(m.name)
                    )catch())
                 """.format(material,
                            key_shell[0],
                            key_shell[1],
                            col_shell[0],
                            col_shell[1])

            MaxPlus.Core.EvalMAXScript(cmd)
    
    def archive_file(self, path):
        if not os.path.lexists(path):
            return
        file_meta = time.localtime(os.stat(path).st_mtime)
        file_time = "{:04d}{:02d}{:02d}{:02d}{:02d}".format(file_meta[0], 
                                                            file_meta[1], 
                                                            file_meta[2],
                                                            file_meta[3], 
                                                            file_meta[4])
        d, f = os.path.split(path)
        archive_path = "{}/archives/{}_{}".format(d, file_time, f)
        if not os.path.exists(os.path.dirname(archive_path)):
            os.makedirs(os.path.dirname(archive_path))

        try:
            shutil.copy2(path, archive_path)
            if self.logger:
                self.logger.debug("copied:\n{}\n{}".format(path, archive_path))
        except:
            if self.logger:
                self.logger.debug("copy failed:\n{}\n{}".format(path, archive_path))

    def execute(self):
        #with open("D:/test.json", "w") as f:
        #    import json
        #    json.dump({"data": self.data, "pass_data": self.pass_data}, f)
        flg = True
        header = "split file"
        detail = ""
        path = self.data["path"]
        if "replace_ext" in self.piece_data:
            path = path.replace(*self.piece_data["replace_ext"])

        d, f = os.path.split(path)
        f, ext = os.path.splitext(f)
        path_ = d.replace("master", "rend")

        dic = {"col": {"type": "col", 
                       "elements": [], 
                       "output_path": "{}/{}_col/{}_col_.png".format(self.pass_data["root_directory"], self.data["name"], self.data["name"]),
                       "name": "col.rps", 
                       "format": [24, False]},
               "tex": {"type": "tex", 
                       "output_path": "{}/{}_tex/{}_tex_.png".format(self.pass_data["root_directory"], self.data["name"], self.data["name"]),
                       "elements": [],
                       "name": "tex_IDmask.rps", 
                       "format": [24, True]},
               "ID_mask": {"type": "ID_mask", 
                           "output_path": "{}/{}_IDMask/{}_IDmask_.png".format(self.pass_data["root_directory"], self.data["name"], self.data["name"]),
                           "elements": [],
                           "format": [24, False],
                           "name": "tex_IDmask.rps"}
                           }
        
        if self.data.get("network_rendering", False):
            net_render = pymxs.runtime.netrender
            manager = net_render.GetManager()
            try:
                manager.connect(pymxs.runtime.Name("manual"), self.data["address"])
                if self.logger:
                    self.logger.debug("connect backburner manager")
                    self.details.append("connect: backburner manager")
            except:
                manager = False
                if self.logger:
                    self.logger.debug("connection failed")
                    self.details.append("connect failed: backburner manager")
        else:
            manager = False

        for each in self.pass_data["element_names"]:
            if "_line" in each:
                dic.setdefault("line", {"ignore": "_line", "elements": []})["elements"].append(each)
                # dic["line"]["format"] = [24, False]
            elif "_sdw" in each:
                dic.setdefault("sdw", {"ignore": "sdw", "elements": []})["elements"].append(each)
                # dic["sdw"]["format"] = [24, True]
                dic["sdw"]["anti"] = True

        for k, v in dic.items():
            if not os.path.exists(path):
                continue
            if self.data["network_rendering"]:
                if not self.data["job_create"]:
                    self.details.append("file & job create skip.")
                    continue

            if kc_file_io.file_open(path):
                render_element_path = self.piece_data["render_element_path"]
                self.details.append("type: {}".format(k))
                if "name" in v:
                    rps_path = "{}/{}".format(render_element_path, v["name"])
                    if os.path.lexists(rps_path):
                        kc_render.rps_import(rps_path)
                        self.details.append("rps: {}".format(rps_path))
                    else:
                        self.details.append("rps not exists: {}".format(rps_path))

                self.change_shell_state(k)
                kc_render.remove_render_elements(v["elements"])
                save_path = "{}/{}/{}_{}_00{}".format(path_, self.data["name"], f, k, ext)
                if not os.path.exists(os.path.dirname(save_path)):
                    os.makedirs(os.path.dirname(save_path))

                self.archive_file(save_path)
                if "render_setup" in self.pass_data:
                    dic = copy.deepcopy(self.pass_data["render_setup"])
                    if "output_path" in v:
                        dic["options"]["output_path"] = v["output_path"]
                        if not os.path.exists(os.path.dirname(v["output_path"])):
                            os.makedirs(os.path.dirname(v["output_path"]))
                    kc_render.setup(dic["start"],
                                    dic["end"],
                                    dic["width"],
                                    dic["height"],
                                    **dic["options"])

                if "format" in v:
                    format_text = "renderSceneDialog.close()\n"
                    if v["format"][0] == 24:
                        format_text += "pngio.setType #true24\n"
                    if v["format"][1]:
                        format_text += "pngio.setAlpha true\n"
                    else:
                        format_text += "pngio.setAlpha false\n"
                    
                    format_text += "rendOutputFilename = rendOutputFilename\n"
                    format_text += "renderSceneDialog.update()"
                    MaxPlus.Core.EvalMAXScript("{}\nrenderSceneDialog.update()".format(format_text))
                    self.details.append(format_text)

                if "anti" in v:
                    if v["anti"]:
                        anti_cmd = "renderers.production.AntiAliasing = true"
                    else:
                        anti_cmd = "renderers.production.AntiAliasing = false"
                    MaxPlus.Core.EvalMAXScript(anti_cmd)
                
                if self.data["network_rendering"]:
                    if k == "sdw" and not self.data["sdw_create"]:
                        self.details.append("sdw file & job create skip.")
                        self.details.append("")
                        self.details.append("")
                        continue

                if kc_file_io.file_save(save_path):
                    self.details.append("saved: {}\n".format(save_path.replace("/", "\\")))
                    if self.logger:
                        self.logger.debug("saved: {}\n".format(save_path.replace("/", "\\")))

                    if self.data["network_rendering"]:
                        self.details.append("-----job-----")
                        if manager and "name" in self.data:
                            job = manager.newjob()
                            job.name = "{}_{}_{}".format(self.data["name"], f, k)
                            job.renderCamera = self.data["camera"]
                            if k == "sdw":
                                job.suspended = self.data["sdw_suspended"]
                                self.details.append("{} suspended: {}".format(k, self.data["sdw_suspended"]))
                            else:
                                job.suspended = False
                                self.details.append("{} suspended: False".format(k))

                            status = job.submit()
                            if self.logger:
                                self.logger.debug("status: {}".format(status))
                            self.details.append("job created. status: {}".format(status))
                        else:
                            self.details.append("manager is not exists: {}".format(data))
                else:
                    self.details.append("save failed: {}\n".format(save_path.replace("/", "\\")))
                    if self.logger:
                        self.logger.debug("save failed: {}\n".format(save_path.replace("/", "\\")))
                
                self.details.append("")
                self.details.append("")

        return flg, self.pass_data, header, u"\n".join(self.details)

if __name__ == "__main__":
    import json
    path = "F:/works/keica/KcToolBox/source/python/KcHooks/pieces/max/ZIZ/test_data/separate_by_element.json"
    # path = "D:/test.json"
    js = json.load(open(path, "r"))
    piece_data = {"render_element_path": "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_Tool/rps"}

    kc_file_io.file_open(js["data"]["path"])
    x = SeparateByElement(piece_data=piece_data, data=js["data"], pass_data=js["pass_data"])
    print(x.execute()[3])