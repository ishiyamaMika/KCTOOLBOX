import MaxPlus
import pymxs

def get_nodes():
    return pymxs.runtime.objects

def get_root_nodes():
    root_scene = pymxs.runtime.rootScene
    return list(root_scene[pymxs.runtime.Name("world")].object.Children)

def to_object(name):
	if isinstance(name, list):
		ls = []
		for n in name:
			obj = to_object(n)
			if obj is not None:
				ls.append(obj)
	else:
		return pymxs.runtime.getNodeByName(name)

if __name__ == "__main__":
    root_nodes = get_root_nodes()
    print
    print "-----------------------------------------"
    
    print to_object("HOGE")
    camera = to_object("cam_s99c999:Merge_Camera")

    pymxs.runtime.viewport.setCamera(camera)