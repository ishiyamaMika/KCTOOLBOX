from pyfbsdk import *
from puzzle2.PzLog import PzLog

TASK_NAME = "remove_namespace"

def main(event={}, context={}):
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0
    renamed = []
    for root in FBSystem().Scene.RootModel.Children:
        m_list = FBModelList()
        FBGetSelectedModels(m_list, root, False, True)
        for m in m_list:
            renamed.append(u"{} -> {}".format(m.LongName, m.Name))
            m.LongName = m.Name
    
    logger.details.add_detail(u"\n".join(renamed))
    if len(renamed) > 0:
        logger.details.set_header(u"namespaceを削除しました")
    else:
        logger.details.set_header(u"namespaceは設定されていませんでした")

    return {"return_code": return_code}

if __name__ in ["__builtin__", "__main__", "builtins"]:
    data = {"": ""}
    main(event={"data": data})