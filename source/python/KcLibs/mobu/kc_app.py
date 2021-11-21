# -*-coding: utf8 -*-

import os
import sys

from pyfbsdk import ShowTool, FBAttachType, FBWidgetHolder, FBTool, FBAddRegionParam
from pyfbsdk_additions import FBAddTool, FBToolList, FBDestroyToolByName

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])

if mod not in sys.path:
    sys.path.append(mod)

os.environ["QT_PREFERRED_BINDING"] = os.pathsep.join(["PySide", "PySide2"])

import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()

from Qt import QtWidgets

try:
    from PySide import shiboken
except:
    try:
        from PySide2 import shiboken
    except:
        import shiboken2 as shiboken


class NativeWidgetHolder(FBWidgetHolder):
    def WidgetCreate(self, parent):
        self.native_widget = self.tool(parent=shiboken.wrapInstance(parent, QtWidgets.QWidget))
        print type(self.native_widget.parent())
        self.native_widget.set_ui()
        return shiboken.getCppPointer(self.native_widget)[0]


class NativeWidgetTool(FBTool):
    def BuildLayout(self):
        x = FBAddRegionParam(0, FBAttachType.kFBAttachLeft, "")

        y = FBAddRegionParam(0, FBAttachType.kFBAttachTop, "")
        w = FBAddRegionParam(0, FBAttachType.kFBAttachRight, "")
        h = FBAddRegionParam(0, FBAttachType.kFBAttachBottom, "")
        self.AddRegion("main", "main", x, y, w, h)
        self.SetControl("main", self.holder)

    def __init__(self, name):
        FBTool.__init__(self, name)

    def setup(self, tool, x=600, y=600):
        self.holder = NativeWidgetHolder()
        self.holder.tool = tool
        self.BuildLayout()
        self.StartSizeX = x
        self.StartSizeY = y


def start_app(tool_instance, **kwargs):
    rem = []

    for tool in FBToolList:
        if tool_instance.NAME in tool:
            rem.append(tool)

    for r in rem:
        FBDestroyToolByName(r)

    tool = NativeWidgetTool(tool_instance.NAME)
    tool.setup(tool_instance, kwargs.get("x", 600), kwargs.get("y", 600))
    FBAddTool(tool)
    ShowTool(tool)


def destroy(name):
    FBDestroyToolByName(name)


    