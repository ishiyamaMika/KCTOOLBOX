#-*-coding: utf-8 -*-

import os
import subprocess


def open(path, inside=False):
    def _change_for_cmd(path):
        path = path.replace("/", "\\")
        try:
            path = path.replace("/", "\\")
            path = path.replace(u"&", u"^&")
            path = path.replace(u"(", u"^(")
            path = path.replace(u")", u"^)")
            path = path.replace(u"%", u"%%")        
        except:
            pass

        return path

    explorer = "C:\\Windows\\explorer.exe"
    try:
        path = os.path.normpath(path)
    except:
        path = path.replace("/", "\\")
    if path[-1] == "\\":
        path = path[:-1]
    if path.startswith('https://') or path.startswith('http://'):
        cmd = "rundll32 url.dll,FileProtocolHandler %s" % path
        os.popen("rundll32 url.dll,FileProtocolHandler %s" % path)

    elif os.path.isdir(path):
        path = _change_for_cmd(path)
        if inside:
            cmd = "%s /e,%s" % (explorer, path)
          #  os.popen("explorer /e," + path+"\\")
        else:
            cmd = "%s /select,%s\\" % (explorer, path)
         #   os.popen("explorer /select," + path+"\\")
    else:
        path = _change_for_cmd(path)
        cmd = "%s /select,%s" % (explorer, path)
        #os.popen("explorer /select," + path)
    #os.popen(cmd)
    print(cmd)
    subprocess.Popen(cmd, shell=True)

