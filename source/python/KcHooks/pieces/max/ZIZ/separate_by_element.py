import os
import sys
import time
import MaxPlus
import pymxs
import copy

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

import KcLibs.max.kc_file_io as kc_file_io
import KcLibs.max.kc_render as kc_render

from puzzle2.PzLog import PzLog

TASK_NAME = "separate_by_element"


def change_shell_state(type_):
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

def archive_file(path, logger):
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
        logger.debug("copied:\n{}\n{}".format(path, archive_path))
    except:
        logger.debug("copy failed:\n{}\n{}".format(path, archive_path))

def main(event={}, context={}):
    """
    pass_data: root_directory, element_names, render_setup
    piece_data: replace_ext, render_element_path
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    #with open("D:/test.json", "w") as f:
    #    import json
    #    json.dump({"data": data, "pass_data": data}, f)
    flg = True
    header = "split file"
    detail = ""
    path = data["path"]
    if "replace_ext" in data:
        path = path.replace(*data["replace_ext"])

    d, f = os.path.split(path)
    f, ext = os.path.splitext(f)
    path_ = d.replace("master", "rend")

    dic = {"col": {"type": "col", 
                    "elements": [], 
                    "output_path": "{}/{}_col/{}_col_.png".format(data["root_directory"], data["name"], data["name"]),
                    "name": "col.rps", 
                    "format": [24, False]},
            "tex": {"type": "tex", 
                    "output_path": "{}/{}_tex/{}_tex_.png".format(data["root_directory"], data["name"], data["name"]),
                    "elements": [],
                    "name": "tex_IDmask.rps", 
                    "format": [24, True]},
            "ID_mask": {"type": "ID_mask", 
                        "output_path": "{}/{}_IDMask/{}_IDmask_.png".format(data["root_directory"], data["name"], data["name"]),
                        "elements": [],
                        "format": [24, False],
                        "name": "tex_IDmask.rps"}
                        }
    
    if data.get("network_rendering", False):
        net_render = pymxs.runtime.netrender
        manager = net_render.GetManager()
        try:
            manager.connect(pymxs.runtime.Name("manual"), data["address"])
            logger.debug("connect backburner manager")
            logger.details.add_detail("connect: backburner manager")
        except:
            manager = False
            logger.debug("connection failed")
            logger.details.add_detail("connect failed: backburner manager")
    else:
        manager = False

    for each in data["element_names"]:
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
        if data["network_rendering"]:
            if not data["job_create"]:
                logger.details.add_detail("file & job create skip.")
                continue

        logger.debug("open:{}".format(path))

        if kc_file_io.file_open(path):
            render_element_path = data["render_element_path"]
            logger.details.add_detail("type: {}".format(k))
            if "name" in v:
                rps_path = "{}/{}".format(render_element_path, v["name"])
                if os.path.lexists(rps_path):
                    kc_render.rps_import(rps_path)
                    logger.details.add_detail("rps: {}".format(rps_path))
                else:
                    logger.details.add_detail("rps not exists: {}".format(rps_path))

            change_shell_state(k)
            kc_render.remove_render_elements(v["elements"])
            save_path = "{}/{}/{}_{}_00{}".format(path_, data["name"], f, k, ext)
            if not os.path.exists(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path))

            archive_file(save_path, logger)
            if "render_setup" in data:
                dic = copy.deepcopy(data["render_setup"])
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
                logger.details.add_detail(format_text)

            if "anti" in v:
                if v["anti"]:
                    anti_cmd = "renderers.production.AntiAliasing = true"
                else:
                    anti_cmd = "renderers.production.AntiAliasing = false"
                MaxPlus.Core.EvalMAXScript(anti_cmd)
            
            if data["network_rendering"]:
                if k == "sdw" and not data["sdw_create"]:
                    logger.details.add_detail("sdw file & job create skip.")
                    logger.details.add_detail("")
                    logger.details.add_detail("")
                    continue
            
            if k == "sdw":
                for geo in pymxs.runtime.Geometry:
                    if "GEO_body" in geo.name:
                        geo.primaryVisibility = False
                        logger.details.add_detail("set primaryVisibility: {}".format(geo.name))
                    else:
                        pymxs.runtime.hide(geo)
                        logger.details.add_detail("set hide: {}".format(geo.name))

                obj = pymxs.runtime.getNodeByName("sdw_Plane")
                if obj:
                    logger.details.add_detail("unhide: sdw_Plane")
                    pymxs.runtime.unhide(obj)

            if kc_file_io.file_save(save_path):
                logger.details.add_detail("saved: {}\n".format(save_path.replace("/", "\\")))

                logger.debug("saved: {}\n".format(save_path.replace("/", "\\")))

                if data["network_rendering"]:
                    logger.details.add_detail("-----job-----")
                    if manager and "name" in data:
                        job = manager.newjob()
                        job.name = "{}_{}_{}".format(data["name"], f, k)
                        job.renderCamera = data["camera"]
                        if k == "sdw":
                            job.suspended = data["sdw_suspended"]
                            logger.details.add_detail("{} suspended: {}".format(k, data["sdw_suspended"]))
                        else:
                            job.suspended = False
                            logger.details.add_detail("{} suspended: False".format(k))

                        status = job.submit()
                        logger.debug("status: {}".format(status))
                        logger.details.add_detail("job created. status: {}".format(status))
                    else:
                        logger.details.add_detail("manager is not exists: {}".format(data))
            else:
                logger.details.add_detail("save failed: {}\n".format(save_path.replace("/", "\\")))
                logger.debug("save failed: {}\n".format(save_path.replace("/", "\\")))
            
            logger.details.add_detail("")
            logger.details.add_detail("")
    logger.details.set_header(header)

    return {"return_code": return_code}


if __name__ == "__main__":
    import json
    path = "F:/works/keica/KcToolBox/source/python/KcHooks/pieces/max/ZIZ/test_data/separate_by_element.json"
    # path = "D:/test.json"
    js = json.load(open(path, "r"))
    piece_data = {"render_element_path": "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_Tool/rps"}
    js["data"].update(piece_data)
    kc_file_io.file_open(js["data"]["path"])

    main({"data": js["data"]})
