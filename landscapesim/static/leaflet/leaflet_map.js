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

var options = {
    position:"topleft",
    exclusiveGroups: ["Reporting Units","Base Maps", "Library Layers"]
};

layerControl = L.control.groupedLayers("", groupedOverlays, options).addTo(map);


function loadLayers(scenario_input_services){

    var stateClassLayer = L.tileLayer(scenario_input_services.stateclass);
    var stratumLayer = L.tileLayer(scenario_input_services.stratum);

    stateClassLayer.on

    layerControl.addOverlay(stateClassLayer, "State Classes", "Library Layers");
    layerControl.addOverlay(stratumLayer, "Vegetation Types", "Library Layers");

    stratumLayer.addTo(map)

}

map.on('overlayadd', swapLegend);

function swapLegend(e){

    $("#scene_legend").empty();
    $("#scene_legend").append("<div class='legend_title'>" + e.name + "</div>");
    $.each(colorMap[e.name], function(key,value){
        $("#scene_legend").append("<div class='scene_legend_color' style='background-color:" + value + "'> &nbsp</div>" + key + "<br>")
    });
}


function loadOutputLayers(scenario_output_services){

    // Change it to the number of iterations
    // Change t to the min timestep

    var t0it1 = {'t': 0, 'it': 1};

    if (typeof scenario_output_services.stateclass != "undefined") {

        var stateClassLayer = L.tileLayer(scenario_output_services.stateclass, t0it1);


        var timestep_slider = L.control.range({
            position: 'topright',
            min: config.run_control.min_timestep,
            max: config.run_control.max_timestep - 1,
            value: config.run_control.min_timestep,
            step: 1,
            orient: 'horizontal',
            iconClass: 'leaflet-range-icon'
        });

        timestep_slider.on('input change', function (e) {

            stateClassLayer.options.t = Number(e.value);
            stateClassLayer.redraw();

        });

        map.addControl(timestep_slider);
    }

}

// Zoom control
L.control.zoom({
    position:'topleft'
}).addTo(map);

