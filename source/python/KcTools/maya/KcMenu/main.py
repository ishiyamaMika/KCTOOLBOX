# -*- coding: utf8 -*-

import os
import sys
import copy

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)
mod = "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)
import KcLibs.core.kc_env as kc_env
import puzzle2.pz_config as pz_config

import maya.cmds as cmds
from functools import partial

def execute(p, *args):
    print(p, "execute")
    if p.endswith(".py"):
        execfile(p)


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

    root = cmds.menu(l="keica", p="MayaWindow")
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
        menu = cmds.menuItem(l=l, p=menus[menu_root], sm=True)
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
                    sub_menu = cmds.menuItem(l=d_, p=menus[parent], sm=True)
                    menus[sub_menu_path] = sub_menu

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
                cmds.menuItem(l=os.path.splitext(f)[0], icb=True, p=p_menu, c=partial(execute, path))


if __name__ == "__main__":
    create_menu("{}/config/apps/maya/menu".format(kc_env.get_root_directory()))



