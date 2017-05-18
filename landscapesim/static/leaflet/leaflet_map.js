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
    "Output Layers": {
    },
    "Input Layers": {
    },
};

var options = {
    position:"topleft",
    /*exclusiveGroups: ["Reporting Units","Base Maps", "Input Layers"]*/
};

layerControl = L.control.groupedLayers("", groupedOverlays, options).addTo(map);


function loadLayers(scenario_input_services){

    inputStateClassLayer = L.tileLayer(scenario_input_services.stateclass);
    inputStratumLayer = L.tileLayer(scenario_input_services.stratum);

    layerControl.addOverlay(inputStateClassLayer, "State Classes", "Input Layers");
    layerControl.addOverlay(inputStratumLayer, "Vegetation Types", "Input Layers");

    inputStratumLayer.addTo(map)

}

map.on('overlayadd', overlayAdd);

function overlayAdd(e){
    var layer = e.layer;
    layer.bringToFront();

    $("#scene_legend").empty();
    $("#scene_legend").append("<div class='legend_title'>" + e.name + "</div>");
    $.each(colorMap[e.name], function(key,value){
        $("#scene_legend").append("<div class='scene_legend_color' style='background-color:" + value + "'> &nbsp</div>" + key + "<br>")
    });
}

function loadOutputLayers(results_scenario_configuration){

    // Change it to the number of iterations
    // Change t to the min timestep


    map.removeLayer(inputStateClassLayer);
    map.removeLayer(inputStratumLayer);

    if( $("#spatial_switch")[0].checked) {

        var t0it1 = {'t': 0, 'it': 1};

        if (typeof results_scenario_configuration.scenario_output_services.stateclass != "undefined") {

            var outputStateClassLayer = L.tileLayer(results_scenario_configuration.scenario_output_services.stateclass, t0it1).addTo(map).bringToFront();
            layerControl.addOverlay(outputStateClassLayer, "State Classes", "Output Layers");

            var timestep_slider = L.control.range({
                position: 'bottomright',
                min: results_scenario_configuration.run_control.min_timestep,
                max: results_scenario_configuration.run_control.max_timestep - 1,
                value: results_scenario_configuration.run_control.min_timestep,
                step: 1,
                orient: 'horizontal',
                iconClass: 'leaflet-range-icon'
            });

            timestep_slider.on('input change', function (e) {

                outputStateClassLayer.options.t = Number(e.value);
                outputStateClassLayer.redraw();
                outputStateClassLayer.bringToFront();

            });

            map.addControl(timestep_slider);
        }
    }
    else{
        var centroid = bounding_box_layer.getBounds().getCenter();
        var popup = L.popup()
            .setLatLng(centroid)
            .setContent("Spatial output is only available for spatial runs. Enable spatial output under Run Control")
            .openOn(mymap);

    }
}

// Zoom control
L.control.zoom({
    position:'topleft'
}).addTo(map);

