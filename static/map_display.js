var center = SMap.Coords.fromWGS84(14.1, 50.1);
var m = new SMap(JAK.gel("mapa"), center);
m.addDefaultLayer(SMap.DEF_BASE).enable();
m.addDefaultLayer(SMap.DEF_OPHOTO);
m.addDefaultLayer(SMap.DEF_TURIST);
m.addDefaultLayer(SMap.DEF_TURIST_WINTER);
m.addDefaultControls();

// m.addControl(new SMap.Control.Sync());

var layer = new SMap.Layer.Marker(undefined, {
	poiTooltip: true
});
m.addLayer(layer).enable();

var dataProvider = m.createDefaultDataProvider();
dataProvider.setOwner(m);
dataProvider.addLayer(layer);
dataProvider.setMapSet(SMap.MAPSET_BASE);
dataProvider.enable();

var l = new SMap.Layer.Marker();
m.addLayer(l).enable();

var layerSwitch = new SMap.Control.Layer({
	width: 65,
  items: 4,
  page: 4
});
layerSwitch.addDefaultLayer(SMap.DEF_BASE);
layerSwitch.addDefaultLayer(SMap.DEF_OPHOTO);
layerSwitch.addDefaultLayer(SMap.DEF_TURIST);
layerSwitch.addDefaultLayer(SMap.DEF_TURIST_WINTER);
m.addControl(layerSwitch, {left:"0px", top:"0px"});

function geokoduj(e, elm) {
    JAK.Events.cancelDef(e);
    var query = JAK.gel("place_search").value;
    new SMap.Geocoder(query, odpoved);
}

function odpoved(geocoder) { /* Odpověď */
    if (!geocoder.getResults()[0].results.length) {
        alert("Tohle neznáme.");
        return;
    }

    var vysledky = geocoder.getResults()[0].results;
    sentData = {}
    while (vysledky.length) { /* Zobrazit všechny výsledky hledání */
        var item = vysledky.shift();
        item.coords = item.coords.toWGS84(2).reverse().join(", ");
        sentData[item.id] = item;
    }
    $.ajax({
        type: "POST",
        contentType: "application/json;charset=utf-8",
        url: "/placeSearch",
        data: JSON.stringify(sentData),
        dataType: "json"
    }).done(function(data) {
        var par = document.createElement('p');
        for (var key in data) {
            var label = document.createElement('label');
            label.innerHTML = data[key].trim();
            par.appendChild(label);
        }
        old_par = document.getElementById('searchResultPar');
        document.getElementById('searchResult').replaceChild(par,old_par);
        par.setAttribute("id", "searchResultPar");
	});
}

function coordinate_search() {
    var coords = document.getElementById("coordinate_search_text").value;
    var c = SMap.Coords.fromWGS84(coords);
    var zoom = 16;
    // m.setCenter(c);
    m.setCenterZoom(c, zoom)
}

var markers = []

var marker_layer = new SMap.Layer.Marker();
m.addLayer(marker_layer);
marker_layer.enable();

function place_marker() {
    var options = {};
    var coords = document.getElementById("place_marker_text").value;
    var c = SMap.Coords.fromWGS84(coords);
    var marker = new SMap.Marker(c, "myMarker", options);
    markers.push(marker);
    marker_layer.addMarker(marker);
}

function sendMarkersToFlask() {
    markers_obj = {};
    for (var i = 0; i < markers.length; i++) {
        marker = markers[i]
        console.log(marker['_options']);
        console.log(marker['_ec']);
        console.log(marker['_id']);
        markers_obj[i] = marker['_id'];
    }
    console.log(markers_obj);
    $.ajax({
          type: "POST",
          contentType: "application/json;charset=utf-8",
          url: "/map",
          data: JSON.stringify(markers_obj),
          dataType: "json"
    });
}

var form = JAK.gel("form");
JAK.Events.addListener(form, "submit", geokoduj);
document.getElementById("coordinate_search_button").addEventListener("click", coordinate_search);

document.getElementById("sendMarkers").addEventListener("click", sendMarkersToFlask);

document.getElementById("place_marker_button").addEventListener("click", place_marker);
