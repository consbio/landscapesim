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
function loadInputLayers(inputServices) {
    if (inputServices === null) return;
    inputStateClassLayer = L.tileLayer(inputServices.stateclass);
    inputStratumLayer = L.tileLayer(inputServices.stratum);
    layerControl.addOverlay(inputStateClassLayer, "State Classes", "Initial Conditions");
    layerControl.addOverlay(inputStratumLayer, "Vegetation Types", "Initial Conditions");
    inputStratumLayer.addTo(map)
}

function loadInputLayersFromConfig(info) {
    inputStateClassLayer = L.tileLayer.wms(info.stateclass_service.url, {
        layers: info.stateclass_service.layers
    })
    inputStratumLayer = L.tileLayer.wms(info.stratum_service.url, {
        layers: info.stratum_service.layers
    })
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
    var config = modelRunCache[run].config;

    // If the model run was not spatial, do nothing
    if (!config.run_control.is_spatial) return;

    if (typeof iteration == 'undefined') {
        iteration = 1;
    }
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

/** Start Reporting Unit functions */

var activeRegionLayer = null;

var reportingUnitControl = L.control();
reportingUnitControl.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info');
    this.update();
    return this._div;
};
reportingUnitControl.update = function (props) {
    this._div.innerHTML = '<h4>Reporting Unit Name</h4>' +  (props ?
    '<b>' + props.name
        : 'Hover over a reporting unit');
};

var selectedFeatureStyle = {
    weight: 5,
    dashArray: '',
    fillColor:'#5BDAFF',
    fillOpacity: 0.8
};

var defaultFeatureStyle = {
    "color": "#3D8DFF",
    "weight": 3,
    "opacity": 0.65,
    "fillOpacity":.15
};

var clearRegionLayer = function() {
    if (activeRegionLayer) {
        map.removeLayer(activeRegionLayer);
    }
    map.removeControl(reportingUnitControl);
}

var updateRegionLayer = function(regionName) {
    var region = availableRegions.find(function(x) { return x.name == regionName; })
   
    clearRegionLayer();
    activeRegionLayer = L.geoJSON(region.data, {
        clickable: true,
        style: defaultFeatureStyle,
        onEachFeature: function(feature, layer) {
            layer.on({
                mouseover: function (e) {
                    var layer = e.target;
                    layer.setStyle(selectedFeatureStyle);
                    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                        layer.bringToFront();
                    }
                    reportingUnitControl.update(layer.feature.properties);
                },
                mouseout: function (e) {
                    activeRegionLayer.resetStyle(e.target);

                    if (selectedReportingUnit != null) {
                        selectedReportingUnit.setStyle(selectedFeatureStyle);
                        reportingUnitControl.update(selectedReportingUnit.feature.properties)
                    } else {
                        reportingUnitControl.update()
                    }
                },
                click: function (e) {
                    selectedReportingUnit = e.target;
                    enableLoadButton();
                }
            })
        }
    });
    reportingUnitControl.addTo(map);
    activeRegionLayer.addTo(map);
}

/** End Reporting Unit functions */
