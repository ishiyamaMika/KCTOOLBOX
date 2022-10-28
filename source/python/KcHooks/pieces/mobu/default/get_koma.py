#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()

from puzzle.Piece import Piece
import KcLibs.mobu.kc_model as kc_model
_PIECE_NAME_ = "GetKoma"

class GetKoma(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(GetKoma, self).__init__(**args)
        self.name = _PIECE_NAME_

    def get_frame(self, fb_time):
        if FBSystem().Version >= 13000.0:
            return fb_time.GetFrame()
        else:
            return fb_time.GetFrame(True)   

    def get_all_keys(self, model):
        def _get_each_keys(anim_node, i):
            if anim_node is None:
                return [], {}
            all_keys = {}
            temp_key = None
            modified_list = []
            for ii, k in enumerate(anim_node.Keys):
                frame = self.get_frame(k.Time)
                # print(frame, "----", self.data["start"], self.data["end"])
                keyframe = {}

                if frame < self.data["start"]:
                    keyframe["frame"] = k.Time.GetFrame()
                    keyframe["value"] = k.Value
                    temp_key = keyframe
                    continue
                elif frame > self.data["end"]:
                    continue

                all_keys.setdefault(frame, {})
                # keyframe["type"] = "{}{}".format(trs[0], ["x", "y", "z"][i])
                # keyframe["axis"] = i
                keyframe["frame"] = k.Time.GetFrame()
                # keyframe["frame"] = get_frame(k.Time)
                keyframe["value"] = k.Value
                if "e-" in str(keyframe):
                    keyframe["value"] = 0
                keyframe["value"] = round(keyframe["value"], 4)
                if ii == 0:
                    keyframe["changed"] = True
                else:
                    keyframe["changed"] = temp_key["value"] != keyframe["value"]

                if keyframe["changed"]:
                    modified_list.append(frame)

                all_keys[frame][i] = keyframe
                temp_key = keyframe

            return modified_list, all_keys            

        if isinstance(model, (list, FBModelList)):
            results = []
            for m in model:
                results.extend(self.get_all_keys(m))

            return results

        else:
            all_keys = {}
            modified = []
            for each in model.PropertyList:
                if each.IsAnimatable() and each.IsAnimated():
                    if not each.GetAnimationNode():
                        continue
                
                    if each.GetAnimationNode().FCurve is not None:
                        # print(each.Name)
                        all_keys[each.Name], modified_list_ = _get_each_keys(each.GetAnimationNode().FCurve, each.Name)
                        modified.extend(modified_list_)                    
                        # print("*****", modified_list_)

                    elif len(each.GetAnimationNode().Nodes) > 0:
                        for i in range(len(each.GetAnimationNode().Nodes)):
                            anim_node = each.GetAnimationNode().Nodes[i].FCurve
                            name = "{}_{}".format(each.Name, i)
                            all_keys.setdefault(name, [])
                            all_keys[name], modified_list_ = _get_each_keys(anim_node, name)
                      
                        modified.extend(modified_list_)
            mix = []
            for ls in all_keys.values():
                if len(ls) == 0:
                    continue

                mix.extend(ls)
            
            if len(mix) in [0, 1]:
                return []

            """
            TRSすべてをマージして移動したフレームの取得
            """
            x = list(set(mix))
            x.sort()
            if x[0] > self.data["start"]:
                x.insert(0, self.data["start"])

            return x

    def execute(self):
        flg = True
        header = ""
        detail = ""
        def _ignore(model_name):
            ignores = ["_ctrlSpace", "_jtSpace"]
            for ignore in ignores:
                if ignore in model_name:
                    return False
            return True

        kc_model.unselected_all()
        flg = True

        info, models = self.pass_data["project"].sticky.read(self.data["config"]["export"])

        model_names = ["{}:{}".format(self.data["namespace"], l["name"]) for l in models if _ignore(l)]

        models = kc_model.to_object(model_names)
        keys = self.get_all_keys(models)
        keys = list(set(keys))
        keys.sort()
        d, f = os.path.split(self.data["path"])
        f, ext = os.path.splitext(f)

        koma_path = "{}/{}_koma.json".format(d, f)

        if not os.path.exists(os.path.dirname(koma_path)):
            os.makedirs(os.path.dirname(koma_path))

        kc_env.save_config(koma_path, "KcSceneManager", "koma data", {"modified": keys})

        header = u"コマファイルをエクスポートしました: {}".format(self.data["namespace"])
        detail = u"path: \n{}\n\n".format(koma_path)
        detail += u"start: {}\n".format(self.data["start"])
        detail += u"end  : {}\n".format(self.data["end"])
        detail += u"fps  : {}\n".format(FBPlayerControl().GetTransportFpsValue())
        detail += u", ".join([str(l) for l in keys]) + "\n\n"
        detail += u"\n".join(model_names)
        detail += u"\n"

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    from KcLibs.core.KcProject import *

    kc_project = KcProject()
    kc_project.set("ZIM", "default")

    pass_data = {"project": kc_project}
    in_frame = FBPlayerControl().ZoomWindowStart
    out_frame= FBPlayerControl().ZoomWindowStop    
    start = int(FBTime.GetTimeString(in_frame).replace("*", ""))
    end = int(FBTime.GetTimeString(out_frame).replace("*", ""))

    data = {u'category': u'CH',
           'config': {'export': False, 'plot': False},
           'cut': u'001',
           'end': end,
           'mobu_edit_export_path': u'X:/Project/_942_ZIZ/3D/s01/c001/master/export/ZIM_s01c001_anim_CH_tsukikoQuad.fbx',
            u'config': {'export': "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/usaoSS/MB/config/CH_usaoSS_export.json",
                        'plot': "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/usaoSS/MB/config/CH_usaoSS_plot.json"},
           'mobu_sotai_path': False,
           u'namespace': u'CH_tsukikoQuad',
           'scene': u'01',
           u'selection': True,
           'start': start,
           u'take': 2.0,
           u"path": "E:/works/client/keica/data/junkscript/test.json",
           u'true_namespace': u'CH_usaoSS',
           u'type': u'both',
           u'update_at': u'2021/11/18 01:17:16',
           u'update_by': u'amek'}



    piece_data = {}

    x = GetKoma(piece_data=piece_data, data=data, pass_data=pass_data)
    # x.execute()
    m_list = FBModelList()
    FBGetSelectedModels(m_list)
    keys = list(set(x.get_all_keys(m_list)))
    keys.sort()
    print(keys)