var map = L.map('map', {
        zoomControl: false,
        attributionControl: false
    }
).setView([37,-108], 5);

// Basemaps
var topographic = L.esri.basemapLayer("Topographic").addTo(map);
var imagery = L.esri.basemapLayer("Imagery");
var usa_topo = L.esri.basemapLayer("USATopo");
var national_geographic = L.esri.basemapLayer("NationalGeographic");

var groupedOverlays = {
    "Base Maps": {
        'Topographic': topographic,
        'USA Topo': usa_topo,
        'National Geographic': national_geographic,
        'Imagery': imagery
    },
    "Initial Conditions": {
    },
    "Model Results": {
    }
};

var options = {
    position:"topleft",
    /*exclusiveGroups: ["Reporting Units","Base Maps", "Input Layers"]*/
};

var layerControl = L.control.groupedLayers("", groupedOverlays, options).addTo(map);

var inputStateClassLayer;
var inputStratumLayer;
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

    // After a run, the layer name is "State Classes, Run x". Change the name to "State Classes" to match the key in the colorMap dictionary object.
    if (e.name.indexOf("State Classes") > -1){
        e.name = "State Classes"
    }

    updateLegend(e.name);
}

var outputStateClassServices={};
var outputStateClassLayers={};
var outputTimestepSliders={};
var outputRunSettings={};
var streamingTimestep = 0;

function loadOutputLayers(configuration, streaming){

    if( $("#spatial_switch")[0].checked) {

        map.removeLayer(inputStateClassLayer);
        map.removeLayer(inputStratumLayer);
            
        if (streaming) {

            var updatedStreamingTimestep = configuration.timesteps - 1;

            if (updatedStreamingTimestep <= streamingTimestep) return;

            if (map.hasLayer(outputStateClassLayers[run])) {
                map.removeLayer(outputStateClassLayers[run]);
                map.removeControl(outputTimestepSliders[run])
            }

            streamingTimestep = updatedStreamingTimestep;

            // Store the service for the model run
            outputStateClassServices[run] = configuration.stateclass;

            // Store the run setting for this run (max timestep needed).
            var runControl = {'t': updatedStreamingTimestep, 'it': 1};

            // Create a layer from the run service. Show last timestep and first iteration by default.
            outputStateClassLayers[run] = L.tileLayer(outputStateClassServices[run], runControl).addTo(map);

            // Create dynamic output time slider
            outputTimestepSliders[run] = L.control.range({
                position: 'bottomright',
                min: 0,
                max: updatedStreamingTimestep,
                value: updatedStreamingTimestep,
                step: 1,
                orient: 'horizontal',
                iconClass: 'leaflet-range-icon'
            });

            changeOutputStateClass(run);

        } else {
            // Use global results scenario settings
            // Store the service for the model run
            outputStateClassServices[run] =  results_scenario_configuration.scenario_output_services.stateclass;

            // Store the run setting for this run (max timestep needed).
            var runControl = {'t': results_scenario_configuration.scenario_output_services.timesteps, 'it': 1};

            // Create a layer from the run service. Show last timestep and first iteration by default.
            outputStateClassLayers[run] = L.tileLayer(outputStateClassServices[run], runControl);

            var max_timestep = results_scenario_configuration.run_control.max_timestep - 1;

            // Create an output time step slider.
            outputTimestepSliders[run] = L.control.range({
                position: 'bottomright',
                min: 0,
                max: max_timestep,
                value: max_timestep,
                step: 1,
                orient: 'horizontal',
                iconClass: 'leaflet-range-icon'
            });

            document.getElementById("view" + run + "_link").click();
        }
    }
    else {
        var centroid = bounding_box_layer.getBounds().getCenter();
        var popup = L.popup()
            .setLatLng(centroid)
            .setContent('Spatial output is only available for spatial runs.<p>To conduct a spatial run, turn the spatial output setting to "on" under Run Control.')
            .openOn(map);

    }
}

// Called after a model run (which triggers a tab click), or when a tab is clicked.
var activeRun, globalTimestep;
function changeOutputStateClass(run) {

    activeRun = run;

    // Remove other state class layers.
    $.each(outputStateClassLayers, function(index, stateClassLayer){
        if (map.hasLayer(stateClassLayer)){
            map.removeLayer(stateClassLayer)
        }
    });

    // Remove other sliders.
    $.each(outputTimestepSliders, function(index, object){
        map.removeControl(object)
    });

    outputTimestepSliders[run].addTo(map);

    // Add the slider for the current run // Hookup the timeslider functions here.
    outputTimestepSliders[run].on('input change', function (e) {

        // Store a global time step variable to use in displaying the layer and setting the slider value when a model run tab is clicked.
        globalTimestep = Number(e.value);

        outputStateClassLayers[run].options.t = Number(e.value);
        outputStateClassLayers[run].redraw();
        outputStateClassLayers[run].bringToFront();

        // Also update the 3D layer
        update3DLayer(outputStateClassLayers[run]._url.replace('{t}', globalTimestep).replace('{it}', 1))

    });
    var globalTimestepSet = typeof globalTimestep != "undefined";
    if (globalTimestepSet) {
        outputStateClassLayers[run].options.t = globalTimestep;
        outputTimestepSliders[run].setValue(globalTimestep)
    }

    map.addControl(outputTimestepSliders[run]);

    // Reparent the time slider so it is visible in 3D viewer
    document.getElementById('time-slider').appendChild(outputTimestepSliders[run].getContainer());

    outputStateClassLayers[run].addTo(map);

    // Set the initial timestep map layer in 3D
    var mapTimestep;
    if (typeof results_scenario_configuration == "undefined") {
        mapTimestep = streamingTimestep;
    } else {
        mapTimestep = !globalTimestepSet ? results_scenario_configuration.run_control.max_timestep : globalTimestep;
    }
    update3DLayer(outputStateClassLayers[run]._url.replace('{t}', mapTimestep).replace('{it}', 1))
}

// Zoom control
L.control.zoom({
    position:'topleft'
}).addTo(map);
