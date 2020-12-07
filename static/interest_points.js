var m = new SMap(JAK.gel("mapa"), center);

var layer = new SMap.Layer.Marker(undefined, {
	poiTooltip: true
});
m.addLayer(layer).enable();

var dataProvider = m.createDefaultDataProvider();
dataProvider.setOwner(m);
dataProvider.addLayer(layer);
dataProvider.setMapSet(SMap.MAPSET_BASE);
dataProvider.enable();