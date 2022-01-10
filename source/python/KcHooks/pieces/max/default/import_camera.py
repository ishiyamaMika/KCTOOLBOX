import os
import sys
import json
import pprint

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.max.kc_file_io as kc_file_io
import KcLibs.max.kc_model as kc_model

reload(kc_file_io)
_PIECE_NAME_ = "ImportCamera"

class ImportCamera(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(ImportCamera, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        # kc_file_io.file_open(self.data["asset_path"])

        nodes = kc_model.get_nodes()
        for node in nodes:
            if node.name.startswith("cam_s00c000:"):
                node.name = node.name.replace("cam_s00c000:", "{}:".format(self.data["namespace"]))
                detail += u"renamed: {}".format(node.name)

        if kc_file_io.file_import(self.data["import_path"]):
            header = u"import successed: {}".format(self.data["namespace"])
        else:
            header = u"import failed: {}".format(self.data["namespace"])

        return flg, self.pass_data, header, detail

if __name__ == "__main__":
    piece_data = {"filter": {"category": "camera"}}
    data = {"asset_path": "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/camera/cam_t08_03.max", 
            "import_path": "X:/Project/_942_ZIZ/3D/s99/c999/3D/import/ZIM_s99c999_cam_s99c999.fbx",
            "namespace": "cam_s99c999"}
    x = ImportCamera(piece_data=piece_data, data=data)
    x.execute()
