function getSelectedLayers(){
    var project = app.project;
    var composition = project.activeItem; 
    return composition.selectedLayers;
}

function setTimeremap(values){
    var project = app.project;
    var composition = project.activeItem; 
    var activeLayers = getSelectedLayers();
    var frameRate = 1/composition.frameDuration;
    
    for(var i=0; i < activeLayers.length; i++){
        var layer = activeLayers[i];
        if(layer.timeRemapEnabled == true){
            layer.timeRemapEnabled = false;
        }
        layer.timeRemapEnabled = true;
        layer.timeRemap.removeKey(2);
        for(var ii=0; ii < values.length; ii++){
            value_s = values[ii].split("@")
            layer.timeRemap.setValueAtTime(parseInt(value_s[1])/frameRate, parseInt(value_s[0])/frameRate);
            // layer.timeRemap.setInterpolationTypeAtKey(ii+1, KeyframeInterpolationType.HOLD); 
            // return
        }
    }
}

function remap_from_file(path){
    var obj = new File(path)
    obj.open("r");
    var obj_split = obj.read().split("\n");
    setTimeremap(obj_split)
}

function execute(){
    directory = "*.txt";
    var path = File.openDialog("select text", directory);
    if(path){
        remap_from_file(path);
    }
}

function ui(){
    var w = new Window("palette");
    w.btn = w.add("button", undefined, "remap from file");
    w.btn.onClick = function(){
        var layers = getSelectedLayers();
        if(layers.length == 0){
            alert("select layer(s)");
            return
        }
        execute();
    }
    w.show();
}

//setTimeremap(["0@10", "1@2", "2@5"])

ui();