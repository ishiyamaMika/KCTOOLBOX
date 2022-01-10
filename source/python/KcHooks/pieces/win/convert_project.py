import os
import sys

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece

from KcLibs.core.KcProject import KcProject
_PIECE_NAME_ = "ConvertProject"

class ConvertProject(Piece):
    def __init__(self, **args):
        super(ConvertProject, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        if "project_info" in self.pass_data:
            project = KcProject()
            project.set(self.pass_data["project_info"]["name"], 
                        self.pass_data["project_info"]["variation"])
            
            self.pass_data["project"] = project
            del self.pass_data["project_info"]
            self.logger.debug("cast project object")

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    piece_data = {"include_model": True}
    data = {"namespace": "cam_s01c006A", "start": 10, "stop": 30, "fps": 8}

    x = ConvertProject(piece_data=piece_data, data=data)
    x.execute()

    print x.pass_data
