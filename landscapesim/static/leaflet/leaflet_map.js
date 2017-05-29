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
    "Initial Conditions": {
    },
    "Model Results": {
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

    layerControl.addOverlay(inputStateClassLayer, "State Classes", "Initial Conditions");
    layerControl.addOverlay(inputStratumLayer, "Vegetation Types", "Initial Conditions");

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

outputStateClassServices={};
outputStateClassLayers={};
outputTimestepSliders={};
outputRunSettings={};

function loadOutputLayers(results_scenario_configuration){

    if( $("#spatial_switch")[0].checked) {

        map.removeLayer(inputStateClassLayer);
        map.removeLayer(inputStratumLayer);

        if (typeof results_scenario_configuration.scenario_output_services.stateclass != "undefined") {

            // Store the service for the model run
            outputStateClassServices[run] = results_scenario_configuration.scenario_output_services.stateclass;

            // Store the run setting for this run (max timestep needed).
            var runControl = {'t': current_scenario.config.run_control.max_timestep, 'it': 1};

            // Create a layer from the run service. Show last timestep and first iteration by default.
            outputStateClassLayers[run] = L.tileLayer(outputStateClassServices[run], runControl);

            // Add layer control
            layerControl.addOverlay(outputStateClassLayers[run], "State Classes, Run " + run, "Model Results");

            // Create an output time step slider.
            outputTimestepSliders[run] = L.control.range({
                position: 'bottomright',
                min: results_scenario_configuration.run_control.min_timestep,
                max: results_scenario_configuration.run_control.max_timestep,
                value: results_scenario_configuration.run_control.max_timestep,
                step: 1,
                orient: 'horizontal',
                iconClass: 'leaflet-range-icon'
            });


        }
    }
    else{
        var centroid = bounding_box_layer.getBounds().getCenter();
        var popup = L.popup()
            .setLatLng(centroid)
            .setContent('Spatial output is only available for spatial runs.<p>To conduct a spatial run, turn the spatial output setting to "on" under Run Control.')
            .openOn(map);

    }

    // Click action will trigger the function below
    document.getElementById("view" + run + "_link").click();
}

// Called after a model run (which triggers a tab click), or when a tab is clicked.
function changeOutputStateClass(run) {

    activeRun = run;

    console.log(1)

    // Remove other state class layers.
    $.each(outputStateClassLayers, function(index, stateClassLayer){
        if (map.hasLayer(stateClassLayer)){
            map.removeLayer(stateClassLayer)
        }
    })

    console.log(2)


    console.log(3)
    // Remove other sliders.
    $.each(outputTimestepSliders, function(index, object){
        map.removeControl(object)
    });

    console.log(4)
    outputTimestepSliders[run].addTo(map);

    console.log(5)

    // Add the slider for the current run // Hookup the timeslider functions here.
    outputTimestepSliders[run].on('input change', function (e) {

        // Store a global time step variable to use in displaying the layer and setting the slider value when a model run tab is clicked.
        globalTimestep = Number(e.value);

        outputStateClassLayers[run].options.t = Number(e.value);
        outputStateClassLayers[run].redraw();
        outputStateClassLayers[run].bringToFront();

    });

    if (typeof globaltimestep != "undefined") {
        outputStateClassLayers[run].options.t = globalTimestep;
        outputTimestepSliders[run].setValue(globalTimestep)
    }

    map.addControl(outputTimestepSliders[run]);

    console.log(6)

    outputStateClassLayers[run].addTo(map);

}

// Zoom control
L.control.zoom({
    position:'topleft'
}).addTo(map);

