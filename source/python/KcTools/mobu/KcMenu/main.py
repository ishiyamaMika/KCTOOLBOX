# -*- coding: utf8 -*-

import os
import sys
import copy
import random

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)
mod = "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)
import KcLibs.core.kc_env as kc_env
import puzzle.pz_config as pz_config


from pyfbsdk import FBMenuManager, FBApplication, FBGenericMenu, FBSystem
_MENU_DIC_ = {}

def generate_id():
    inc = random.randint(0, 2000)
    while inc in _MENU_DIC_.keys():
        inc += 1
    return inc


def eventMenu(control, event):
    print event.Name
    print event.Id
    print _MENU_DIC_
    if event.Id not in _MENU_DIC_:  
        return
    script = _MENU_DIC_[event.Id]
    d, f = os.path.split(script)
    f, ext = os.path.splitext(f)
    if ext == ".py":
        FBApplication().ExecuteScript(script)

def create_menu(menu_root):
    def _get_yml_config(directory):
        path = u"{}/config.yml".format(directory)
        if os.path.exists(path):
            info, data = pz_config.read(path)
        else:
            data = {}
        return data

    def _sort(config, ls):
        order = config.get("order", [])
        for o in order[::-1]:
            if o not in ls:
                order.remove(o)

        for each in order:
            if each in ls:
                ls.remove(each)
        return order + ls

    menu_manager = FBMenuManager()
    # if menu_manager.GetMenu("keica") is not None:
    #    return

    menu_manager.InsertBefore(None, "Help", "keica")
    root = menu_manager.GetMenu("keica")

    ls = os.listdir(menu_root)
    menus = {menu_root: root}
    config = _get_yml_config(menu_root)
    ls = _sort(config, ls)
    for l in ls:
        directory = "{}/{}".format(menu_root.replace("\\", "/"), l)
        if l.endswith(".yml"):
            continue
        if len(os.listdir(directory)) == 0:
            continue

        menu = FBGenericMenu()
        root.InsertLast(l, 200, menu)
        menu.OnMenuActivate.Add(eventMenu)
        menus[directory] = menu

        config = _get_yml_config(directory)
        for d, dl, fl in os.walk(directory):
            d = d.replace("\\", "/")

            dl_ = _sort(config, copy.deepcopy(dl))
            parent = d
            for d_ in dl_:
                sub_menu_path = "{}/{}".format(d, d_)
                if not os.path.exists(sub_menu_path):
                    continue
                if not os.path.isdir(sub_menu_path):
                    continue
                if len(os.listdir(sub_menu_path)) == 0:
                    continue

                if sub_menu_path not in menus:
                    sub_menu = FBGenericMenu()
                    menus[parent].InsertLast(d_, 200, sub_menu)
                    menus[sub_menu_path] = sub_menu
                    sub_menu.OnMenuActivate.Add(eventMenu)

            p_menu = menus[d]
            config = _get_yml_config(d)
            fl_ = _sort(config, copy.deepcopy(fl))
            for f in fl_:
                f_path = "{}/{}".format(d, f)
                if os.path.isdir(f_path):
                    continue
                if f.endswith(".yml"):
                    continue
                path = u"{}/{}".format(d, f)
                inc = generate_id()
                p_menu.InsertLast(os.path.splitext(f)[0], inc)
                _MENU_DIC_[inc] = f_path


if __name__ == "__builtin__":
    create_menu("{}/config/apps/mobu/menu".format(kc_env.get_root_directory()))



