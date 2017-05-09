var map = L.map('map', {
        zoomControl: false
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
L.control.groupedLayers("", groupedOverlays, options).addTo(map);

// Zoom control
L.control.zoom({
    position:'topright'
}).addTo(map);

// END MAP CONTROLS

// BEGIN LAYERS AND LAYER FUNCTIONS

