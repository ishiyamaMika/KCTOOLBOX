
function get_compostion(comp_name){
    for (var i=1; i < app.project.items.length; i++){//1
        var item = app.project.items[i];
        if (item.typeName=="コンポジション" && item.name == comp_name){//2
            return item;
            }//2
        }//1
    return false
}

function create_composition(comp_name, folder, width, height, duration, parent){//0
    //alert("---------------------------")
    //alert(comp_name)
    //alert(folder)
    //alert(width)
    //alert(height)
    //alert(duration)
    //alert(parent)

    var composition = get_compostion(comp_name)
    if (composition == false){//1
        var composition = app.project.items.addComp(comp_name, width, height, 1, duration, 24.0);
        if(folder){//2
            composition.parentFolder = folder;
        }//2
        if(parent){
            var parent_comp = get_compostion(parent)
            if(parent_comp){
                //alert(parent)
                //alert(composition)
                parent_comp.layers.add(composition)
            }
        }
    }//1 
    return composition
    }//0

function get_folder(name, parent){//0
    var folder = false;
    for (var i=1; i < app.project.items.length; i++){//1
        item = app.project.items[i];
        //alert("------------------------------------")
        //alert(item.typeName);
        //alert(item.name + "-xx-" + name);
        if(item.typeName == "フォルダー"){//2
            if(item.name == name){//3
            return item
            }//3
        }//2
    }//1

    var folder = app.project.items.addFolder(name);
    if (parent != false){//1
        folder.parentFolder = parent;
        }//1
    return folder
    }//0

function to_dict(path){//0
    x = new File(path);
    x.open("r");
    fs = x.read().split("\n");
    var dic = {}
    for(var ii=0; ii < fs.length; ii++){//1
        fs_s = fs[ii].split("=");
        if(fs_s[0] == "order"){//2
            dic[fs_s[0]] = fs_s[1].split(",");
        }else if(fs_s[0][0] == "@"){
            dic[fs_s[0]] = fs_s[1].split(",");
        }else if(fs_s[0] == "timesheet"){
            dic[fs_s[0]] = fs_s[1].split(",");
        }else if(fs_s[0] == "assets"){
            dic[fs_s[0]] = fs_s[1].split(",");            
        }else{
            dic[fs_s[0]] = fs_s[1];
            }//2
        }//1
    return dic
    }//0

function get_item(name){//1
    for(var i=1; i<=app.project.items.length; i++){//2
        var item = app.project.item(i);
        var current_name = item.name;
        if (item.typeName == "フッテージ" && item.name == name){//3
            return app.project.item(i);
        }//3
        //if(current_name == name){
        //    return app.project.item(i);
        //} 
    }//2
    return false;
}//1

function import_file(name, path, sequence, parent, folder, framerate){
    //alert(1);
    var item_ = get_item(name);
    if (item_){
        return item_
    }

    var i_o = new ImportOptions(File(path));
    //alert(2);    
    if (i_o.canImportAs(ImportAsType.FOOTAGE));
    i_o.importAs = ImportAsType.FOOTAGE;
    i_o.sequence = sequence;
    i_o.forceAlphabetical = true;
    tiffseq = app.project.importFile(i_o);
    if(folder){
        folder = get_folder(layer.folder, parent);
        tiffseq.parentFolder = folder;
    }else{
        tiffseq.parentFolder = parent;
    }
    if (framerate != -1){
        //alert(tiffseq);
        //alert(tiffseq.mainSource);
        //alert(tiffseq.mainSource.conformFrameRate);
        tiffseq.mainSource.conformFrameRate = framerate;
    }

    return get_item(name)
}

function set_mode(layer_item_, blending_mode, mat_type){
    if(blending_mode == "add"){
        layer_item_.blendingMode = BlendingMode.ADD;
    }else if(blending_mode == "alpha_add"){
        layer_item_.blendingMode = BlendingMode.ALPHA_ADD;
    }else if(blending_mode == "classic_color_burn"){
        layer_item_.blendingMode = BlendingMode.CLASSIC_COLOR_BURN;
    }else if(blending_mode == "classic_color_dodge"){
        layer_item_.blendingMode = BlendingMode.CLASSIC_COLOR_DODGE;
    }else if(blending_mode == "classic_difference"){
        layer_item_.blendingMode = BlendingMode.CLASSIC_DIFFERENCE;
    }else if(blending_mode == "color"){
        layer_item_.blendingMode = BlendingMode.COLOR;
    }else if(blending_mode == "color_burn"){
        layer_item_.blendingMode = BlendingMode.COLOR_BURN;
    }else if(blending_mode == "dancing_dissolve"){
        layer_item_.blendingMode = BlendingMode.DANCING_DISSOLVE;
    }else if(blending_mode == "darken"){
        layer_item_.blendingMode = BlendingMode.DARKEN;
    }else if(blending_mode == "darker_color"){
        layer_item_.blendingMode = BlendingMode.DARKER_COLOR;
    }else if(blending_mode == "difference"){
        layer_item_.blendingMode = BlendingMode.DIFFERENCE;
    }else if(blending_mode == "dissolve"){
        layer_item_.blendingMode = BlendingMode.DISSOLVE;
    }else if(blending_mode == "exclusion"){
        layer_item_.blendingMode = BlendingMode.EXCLUSION;
    }else if(blending_mode == "hard_light"){
        layer_item_.blendingMode = BlendingMode.HARD_LIGHT;
    }else if(blending_mode == "hard_mix"){
        layer_item_.blendingMode = BlendingMode.HARD_MIX;
    }else if(blending_mode == "hue"){
        layer_item_.blendingMode = BlendingMode.HUE;
    }else if(blending_mode == "lighten"){
        layer_item_.blendingMode = BlendingMode.LIGHTEN;
    }else if(blending_mode == "lighter_color"){
        layer_item_.blendingMode = BlendingMode.LIGHTER_COLOR;
    }else if(blending_mode == "linear_burn"){
        layer_item_.blendingMode = BlendingMode.LINEAR_BURN;
    }else if(blending_mode == "linear_dodge"){
        layer_item_.blendingMode = BlendingMode.LINEAR_DODGE;
    }else if(blending_mode == "linear_light"){
        layer_item_.blendingMode = BlendingMode.LINEAR_LIGHT;
    }else if(blending_mode == "luminescent_premul"){
        layer_item_.blendingMode = BlendingMode.LUMINESCENT_PREMUL;
    }else if(blending_mode == "luminosity"){
        layer_item_.blendingMode = BlendingMode.LUMINOSITY;
    }else if(blending_mode == "multiply"){
        layer_item_.blendingMode = BlendingMode.MULTIPLY;
    }else if(blending_mode == "normal"){
        layer_item_.blendingMode = BlendingMode.NORMAL;
    }else if(blending_mode == "overlay"){
        layer_item_.blendingMode = BlendingMode.OVERLAY;
    }else if(blending_mode == "pin_light"){
        layer_item_.blendingMode = BlendingMode.PIN_LIGHT;
    }else if(blending_mode == "saturation"){
        layer_item_.blendingMode = BlendingMode.SATURATION;
    }else if(blending_mode == "screen"){
        layer_item_.blendingMode = BlendingMode.SCREEN;
    }else if(blending_mode == "sulhouete_alpha"){
        layer_item_.blendingMode = BlendingMode.SILHOUETE_ALPHA;
    }else if(blending_mode == "sulhouette_luma"){
        layer_item_.blendingMode = BlendingMode.SILHOUETTE_LUMA;
    }else if(blending_mode == "soft_light"){
        layer_item_.blendingMode = BlendingMode.SOFT_LIGHT;
    }else if(blending_mode == "stencil_alpha"){
        layer_item_.blendingMode = BlendingMode.STENCIL_ALPHA;
    }else if(blending_mode == "stencil_luma"){
        layer_item_.blendingMode = BlendingMode.STENCIL_LUMA;
    }else if(blending_mode == "vivid_light"){
        layer_item_.blendingMode = BlendingMode.VIVID_LIGHT;
    }

    if(mat_type == "alpha"){
        layer_item_.trackMatteType = TrackMatteType.ALPHA;
    }else if(mat_type == "alpha_inverted"){
        layer_item_.trackMatteType = TrackMatteType.ALPHA_INVERTED;
    }else if(mat_type == "luma"){
        layer_item_.trackMatteType = TrackMatteType.LUMA;
    }else if(mat_type == "luma_inverted"){
        layer_item_.trackMatteType = TrackMatteType.LUMA_INVERTED;
    }
}

function override_default(data1, data2, name){
    if (data2[name]){
        return data2[name];
    }else{
        return data1[name];
    }
}

function set_effects(layer_item, effects){//0
    for (var iii=0; iii < effects.length; iii++){//1
        var effect = effects[iii];
        //alert(effect.name);
        if (!layer_item.Effects.canAddProperty(effect.name)){//2
            //alert("no effect name property");
            continue
        }//2

        var fx = layer_item.Effects.addProperty(effect.name);
        if (!effect.properties){//2
            //alert("no effect property");
            continue
        }//2

        for (var iiii=0; iiii < effect.properties.length; iiii++){//2
            property_ = effect.properties[iiii];
            fx.property(property_.name).setValue(property_.value);
        }//2
    }//1
}//0

app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);

//var base_path = "F:\\works\\keica\\data\\comp\\config\\AoiHigh_.json"
//var base_path = "F:\\works\\keica\\data\\comp\\test_export.json"
var base_path = $.getenv("__AUTOCOMP_DATA_PATH__")
var base_file = new File(base_path);
base_file.open("r");
fs = base_file.read()

var result = eval("(" + fs + ")");
for (var i=0; i < result.compositions.length; i++){//1
    var composition = result.compositions[i];
    var folder = get_folder(composition.info.folder, false);
    //alert(composition);
    var comp = create_composition(composition.info.name, folder, composition.info.width, composition.info.height, composition.info.duration, composition.info.parent);
    if(!composition.layers){
        continue
    }
    for (var ii=0; ii < composition.layers.length; ii ++){//2
        layer = composition.layers[ii];
        var layer_item = false;
        var temp_folder = folder
        if(layer.path){//3
            import_file(layer.name, layer.path, true, folder, layer.folder, 24);
            var item = get_item(layer.name);
            layer_item = comp.layers.add(item);
            }//3
        if(layer.primitive){//3
            if (layer.primitive == "solid"){//4
                var width_ = override_default(composition.info, layer, "width");
                var height_ = override_default(composition.info, layer, "height");
                var duration_ = override_default(composition.info, layer, "duration");
                layer_item = comp.layers.addSolid(layer.color, "solid", width_, height_, 1, duration_)
            }//4
        }//3

        set_mode(layer_item, layer.blend_mode, layer.mat_type)
        if (layer.enabled){//3
            layer_item.enabled = true;
        }else{//3
            layer_item.enabled = false;
        }//3
        if (!layer.effects || !layer_item){//3
            //alert("no effects");
            continue
        }//3

        //alert("set effect")
        set_effects(layer_item, layer.effects)
        if (!layer.expression){//3
            continue
        }//3
    }//2
}//1

file_obj = new File($.getenv("__AUTOCOMP_SAVE_PATH__"));
app.project.save(file_obj)
app.quit()