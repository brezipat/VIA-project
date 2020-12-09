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
    m.setCenterZoom(c, zoom)
}

var markers = []

var marker_layer = new SMap.Layer.Marker();
m.addLayer(marker_layer);
marker_layer.enable();

function updateMarkersTable(){
    markers_obj = {};
    markers.forEach((element, index) => {
        data_obj = {};
        data_obj['id'] = element['_id'];
        data_obj['coords'] = element['_coords'].toWGS84(2).reverse().join(", ");
        data_obj['info'] = element['_info'];
        data_obj['links'] = element['_links'];
        markers_obj[index] = data_obj;
    });
//    console.log(markers_obj);
    $.ajax({
          type: "POST",
          contentType: "application/json;charset=utf-8",
          url: "/processMarkers",
          data: JSON.stringify(markers_obj),
          dataType: "json"
    }).done(function(data) {
        document.getElementById('markersTable').innerHTML = data['table']
	});
}

function delete_marker() {
    var name = document.getElementById("delete_marker_name").value;
    if (!name) {
        alert('You have to choose a name for marker you want to delete!');
        return;
    }
    marker_index = -1;
    markers.forEach((element, index) => {
        if (element['_id'] === name) {
            marker_index = index;
            marker_layer.removeMarker(element);
        }
    });
    if (marker_index == -1) {
        alert("There is no such marker");
    } else {
        markers.splice(marker_index, 1);
        updateMarkersTable();
    }
}

function place_marker_util(name, info, coords) {
    var c = SMap.Coords.fromWGS84(coords);
    var name_match = "no";
    var coord_match = "no"
    if (!name) {
        alert('You have to choose a name for your marker!');
        return;
    }
    markers.forEach((element) => {
        if (element['_id'] === name) {
            name_match = "yes";
        }
        if (element['_coords']['x'] == c['x'] && element['_coords']['y'] == c['y']) {
            coord_match = 'yes';
        }
    });
    if (name_match === "no" && coord_match === "no") {
        var options = {title: name};
        var card = new SMap.Card();
        card.getBody().innerHTML = info;
        var marker = new SMap.Marker(c, name, options);
        marker.decorate(SMap.Marker.Feature.Card, card);
        marker['_info'] = info;
        marker['_links'] = {};
        markers.push(marker);
        marker_layer.addMarker(marker);
        updateMarkersTable()
    } else if (name_match === "yes") {
        alert("Marker with such name already exists. Choose a different one!")
    } else {
        alert("Marker on such coordinates already exists. You can't place two markers on top of each other!")
    }
}

function createMarkersFromJson(json) {
//    console.log("logging json")
//    console.log(json);
    for (var key in json) {
        item = json[key];
        var name = item['id'];
        var info = item['info'];
        var c = item['coords'];
        var coords = SMap.Coords.fromWGS84(c);
        var links = item['links'];
//        console.log(links);
        var options = {title: name};
        var card = new SMap.Card();
        body_html = info + '<br/>';
        for (link in links) {
            body_html = body_html + '  ' + links[link];
        }
//        console.log(body_html);
        card.getBody().innerHTML = body_html;
        var marker = new SMap.Marker(coords, name, options);
        marker.decorate(SMap.Marker.Feature.Card, card);
        marker['_links'] = links;
        marker['_info'] = info;
        markers.push(marker);
        marker_layer.addMarker(marker);
    }
    updateMarkersTable();
}

function place_marker(){
    var name = document.getElementById("place_marker_name").value;
    var info = document.getElementById("place_marker_info").value;
    var coords = document.getElementById("place_marker_coords").value;
    place_marker_util(name, info, coords);
}

var form = JAK.gel("form");
JAK.Events.addListener(form, "submit", geokoduj);
document.getElementById("coordinate_search_button").addEventListener("click", coordinate_search);

document.getElementById("place_marker_button").addEventListener("click", place_marker);

document.getElementById("delete_marker_button").addEventListener("click", delete_marker);
