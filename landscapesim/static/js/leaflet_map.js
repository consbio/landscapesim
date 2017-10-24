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

var groupedOverlays = {"Initial Conditions": {}, "Model Results": {}};
var options = {
    position:"topleft",
    exclusiveGroups: ["Model Results"]
};


var layerControlAdded = false;
var layerControl = L.control.groupedLayers("", groupedOverlays, options);

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

var timestepSlider = L.control.range({
    position: 'bottomright',
    min: 0,
    max: 1,
    value: 1,
    step: 1,
    orient: 'horizontal',
    iconClass: 'leaflet-range-icon'
}).addTo(map);

 // Reparent the time slider so it is visible in 3D viewer
 document.getElementById('time-slider').appendChild(timestepSlider.getContainer());
 $('#time-slider').hide();


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
function updateOutputLayers(run) {
    var config = modelRunCache[run].config;
    timestepSlider.on('input change', function (e) {
        var layer = config.stateclasslayer;
        layer.options.t = Number(e.value);
        layer.redraw();
        layer.bringToFront();
        update3DLayer(layer._url.replace('{t}', globalTimestep).replace('{it}', 1))
    });
    $('#time-slider').show();
    update3DLayer(config.stateclassLayer._url.replace('{t}', mapTimestep).replace('{it}', 1))
}

// Zoom control
L.control.zoom({
    position:'topleft'
}).addTo(map);
