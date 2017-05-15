var map = L.map('map', {
        zoomControl: false,
        attributionControl: false
    }
).setView([37,-108], 5);

// Basemaps
topographic=L.esri.basemapLayer("Topographic").addTo(map);
imagery=L.esri.basemapLayer("Imagery");
usa_topo=L.esri.basemapLayer("USATopo");
national_geographic=L.esri.basemapLayer("NationalGeographic");

var groupedOverlays = {
    "Base Maps": {
        'Topographic': topographic,
        'USA Topo': usa_topo,
        'National Geographic': national_geographic,
        'Imagery': imagery,
    },
    "Library Layers": {
    }
};

layerControl = L.control.groupedLayers("", groupedOverlays, options).addTo(map);

var options = { exclusiveGroups: ["Reporting Units","Base Maps"]};

function loadLayers(scenario_input_services){

    var stateClassLayer = L.tileLayer(scenario_input_services.stateclass);
    var stratumLayer = L.tileLayer(scenario_input_services.stratum);

    layerControl.addOverlay(stateClassLayer, "State Classes", "Library Layers");
    layerControl.addOverlay(stratumLayer, "Vegetation Types", "Library Layers");

    stratumLayer.addTo(map)

}

// Zoom control
L.control.zoom({
    position:'topright'
}).addTo(map);

