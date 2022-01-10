#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

from puzzle.Piece import Piece
import KcLibs.core.kc_env as kc_env
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
        def _get_trs_key(model, trs="Translation"):
            all_keys = {}

            trs_object = getattr(model, trs)
            if not trs_object.GetAnimationNode():
                return {}
            for i in range(3):
                each_keys = []
                anim_node = trs_object.GetAnimationNode().Nodes[i]
                if anim_node is None:
                    #all_keys.append(each_keys)
                    continue

                temp_key = None
                for ii, k in enumerate(anim_node.FCurve.Keys):
                    frame = self.get_frame(k.Time)
                    all_keys.setdefault(frame, [None, None, None])
                    keyframe = {}
                    keyframe["type"] = "{}{}".format(trs[0], ["x", "y", "z"][i])
                    keyframe["axis"] = i
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

                    all_keys[frame][i] = keyframe
                    temp_key = keyframe
            return all_keys

        if isinstance(model, (list, FBModelList)):
            all_ = {}
            for m in model:
                dic = self.get_all_keys(m)
                if dic is not None:
                    all_[m.LongName] = dic[m.LongName]
            return all_
        else:
            all_keys = {}
            for trs in ["Translation", "Rotation", "Scaling"]:
                all_keys[trs] = _get_trs_key(model, trs)

            a = all_keys["Translation"].keys()
            b = all_keys["Rotation"].keys()
            c = all_keys["Scaling"].keys()
            mix = a + b + c
            mix = list(set(mix))
            mix.sort()
            if len(mix) in [0, 1]:
                return None
                # return {model.LongName: {"min": None, "max": None, "list": []}}
            """
            print "type:", type(a), type(b), type(c)
            print "T:", a
            print "R:", b
            print "S:", c
            print "A:", mix
            print "len:", len(mix), len(mix)
            """

            """
            TRSすべてをマージして移動したフレームの取得
            """
            min_ = mix[0]
            max_ = mix[-1]
            keyframe_set = {}
            keyframe_set["min"] = min_
            keyframe_set["max"] = max_
            keyframe_set["list"] = []
            for i in range(min_, max_+1):
                keys = {}
                for trs in ["Translation", "Rotation", "Scaling"]:
                    if i in all_keys[trs]:
                        keys[trs] = all_keys[trs][i]
                    else:
                        continue
                keyframe_set["list"].append(keys)

            return {model.LongName: keyframe_set}

    def execute(self):
        flg = True
        header = ""
        detail = ""


        kc_model.unselected_all()
        flg = True

        info, models = self.pass_data["project"].sticky.read(self.data["config"]["export"])

        model_names = ["{}:{}".format(self.data["namespace"], l["name"]) for l in models]

        models = kc_model.to_object(model_names)
        keys = self.get_all_keys(models)

        d, f = os.path.split(self.data["path"])
        f, ext = os.path.splitext(f)

        koma_path = "{}/{}_koma.json".format(d, f)

        if not os.path.exists(os.path.dirname(koma_path)):
            os.makedirs(os.path.dirname(koma_path))

        kc_env.save_config(koma_path, "KcSceneManager", "koma data", {"modified": keys})

        header = u"コマファイルをエクスポートしました: {}".format(self.data["namespace"])
        detail = u"path: \n{}".format(koma_path)


        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":
    from KcLibs.core.KcProject import *

    kc_project = KcProject()
    kc_project.set("ZIM", "default")

    pass_data = {"project": kc_project}
    data = {u'category': u'CH',
           'config': {'export': False, 'plot': False},
           'cut': u'001',
           'end': 0,
           'mobu_edit_export_path': u'X:/Project/_942_ZIZ/3D/s01/c001/master/export/ZIM_s01c001_anim_CH_tsukikoQuad.fbx',
            u'config': {'export': "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/tsukikoQuad/MB/config/CH_tsukikoQuad_export.json",
                            'plot': "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/tsukikoQuad/MB/config/CH_tsukikoQuad_plot.json"},
           'mobu_sotai_path': False,
           u'namespace': u'CH_tsukikoQuad',
           'scene': u'01',
           u'selection': True,
           'start': 0,
           u'take': 2.0,
           u"path": "E:/works/client/keica/data/junkscript/test.json",
           u'true_namespace': u'CH_tsukikoQuad',
           u'type': u'both',
           u'update_at': u'2021/11/18 01:17:16',
           u'update_by': u'amek'}

    piece_data = {}

    x = GetKoma(piece_data=piece_data, data=data, pass_data=pass_data)
    x.execute()

    print x.pass_data
