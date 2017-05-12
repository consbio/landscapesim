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
    "Reference Layers": {
    }
};

var options = { exclusiveGroups: ["Reporting Units","Base Maps"]};

function loadLayers(scenario_input_services){

    var stateClassLayer = L.tileLayer(scenario_input_services.stateclass);
    var stratumLayer = L.tileLayer(scenario_input_services.stratum);

    groupedOverlays["Reference Layers"]["State Class"] = stateClassLayer;
    groupedOverlays["Reference Layers"]["Vegetation Type"] =  stratumLayer;

    L.control.groupedLayers("", groupedOverlays, options).addTo(map);

    stratumLayer.addTo(map)

}

// Zoom control
L.control.zoom({
    position:'topright'
}).addTo(map);

