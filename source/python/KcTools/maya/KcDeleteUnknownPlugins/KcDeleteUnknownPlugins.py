import maya.cmds as cmds

try:
    unknown = cmds.unknownPlugin(q=True, list=True) or []
except:
    unknown = []

#cmds.delete(cmds.ls(type="unknown"))
for plugin in unknown:
    try:
        cmds.unknownPlugin(plugin, remove=True)
        print "removed: ", plugin
    except:
        print "failed:", plugin

print "done"
