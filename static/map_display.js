var center = SMap.Coords.fromWGS84(14.41790, 50.12655);
var m = new SMap(JAK.gel("mapa"), center, 13);
m.addDefaultLayer(SMap.DEF_BASE).enable();
m.addDefaultControls();
var layers = {};

layers[SMap.DEF_BASE] = m.addDefaultLayer(SMap.DEF_BASE);
layers[SMap.DEF_OPHOTO] = m.addDefaultLayer(SMap.DEF_OPHOTO);
layers[SMap.DEF_HYBRID] = m.addDefaultLayer(SMap.DEF_HYBRID);
layers[SMap.DEF_TURIST] = m.addDefaultLayer(SMap.DEF_TURIST);
layers[SMap.DEF_TURIST_WINTER] = m.addDefaultLayer(SMap.DEF_TURIST_WINTER);
layers[SMap.DEF_BASE].enable(); /* pro začátek zapnout základní podklad */
m.addDefaultControls();

var switchLayer = function(e, elm) {
    for (var p in layers) { layers[p].disable(); }
    switch (elm.selectedIndex) {
        case 0:
            layers[SMap.DEF_BASE].enable();
        break;
        case 1:
            layers[SMap.DEF_OPHOTO].enable();
            layers[SMap.DEF_HYBRID].enable();
        break;
        case 2:
            layers[SMap.DEF_TURIST].enable();
        break;
        case 3:
            layers[SMap.DEF_TURIST_WINTER].enable();
        break;
    }
}

var s = JAK.mel("select");
JAK.gel("controls").innerHTML = "Choose Layer: ";
JAK.gel("controls").appendChild(s);
var names = ["base", "flight", "touristic", "winter"]
for (var i=0; i<names.length; i++) {
    var o = JAK.mel("option");
    o.innerHTML = names[i];
    s.appendChild(o);
}
var e = JAK.Events.addListener(s, "change", window, switchLayer);