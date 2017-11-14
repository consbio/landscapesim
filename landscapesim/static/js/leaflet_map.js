// The map
var map = L.map('map', {
        zoomControl: false,
        attributionControl: false
    }
).setView([37,-108], 5);

// Basemaps
var topographic = L.esri.basemapLayer("Topographic");
var imagery = L.esri.basemapLayer("Imagery");
var terrain = L.esri.basemapLayer("Terrain");
var national_geographic = L.esri.basemapLayer("NationalGeographic");
var basemaps = map.addControl(L.control.basemaps({
    basemaps: [topographic, terrain, national_geographic, imagery],
    position: 'bottomleft'
}))

/*
var landfire = L.tileLayer.wms("http://landfire.cr.usgs.gov/arcgis/services/Landfire/US_140/MapServer/WMSServer?", {
	layers: "US_140BPS", 	//layers: "US_130BPS",
	format: "image/png",
	transparent: true
}).addTo(map);

landfire.bringToFront();
*/

var currentBasemap = topographic._url;
map.on('baselayerchange', function(basemap) {
    currentBasemap = basemap._url;
})

var groupedOverlays = {"Initial Conditions": {}, "Model Results": {}};
var options = {
    position:"topleft",
    exclusiveGroups: ["Model Results"]
};
var layerControl = L.control.groupedLayers("", groupedOverlays, options).addTo(map);

// Zoom control
L.control.zoom({
    position:'topleft'
}).addTo(map);

// Hide layer control until items have been added
var layerControlHidden = true;
layerControl.getContainer().style.display = 'none';

var inputStateClassLayer;
var inputStratumLayer;
function loadInputLayers(inputServices){
    inputStateClassLayer = L.tileLayer(inputServices.stateclass);
    inputStratumLayer = L.tileLayer(inputServices.stratum);
    layerControl.addOverlay(inputStateClassLayer, "State Classes", "Initial Conditions");
    layerControl.addOverlay(inputStratumLayer, "Vegetation Types", "Initial Conditions");
    inputStratumLayer.addTo(map)
}

map.on('overlayadd', overlayAdd);

function overlayAdd(e){
    var layer = e.layer;
    layer.bringToFront();

    // After a run, the layer name is "State Classes, Run x". Change the name to "State Classes" to match the key in the colorMap dictionary object.
    if (e.name.indexOf("State Classes") > -1){
        e.name = "State Classes"
    }
    updateLegend(e.name);
}

var opacity = L.control.range({
    position: 'topleft',
    min: 0,
    max: 1,
    step: 0.01,
    value: 1,
    orient: 'vertical',
    iconClass: 'leaflet-range-icon'
}).addTo(map);

opacity.getContainer().style.display = 'none';    // Hide until input layers are loaded

opacity.on('input change', function(e) {
    if (typeof inputStateClassLayer != 'undefined') {
        inputStateClassLayer.setOpacity(e.value);
        inputStratumLayer.setOpacity(e.value);    
    }
    if (typeof currentOutputLayer != 'undefined') {
        currentOutputLayer.setOpacity(e.value);
    }
})

function loadOutputLayers(config) {
    if( $("#spatial_switch")[0].checked) {
        map.removeLayer(inputStateClassLayer);
        map.removeLayer(inputStratumLayer);
        var stateclassURL = config.scenario_output_services.stateclass;
        var stateclassLayer = L.tileLayer(stateclassURL, {'t': config.run_control.max_timestep, 'it': 1});
        config.stateclassLayer = stateclassLayer;
        layerControl.addOverlay(stateclassLayer, "State Classes, Run " + modelRunCache.length, "Model Results");
    }
    else{
        var centroid = boundingBoxLayer.getBounds().getCenter();
        var popup = L.popup()
        .setLatLng(centroid)
        .setContent('Spatial output is only available for spatial runs.<p>To conduct a spatial run, turn the spatial output setting to "on" under Run Control.')
        .openOn(map);
    }
}

// Called after a model run (which triggers a tab click), or when a tab is clicked.
var currentOutputLayer;
var timestepSlider;
function updateOutputLayers(run, iteration) {

    if (typeof iteration == 'undefined') {
        iteration = 1;
    }

    var config = modelRunCache[run].config;
    var layer = config.stateclassLayer;
    var step = config.run_control.max_timestep;

    // Remove output layer if set
    if (typeof timestepSlider != 'undefined') {
        map.removeControl(timestepSlider);
        map.removeLayer(currentOutputLayer);
    }

    currentOutputLayer = layer;
    currentOutputLayer.options.t = step;
    currentOutputLayer.options.it = iteration;
    currentOutputLayer.addTo(map);
    currentOutputLayer.setOpacity(Number(opacity.getContainer().children[1].value));

    timestepSlider = L.control.range({
        position: 'bottomright',
        min: 0,
        max: step,
        value: step,
        step: 1,
        orient: 'horizontal',
        iconClass: 'leaflet-range-icon'
    }).addTo(map);

    timestepSlider.on('input change', function (e) {
        layer.options.t = Number(e.value);
        layer.redraw();
        layer.bringToFront();
        update3DLayer(layer._url.replace('{t}', layer.options.t).replace('{it}', iteration))
    });

    // Reparent the time slider so it is visible in 3D viewer
    document.getElementById('time-slider').appendChild(timestepSlider.getContainer());
    
    // Always update the layer after a layer change.
    update3DLayer(layer._url.replace('{t}', layer.options.t).replace('{it}', layer.options.it))
}
