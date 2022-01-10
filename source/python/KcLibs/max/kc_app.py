import os
import sys
import MaxPlus

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])

if mod not in sys.path:
    sys.path.append(mod)

os.environ["QT_PREFERRED_BINDING"] = os.pathsep.join(["PySide", "PySide2"])
from pyside2uic import compileUi
import KcLibs.core.kc_env as kc_env

# from KcLibs.win.kc_qt import QtWidgets, QtCore, QtGui
# kc_env.append_sys_paths()

class _GCProtector(object):
    widgets = []


from pyside2uic import compileUi
def compile_ui(ui_path):
    to_py_file = ui_path.replace(".ui", ".py")
    with open(to_py_file, "w") as f:
        compileUi(ui_path, f, False, 4, False)

    return to_py_file

def start_app(tool_instance, **kwargs):
    main = tool_instance(MaxPlus.GetQMaxMainWindow())
    main.ct_tool = main.NAME
    main.set_ui()
    _GCProtector.widgets.append(main)
    main.show()

if __name__ == "__main__":
    path = "F:/works/keica/KcToolBox/source/python/KcTools/multi/KcSceneManager/form/ui/main.ui"
    print "------------->", compile_ui(path)