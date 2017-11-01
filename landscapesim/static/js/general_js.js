// where all the magic happens (i.e. the data store)
var availableLibraries = [];
var currentLibrary = {};
var projectURL = '';
var available_projects = [];
var currentProject = {};
var available_scenarios = [];
var scenarioURL = '';
var currentScenario = {};
var runModelURL = '/api/jobs/run-model/';
var settings;
var boundingBoxLayer;
var librarySelected = false;

/* Utility for deep copies on non-prototyped objects. */
var copy = function(obj) { return JSON.parse(JSON.stringify(obj)); }

var getCurrentInfo = function() {

    // TODO - include a way to determine the proper extent for the given area.
    // TODO - handle non-hardcoded extents? i.e. landfire
    return store[$(".model_selection").val()];
}

$(document).ready(function() {

    // Always open instructions on page load
    document.getElementById('instructions').click();

    // Top-level endpoint, get list of available libraries
    $.getJSON('/api/libraries/').done(function (res) {

        availableLibraries = res.results;

        // Add each library to the library selection dropdown.
        $.each(availableLibraries, function(index, library){
            $(".model_selection").append("<option value ='" + library.id + "'>" + library.name)
        });

        $("select").prop("selectedIndex",0);
        $("#spatial_switch")[0].checked = true

    });

    /************************************************* Run Model  ****************************************************/
    // Send the scenario and initial conditions to ST-Sim.
    settings = [];
    settings["spatial"] = false;

    // Progressbar for model run
    var progressbar = $('#progressbar'), progressbarlabel = $('#progresslabel');

    $('#run_button').on('click', function() {

        // Clear the current transition_spatial_multipliers
        currentScenario.config.transition_spatial_multipliers = [];

        // Set default output options
        currentScenario.config.output_options.sum_tr = true;
        currentScenario.config.output_options.sum_tr_t = 1;
        currentScenario.config.output_options.sum_trsc = true;
        currentScenario.config.output_options.sum_trsc_t = 1;

        // Now go find the proper geoJSON
        var timesteps = currentScenario.config.run_control.max_timestep;
        currentProject.definitions.transition_groups.forEach(function(grp) {

            // Get all actions for this transition_group
            var groupActions = managementActionsList.filter(function(x) { return x.action_id == grp.id });

            // If actions are to be taken, create transition spatial multipliers
            if (groupActions.length > 0) {
                for (var ts = 1; ts <= timesteps; ts+=1) {

                    // Find all actions for this group with the same timestep
                    var timestepGroup = groupActions.filter(function(x) {
                        var idx = ts - 1;
                        if (idx >= x.timesteps.length) return false;
                        return  x.timesteps[idx] == 1
                    })

                    if (timestepGroup.length > 0) {

                        // And collect all their geojson
                        var geojson = timestepGroup.map(function (x) {
                            return x.geoJSON
                        })

                        // Submit one raster to be created for this management action type for this timestep
                        currentScenario.config.transition_spatial_multipliers.push({
                            transition_group: grp.id,
                            timestep: ts,
                            iteration: null,
                            transition_multiplier_type: null,
                            transition_multiplier_file_name: null,
                            geojson: geojson,
                        })
                    }
                }
            }
        })

        $("#start_button").attr("disabled", true);
        $("#start_button").addClass('disabled');

        settings["library"] = currentLibrary.name;
        settings["spatial"] = $("#spatial_button").hasClass('selected')

        $(".slider_bars").slider( "option", "disabled", true );
        $('input:submit').attr("disabled", true);
        $("#run_button").addClass('disabled');
        $("#run_button").html("Running ST-Sim...<div id='results_loading'><img src='/static/img/spinner.gif'></div>");
        $(".leaflet-right").css("right", "380px");

        // Enable progressbar
        $("#progressbar-container").show();

        var updateProgress = function(progress, jobStatus, modelStatus) {

            if (modelStatus == 'waiting') {
                progressbarlabel.text("Waiting for worker...");
            }
            else if (modelStatus == 'starting') {
                progressbarlabel.text("Starting worker...");
            }
            else if (jobStatus == 'started' && modelStatus == 'running') {
                if (progress !== undefined && progress !== null) {
                    var intProgress = parseInt(progress * 100);
                    progressbar.css('width', intProgress + '%');
                    progressbarlabel.text(intProgress + "% Complete")
                }
                else {
                    progressbarlabel.text(0 + "% Complete")
                }

                if (modelStatus == 'processing' || modelStatus == 'complete') {
                    progressbarlabel.text("Run Complete - Preparing Results");
                }
            }
        }

        var inputs = {
            'sid': currentScenario.sid,
            'pid': currentProject.pid,
            'library_name': currentLibrary.name,
            'config': currentScenario.config
        };

        $.post(runModelURL, {'inputs': JSON.stringify(inputs)})
            .done(function (job) {
                (function poll() {
                    setTimeout(function() {
                        $.getJSON(runModelURL + job.uuid + '/').done(function (update) {
                            updateProgress(update.progress, update.status, update.model_status);
                            if (update.status === 'success' || update.model_status === 'complete') {
                                $("#output").show();
                                var results_model_id = String(update.result_scenario);
                                var reports_url = window.location.href + "api/scenarios/" + results_model_id + "/reports/";
                                var results_scenario_configuration_url = window.location.href + "api/scenarios/" + results_model_id + "/config/";
                                $.getJSON(reports_url).done(function (reportURLs) {
                                    var stateclassReportURL = reportURLs['stateclass_summary_report'];
                                    $("#results_loading").empty();
                                    $.getJSON(stateclassReportURL).done(function (reportData) {
                                        $.getJSON(results_scenario_configuration_url).done(function (config) {
                                            reportData.config = copy(config);
                                            loadOutputLayers(reportData.config);
                                            processStateClassSummaryReport(reportData);
                                            updateModelRunSelection(modelRunCache.length - 1);
                                            updateResultsViewer(modelRunCache.length - 1);
                                            $('#progressbar-container').hide();
                                            progressbar.css('width', '0%');
                                            progressbarlabel.text("Waiting for worker...")
                                            var resultsHeader = $("#model_results_header");
                                            if (!resultsHeader.hasClass('full_border_radius')) resultsHeader.click();
                                        });
                                    });
                                });
                                $("#run_button").html('Run Model');
                                $("#run_button").removeClass('disabled');
                                $('input:submit').attr("disabled", false);
                                $(".slider_bars").slider( "option", "disabled", false );
                                $("#button_container").attr("disabled", false);
                                $("#legend_header").nextAll(".collapsible_div:first").slideUp(400, function(){});
                                $("#legend_header").children(".collapse_icon").addClass("rotate90");
                                $("#legend_container").css("width", "100%")
                            } else if (update.status === 'failure') {
                                alert('An error occurred. Please try again.')
                                $("#run_button").html('Run Model');
                                $("#run_button").removeClass('disabled');
                                $('input:submit').attr("disabled", false);
                                $('#button_container').attr("disabled", false);
                            } else {
                                poll();
                            }
                        })
                   }, 1500)
                })();
            });
    });

    /***************************************** Change Library *********************************************************/

    $(".model_selection").on("change", function() {
        $("#model_selection_td").removeClass("initial_td_styling");
        showLibraryInfo();
        $(".library_info_hidden").show();
        $("#start_button").show();
    });

    // Also called on page load.
    function showLibraryInfo() {
        var info = getCurrentInfo();

        // Show the layer
        boundingBoxLayer = L.geoJSON(info.extent).addTo(map);
        boundingBoxLayer.bindPopup(info.name + " Extent").openPopup();

        // Uppate the values in the library_info table
        $("#library_author").html(info.author);
        $("#library_date").html(info.date);
        $("#library_description").html(info.description);

    };

    /********************************************** Load Library (Start) **********************************************/

    $("#start_button").on("click", function(){

        if (layerControlHidden) {
            layerControl.getContainer().style.display = '';
            opacity.getContainer().style.display = '';
            layerControlHidden = false;
        }

        $("#library_header").addClass("full_border_radius");

        currentLibrary = $.grep(availableLibraries, function(e) {return e.id == $(".model_selection").val()})[0];
        available_projects = currentLibrary.projects;
        projectURL = available_projects[0];

        // Get Stuff from the Web API
        $.getJSON(projectURL).done(function (project) {
            currentProject = project;
            available_scenarios = currentProject.scenarios;

            // Get project definitions
            $.getJSON(projectURL + 'definitions').done(function (definitions) {
                currentProject.definitions = definitions;
                createColorMap(currentProject.definitions)
            });

            // Select scenario from list; here we are just taking the top one
            scenarioURL = available_scenarios[0];

            // Get scenario information
            $.getJSON(scenarioURL).done(function (scenario) {
                currentScenario = scenario;


                // Scenario configuration (at import)
                $.getJSON(scenarioURL + 'config').done(function (config) {
                    currentScenario.config = config;

                    // Spatial by default:
                    setSpatialOutputOptions(true);

                    // Store the original transition values to reference when adjusting probabilistic transition sliders.
                    $.each(currentScenario.config.transitions, function(index, object){
                        object.original_probability = object.probability;
                    });

                    // Create objects from Web API data
                    vegInitialConditions = createVegInitialConditionsDict();
                    createVegTypeStateClassesJSON(vegInitialConditions);

                    // Set Initial Conditions (Veg sliders & Probabilistic Transitions)
                    setInitialConditionsSidebar(vegInitialConditions);

                    loadInputLayers(currentScenario.config.scenario_input_services);
                    init3DScenario(inputStratumLayer._url);

                    $(".veg_slider_bars").slider("disable");
                    $(".veg_slider_bars").addClass("disabled");
                    $(".veg_state_class_entry").addClass("disabled");
                    $(".veg_state_class_entry").prop("disabled", true);

                    $("#settings_timesteps").val(currentScenario.config.run_control.max_timestep);
                    $("#timesteps_div").text(["Timesteps (", unitConfig[$(".model_selection").val()].timesteps, "):"].join(''));
                })

            });

            //map.fitBounds(boundingBoxLayer.getBounds(),{"paddingTopLeft":[0,1]});
            map.fitBounds(boundingBoxLayer.getBounds());
            map.removeLayer(boundingBoxLayer);

            // Collapse the Welcome and Library divs.
            $("#library_header").siblings(".collapsible_div").slideUp(400, function(){});
            $("#library_header").children(".collapse_icon").addClass("rotate90");

            // Show the other inputs.
            $("#inputs").show();
            $("#initial_vegetation_container").show();
            $("#legend_container").show();

            // Management Action Controls
            $(".leaflet-control-command-button-container").show();
            $(".leaflet-control-command-form").show();
            $(".leaflet-control-command").show();
            $(".leaflet-draw").show();
            $(".leaflet-left")[0].style.top = '60px';
            $("#scene-toggle").show();
            document.getElementById('scene-toggle').style.display = 'inline-block';
            librarySelected = true
        })
    });

    /********************************************* General UI Functions ***********************************************/

    // Switch context between map and 3D viewer
    $(document).on("change", "#scene-switch", function(){
        if ($(this)[0].checked){
            $('#map').hide();
            $('#scene').show();
            resize();
            window.addEventListener('resize', resize, false);
            animate();
        }
        else{
            $('#scene').hide();
            window.removeEventListener('resize', resize, false);
            cancelAnimate();
            $('#map').show();
            map.invalidateSize();
        }
    });

    // Collapse div on header click
    $(document).on("click", ".header", function () {

        // Get this collapsible div
        var this_collapsible_div = $(this).siblings(".collapsible_div");

        // If a library has been loaded, collapse other divs on header click.
        if (librarySelected){
            collapseOtherDivs(this)
        }

        // Toggle the border radius
        $(this).toggleClass("full_border_radius");
        var this_collapse_icon =$(this).children(".collapse_icon");

        // Toggle the collapse icon
        toggleIcon(this_collapse_icon);

        // Slide toggle this div.
        this_collapsible_div.slideToggle(400, function () {

            // Figure out the header position and determine the max height;
            var this_div_position = $(this).offset().top;
            var max_height = $(window).height() - this_div_position - 220;
            this_collapsible_div.css('max-height', max_height);
        });
    });

    // Collapse div on header click
    $(document).on("click", "#model_results_header", function () {

            // Get this collapsible div
            var this_collapsible_div = $(this).siblings(".collapsible_div");

            // Toggle the border radius
            $(this).toggleClass("full_border_radius");
            var this_collapse_icon =$(this).children(".collapse_icon");

            // Toggle the collapse icon
            toggleIcon(this_collapse_icon);

            // Slide toggle this div.
            this_collapsible_div.slideToggle(400, function () {

                // Figure out the header position and determine the max height;
                var this_div_position = $(this).offset().top;
                var height = $(window).height() - this_div_position - 120;
                this_collapsible_div.css('height', height);
            });
    });

    // Download data from currently viewable model results.
    $("#download-data").on("click", downloadModelResults);

    function toggleIcon(collapse_icon){

        // Rotate the arrow icon.
        if (collapse_icon.hasClass("rotate90")){
            $(collapse_icon).removeClass("rotate90");
        }
        else {
            $(collapse_icon).addClass("rotate90");
        }
    }

    function collapseOtherDivs(this_header) {
        // For left hand header clicks, collapse the other divs
        var this_collapsible_div = $(this_header).siblings(".collapsible_div");

        if (!$(this_header).hasClass("right_header")) {

            var other_collapsible_divs = $("#left .header").siblings(".collapsible_div").not(this_collapsible_div);
            $.each(other_collapsible_divs, function () {
                $(this).slideUp();
                $(this).toggleClass("full_border_radius");
            });

            var other_headers = $("#left .header").not(this_header);
            $.each(other_headers, function () {
                $(this).addClass("full_border_radius");
                $(this).children(".collapse_icon").addClass("rotate90");
            });
        }
    }

    $(document).on("click", ".close_state_class", function(){
        map.removeLayer(inputStateClassLayer);
        updateLegend("Vegetation Types");
        update3DLayer(inputStratumLayer._url);
        $(this).parents(".sub_slider_text_inputs").hide()
    });

    // Tooltip popup on management scenarios
    $(".scenario_radio_label").hover(function(e) {
        var moveLeft = 50;
        var moveDown = -20;
        $("div#pop-up").html(this.id);
        $('div#pop-up').show();
        $('.scenario_radio_label').mousemove(function(e) {
            $("div#pop-up").css('top', e.pageY + moveDown).css('left', e.pageX + moveLeft);
        });

      // On mouse out
    },function(e){
            $('div#pop-up').hide();
            $(this).css("background-color", "white");
        }
    );

    // delegate the popup menus for any that occur on the page.
    function delegatedPopupContext(selector, element) {
        $(document).on('click', selector, function () {
            var url;
            if ($(this).siblings(element).is(":visible")) {
                $(this).siblings(element).hide();
                map.removeLayer(inputStateClassLayer);
                updateLegend("Vegetation Types");
                url = inputStratumLayer._url
            }
            else {
                $(".sub_slider_text_inputs").hide();
                $(this).siblings(element).show();
                inputStateClassLayer.addTo(map);
                updateLegend("State Classes");
                url = inputStateClassLayer._url
            }
            update3DLayer(url);
        });
    }

    delegatedPopupContext('.show_state_classes_link', '.sub_slider_text_inputs');
    delegatedPopupContext('.manage_div', '.management_action_inputs');

    /*********************************************** Spatial Setting **************************************************/

    $(document).on("change", "#spatial_switch", function(){
        setSpatialOutputOptions($(this)[0].checked)
        if ($(this)[0].checked){

            $(".veg_slider_bars").slider("disable");
            $(".veg_slider_bars").addClass("disabled");
            $(".veg_state_class_entry").addClass("disabled");
            $(".veg_state_class_entry").prop("disabled", true);
        }
        else{

            $(".veg_slider_bars").slider("enable");
            $(".veg_slider_bars").removeClass("disabled");
            $(".veg_state_class_entry").removeClass("disabled");
            $(".veg_state_class_entry").prop("disabled", false);
        }

    });

    function setSpatialOutputOptions(setting) {

        var raster_frequency;

        currentScenario.config.run_control.is_spatial = setting;
        currentScenario.config.output_options.raster_sc = setting;

        if(setting == true){

            raster_frequency = 1;

            // Management Action Controls
            $(".leaflet-control-command-button-container").show();
            $(".leaflet-control-command-form").show();
            $(".leaflet-control-command").show();
            $(".leaflet-draw").show();

        }
        else{
            raster_frequency = -1;

            // Management Action Controls
            $(".leaflet-control-command-button-container").hide();
            $(".leaflet-control-command-form").hide();
            $(".leaflet-control-command").hide();
            $(".leaflet-draw").hide();
        }

        currentScenario.config.output_options.raster_sc_t = raster_frequency;

        /* Taylor's suggestion for temporarily fixing the 20 timestep error */
        currentScenario.config.output_options.raster_tr = false;
        currentScenario.config.output_options.raster_tr_t = -1;

        /* Other setting don't currently work

        $.each(currentScenario.config.output_options, function (key, value) {

            if (key.indexOf("raster") > -1) {

                if ((key).split("_").pop() == "t") {
                    currentScenario.config.output_options[key] = timesteps;
                }
                else {
                    currentScenario.config.output_options[key] = setting;
                }

            }

        });
        */
    }


    /**************************************** State Class Input Changes ***********************************************/

    // On state class value entry move slider bar
    $(document).on('keyup', '.veg_state_class_entry', function() {
        var veg_type_id = this.id.split("_")[1];
        var veg_type = this.closest('table').title;

        //Subtract the current slider value from the total percent
        total_input_percent = total_input_percent - veg_slider_values[veg_type];

        veg_slider_values_state_class[veg_type]={};
        var veg_state_class_value_totals=0.0;

        /* New Web API version */
        // Update the value in the initial conditions object for this veg type/state class
        var state_class_id = this.id.split("_")[2];
        var state_class_value = parseFloat($(this).val());

        if (isNaN(state_class_value)) {
            state_class_value = 0;
        }

        $.each(currentScenario.config.initial_conditions_nonspatial_distributions, function (index, vegtypeStateclassObj) {
            if (vegtypeStateclassObj.stratum == parseInt(veg_type_id) && vegtypeStateclassObj.stateclass == parseInt(state_class_id)) {
                vegtypeStateclassObj.relative_amount = state_class_value;
            }
        });

        // Recalculate the total amount for this state class.
        $("#" + veg_type_id).find('input').each(function(){
            var input_value =  parseFloat($(this).val());
            if (isNaN(input_value)) {
                input_value = 0;
            }
             veg_state_class_value_totals += input_value;
        });

        // To avoid initialization error
        if ($("#veg" + veg_type_id + "_slider").slider()) {
            $("#veg" + veg_type_id + "_slider").slider("value", veg_state_class_value_totals)
            var this_veg_slider_value=$("#veg" + veg_type_id  + "_slider").slider("option", "value");
            veg_slider_values[veg_type]=this_veg_slider_value
        }

        //Add the current slider value from the total percent
        total_input_percent = total_input_percent + veg_slider_values[veg_type];

        if (veg_state_class_value_totals > 100){

            $("#total_input_percent").html(">100%");
            total_percent_action(9999);

        }

        else {

            $("#total_input_percent").html(total_input_percent.toFixed(0) + "%");
            total_percent_action(total_input_percent.toFixed(0));

        }

    });

    $("#reset_default_probabilistic_transitions").on("click", function(){
        reset_probabilistic_transitions();
    });

    function reset_probabilistic_transitions() {
        var count=1;
        $.each(probabilistic_transitions_json, function (transition_type) {
            probabilistic_transitions_slider_values[transition_type] = 0;
            $("#probabilistic_transition" + count + "_slider").slider("value", 0);
            $("#probabilistic_transition" + count + "_label").val("Default Probabilities");
            count+=1;
        });
    }

    /********************************************** Timestep Changes **************************************************/

    $("#settings_timesteps").on("keyup", function(){
        var user_timesteps =  parseFloat($(this).val());

        if (isNaN(user_timesteps)) {
            alert("Please enter an integer value");
            $(this).val(1)
        }
        else if (user_timesteps == 0 ) {
            alert("Please enter a value greater than 0");
            $(this).val(1)
        }

        currentScenario.config.run_control.max_timestep = parseInt($(this).val())
    });

    /********************************************* Iteration Changes **************************************************/

    $("#settings_iterations").on("keyup", function(){
        var user_iterations =  parseFloat($(this).val());

        if (isNaN(user_iterations)) {
            alert("Please enter an integer value");
            $(this).val(1)
        }
        else if (user_iterations == 0 ) {
            alert("Please enter a value greater than 0");
            $(this).val(1)
        }
        currentScenario.config.run_control.max_iteration = parseInt($(this).val());
    });

});

/***************************************** Create objects from Web API ************************************************/

// Takes the data returned from the web api and restructure it to create the the objects below
// which are then used to create the sliders
// vegInitialConditions
// vegtypeStateclassesDictionary

function createVegInitialConditionsDict() {

   // current_proejct.definitions can be slow to initialize. Keep trying until it's defined.

   if (typeof currentProject.definitions != "undefined") {

       var vegInitialConditions = {};
       vegInitialConditions["veg_sc_pct"] = {};

       $.each(currentScenario.config.initial_conditions_nonspatial_distributions, function (index, object) {
           var strataObj = $.grep(currentProject.definitions.strata, function (e) {
               return e.id == object.stratum;
           });
           var strataName = strataObj[0].name;
           if (!(strataName in vegInitialConditions["veg_sc_pct"])) {
               vegInitialConditions["veg_sc_pct"][strataName] = {};
           }

           var state_class_object = $.grep(currentProject.definitions.stateclasses, function (e) {
               return e.id == object.stateclass;
           });
           var state_class_name = state_class_object[0].name;
           if (object.relative_amount != 0) {
               vegInitialConditions["veg_sc_pct"][strataName][state_class_name] = object.relative_amount
           }
       });

       return vegInitialConditions

   } else {

       setTimeout(createVegInitialConditionsDict,250);
   }
}

var vegtypeStateclassesDictionary;
function createVegTypeStateClassesJSON(vegInitialConditions) {
    vegtypeStateclassesDictionary = {};
    $.each(vegInitialConditions["veg_sc_pct"], function(veg_type,state_class_object){
        var count=0;
        vegtypeStateclassesDictionary[veg_type] = [];
        $.each(state_class_object, function(state_class, relative_amount){
            vegtypeStateclassesDictionary[veg_type][count] = state_class;
            count+=1;
        });
    });
}

/*************************************** Initial Vegetation Cover Inputs **********************************************/
function updateLegend(name) {
    if (colorMap != undefined && colorMap[name] != undefined) {
        $("#scene_legend").empty();
        $("#scene_legend").append("<div class='legend_title'>" + name + "</div>");
        $.each(colorMap[name], function (key, value) {
            $("#scene_legend").append("<div class='scene_legend_color' style='background-color:" + value + "'> &nbsp</div>" + key + "<br>")
        });
    }
}

var veg_slider_values = {};
var slider_values = {};
var veg_proportion = {};
var total_input_percent;
var probabilistic_transitions_json;
var probabilistic_transitions_slider_values;
var veg_slider_values_state_class;

function setInitialConditionsSidebar(vegInitialConditions) {

    total_input_percent = 100;

    // empty the tables
    $("#vegTypeSliderTable").empty();
    $("#probabilisticTransitionSliderTable").empty();

    // Create the legend
    $("#scene_legend").empty();
    $.each(colorMap["Vegetation Types"], function(key,value){
        $("#scene_legend").append("<div id='scene_legend_color' style='background-color:" + value + "'> &nbsp</div>" + key + "<br>")
    });

    // Iterate over each of the veg types. Access the state class object for each
    $.each(vegInitialConditions["veg_sc_pct"], function (veg_type, state_class_object) {

        if (!(veg_type in vegInitialConditions.veg_sc_pct)) {
            return true;    // skips this entry
        }

        // Get the Veg ID for this veg type from the Web API current project definitions
        var veg_match = $.grep(currentProject.definitions.strata, function(e){ return e.name == veg_type; });
        var veg_id = veg_match[0].id;

        // Count the number of state classes in this veg type.
        var state_class_count = Object.keys(state_class_object).length;

        //Create a skeleton to house the intital conditions slider bar and  state class input table.
        var veg_table_id = veg_type.replace(/ /g, "_").replace(/&/g, "__");
        var management_table_id = veg_table_id + "_management";
        $("#vegTypeSliderTable").append("<tr><td>" +
            "<table class='initial_veg_cover_input_table'>" +
            "<tr><td colspan='4'>" +
            "<div class='scene_legend_color_initial_vegetation_cover' style='background-color:" + colorMap["Vegetation Types"][veg_type] +  "'></div>"+
            "<label for='amount_veg1'><div class='imageOverlayLink'>" + veg_type + " </div></label>" +
            "</td></tr>" +
            "<tr><td>" +
            "<div class='slider_bars veg_slider_bars' id='veg" + veg_id + "_slider'></div>" +
            "</td><td>" +
            "<input type='text' id='veg" + veg_id + "_label' class='current_slider_setting' readonly>" +
            "</td>" +
            "<td>" +
            "<div class='show_state_classes_link state_class_div'> <span class='state_class_span'>State Classes</span></div>" +
            "<div class='sub_slider_text_inputs' style='display:none'>" +
            "<div class='callout right '>" +
            "<table id='" + veg_id + "' class='sub_slider_table' title='" + veg_type + "'><tr><td colspan='3'><div class='state_class_header'>" + veg_type + "<img class='close_state_class' src='static/img/close.png'></div></td></tr></table>" +
            "</div></div>" +
            "</td>" +
             /*
            "<td>" +
            "<div class='manage_div'><span class='manage_span'>Manage</span></div>" +
            "<div class='management_action_inputs' style='display:none'>" +
            "<div class='manage_callout callout right'>" +
            "<table id='" + management_table_id + "' class='sub_slider_table' title='" + veg_type + "'></table>" +
            "</div>" +
            "</div>" +
            "</td>
            */
            "</tr></table>" +
            "</td></tr>"
        );

        // Set the initial slider values equal to initial conditions defined in the library (REQUIRED).
        veg_slider_values_state_class = vegInitialConditions["veg_sc_pct"];

        // Create a slider bar
        create_slider(veg_id, veg_type, state_class_count);

        // Make a row in the state class table for each state class.
        $.each(state_class_object, function (state_class, pct_cover) {

            var state_class_match = $.grep(currentProject.definitions.stateclasses, function(e){ return e.name == state_class; });
            var state_class_id = state_class_match[0].id;

            $("#" + veg_id).append("<tr><td><div class='scene_legend_color_initial_vegetation_cover' style='border-radius: 3px; background-color:" + colorMap["State Classes"][state_class] +  "'></div></td>"+
                "<td>" + state_class + " </td><td><input class='veg_state_class_entry' id='" + "veg_" + veg_id + "_" + state_class_id + "' type='text' size='2' value=" + pct_cover +  ">%</td></tr>")
        });

        /*
        var management_action_count = 1;
        // TODO: Currently hard coded. Same for each veg type. List of management actions will eventually be specific to the veg type.
        management_actions_dict[veg_type] = management_actions_list;
        $.each(management_actions_dict[veg_type], function (index, management_action) {
            $("#" + management_table_id).append("<tr><td>" + management_action + " </td><td><input class='veg_state_class_entry' id='" + "management_" + veg_iteration + "_" + state_class_count + "_manage' type='text' size='2' value='0'> Acres</td></tr>")
            management_action_count++
        });
        */

        $("#vegTypeSliderTable").append("</td></td>")

    });

    function create_slider(veg_id, veg_type, state_class_count) {
        // veg_id is currently based on the order in which the veg types occur in the vegtypeStateclassesDictionary
        // This happens to be mappable to the id in curent_project.definitions.strata. Will this always be true?

        $(function () {

            var initial_slider_value = 0;

            // Loop through all the state class pct cover values and sum them up to set the initial veg slider bar value.
            $.each(vegInitialConditions['veg_sc_pct'][veg_type], function (key, value) {
                initial_slider_value += value

            });

            veg_slider_values[veg_type] = Math.ceil(initial_slider_value);

            slider_values[veg_id] = 0;
            veg_proportion[veg_id] = 0;

            $("#veg" + veg_id + "_slider").slider({
                range: "min",
                value: initial_slider_value,
                min: 0,
                max: 100,
                step: 1,
                slide: function (event, ui) {
                    veg_slider_values[veg_type] = ui.value;
                    $("#veg" + veg_id + "_label").val(ui.value + "%");
                    $("#total_input_percent").html(total_input_percent + ui.value + "%");
                    total_percent_action(total_input_percent + ui.value);

                    // Populate state class values equally
                    veg_proportion[veg_id] = parseFloat((ui.value / state_class_count).toFixed(2));

                    $("#" + veg_id).find('input').each(function(){
                        $(this).val(veg_proportion[veg_id])
                    });

                    veg_slider_values_state_class[veg_type] = {};
                },
                start: function (event, ui) {
                    total_input_percent = total_input_percent - ui.value;
                },
                stop: function (event, ui) {
                    total_input_percent = total_input_percent + ui.value;

                    /* New Web API version */
                    // Modify the values in the initial conditions for this veg type.
                    $.each(currentScenario.config.initial_conditions_nonspatial_distributions, function(index, vegtypeStateclassObj){
                        if (vegtypeStateclassObj.stratum ==  veg_id){
                            vegtypeStateclassObj.relative_amount =  veg_proportion[veg_id];
                        }
                    });
                },
                create: function (event, ui) {
                    $("#veg" + veg_id + "_label").val($(this).slider('value') + "%");
                },
            });

        });
    }


/*********************************** Probabilistic Transitions Slider Inputs ******************************************/

    probabilistic_transitions_json = {};
    probabilistic_transitions_slider_values = {};

    $.each(currentProject.definitions.transition_groups, function(index, object){
        probabilistic_transitions_json[object.name] = 0;
    });

    var management_actions_dict = {};
    var probability_labels = {};

    probability_labels[-1] = "0% Probability";
    probability_labels[-.75] = "Very Low (-75%)";
    probability_labels[-.50] = "Low (-50%)";
    probability_labels[-.25] = "Moderately Low (-25%)";
    probability_labels[0] = "Default Probabilities";
    probability_labels[.25] = "Moderately High (+25%)";
    probability_labels[.50] = "High (+50%)";
    probability_labels[.75] = "Very High (+75%)";
    probability_labels[1] = "100% Probability";

    var probability_iteration = 1;

    $.each(probabilistic_transitions_json, function (transition_type, state_class_list) {

        //Create a skeleton to house the intital conditions slider bar and  state class input table.
        //probabilistic_transitions_table_id = transition_type.replace(/ /g, "_").replace(/&/g, "__")   // TODO - is this used?
        $("#probabilisticTransitionSliderTable").append("<tr><td><label for='amount_veg1'><span class='transition_type'>" + transition_type + ": </span></label>" +
            "<input type='text' id='probabilistic_transition" + probability_iteration + "_label' class='current_probability_slider_setting' readonly>" +
            "<div class='slider_bars probabilistic_transition_sliders' id='probabilistic_transition" + probability_iteration + "_slider'></div>" +
            "</td></tr>"
        );

        // Create a slider bar
        create_probability_slider(probability_iteration, transition_type, 0);

        $("#probabilisticTransitionSliderTable").append("</td></td>");

        probability_iteration++;

    });

    function create_probability_slider(iterator, transition_type) {

        $(function () {
            $("#probabilistic_transition" + iterator + "_slider").slider({
                range: "min",
                value: 0,
                min: -1,
                max: 1,
                step: .25,
                slide: function (event, ui) {
                    $("#probabilistic_transition" + iterator + "_label").val(probability_labels[ui.value]);
                },
                change: function (event, ui) {
                    probabilistic_transitions_slider_values[transition_type] = ui.value;
                    updateProbabilisticTransitionValues(transition_type, ui.value);
                },
            });

        });
    }

    //initializeStateClassColorMap();
    $(".current_probability_slider_setting").val("Default Probabilities");
}


// When probability sliders are adjusted  update the values in the Web API object
function  updateProbabilisticTransitionValues(transition_type, slider_value){

    // Get the transition type id associated with this slider
    var transition_type_id = $.grep(currentProject.definitions.transition_groups, function(e){ return e.name == transition_type} )[0].id;

    // Go through each of the transitions and if the transition type matches, update the value
    $.each(currentScenario.config.transitions, function(index, object){
        if (object.transition_type ==  transition_type_id){
            // updated value is the original value + the current slider value.
            this.probability = this.original_probability + slider_value
        }
    })

}

function total_percent_action(value){
    if (value == 100 ){
        $("#total_input_percent").css('background-color', '#1EBA36');
        $("#total_input_percent").css('color', 'white');
        $("#run_button").removeClass('disabled');
        $('input:submit').attr("disabled", false);
        $("#run_button").val('Run Model');
    }
    else {
        $("#total_input_percent").css('background-color','#E47369');
        $("#total_input_percent").css('color', '#444343');
        $("#run_button").addClass('disabled');
        $('input:submit').attr("disabled", true);
        $("#run_button").val('Total Percent Cover Must Equal 100%');
    }
}

/***********************************************Map and 3D Scene Controls  ********************************************/

$("#spatial_link").click(function(){
    var button = $('#spatial_button');
    if (button.hasClass('selected')) {
        button.removeClass('selected');
    } else {
        button.addClass('selected');
    }
    settings['spatial'] = button.hasClass('selected');
});

/***************************** Results selection and data download *******************************************/


function updateModelRunSelection(run) {
    var modelRunSelect = $("#model-run-select");
    modelRunSelect.unbind('change')
    modelRunSelect.empty();

    for (var modelRun in modelRunCache) {
        modelRunSelect.append([
            "<option value=" + modelRun + ">",
            currentProject.name + " (#" + (Number(modelRun) + 1) + ")",
            "</option>"
        ].join(''))
    }

    // Set value to current run
    modelRunSelect.val(run);
    modelRunSelect.on('change', function() {
        updateResultsViewer($(this).val());
    })
}

// Handle data download functionality
function downloadReport(url, filename, configuration) {
    fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json, text/plain, application/zip, */*',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'configuration': configuration})
    }).then(function(res) { return res.blob() }).then(function(blob){
        var reader = new FileReader()
        reader.addEventListener('loadend', function(e) {
            var node = document.createElement('a')
            node.setAttribute('href', e.target.result)
            node.setAttribute('download', filename)
            document.body.appendChild(node)
            node.click()
            document.body.removeChild(node)
            $('#download-data').val('Download Data & Results')
        })
        reader.readAsDataURL(blob);
    });
}

function downloadSpatialData(url, filename, ext, configuration) {
    fetch(url,  {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'configuration': configuration})
    }).then(function(res) { return res.json(); }).then(function(json) {
        if (ext == '.zip') {
            window.location = '/downloads/' + json.filename;
        } else {
            window.open('/downloads/' + json.filename, '_blank');
        }
        $('#download-data').val('Download Data & Results');
    })
}

function downloadModelResults() {

    var modelRun = modelRunCache[$("#model-run-select").val()]
    var reportInputs = [];
    for (var report in availableReports) {
        var id = report;
        var value = availableReports[report].label
        reportInputs.push("<input value='" + value + "' type='button' class='my-button download-report' id='" + report + "'>")
    }

    // TODO - add selection objects in a modal.
    var text = [
        "<div class='alertify-header'>",
        "Download Data & Results",
        "</div>",
        reportInputs.join('')
    ].join('')
    alertify.alert(text);
    $('.alertify-message').remove();    // Removes the extra div created, which we replace

    // Setup the events to respond to.
    $('.download-report').on('click', function() {
        reportToDownload = this.id;
        var reportConfig = availableReports[reportToDownload];
        var info = getCurrentInfo();
        var configuration = {
            'scenario_id': modelRun.scenario,
            'report_name': reportToDownload,
        }

        // TODO - include the probability transition percent increases & decreases as part of the report, and include them in the modelRunCache to begin with

        if (reportToDownload == 'overview') {
            // Get information about the map
            configuration['center'] = turf.center(info.extent);
            configuration['bbox'] = turf.bbox(info.extent);
            configuration['opacity'] =  Number(opacity.getContainer().children[1].value);
            configuration['basemap'] = currentBasemap;
            configuration['zoom'] = info.zoom;

            // Collect stacked area charts
            configuration['stacked_charts'] = [];
            configuration['column_charts'] = [];

            var stackedCharts = document.getElementsByClassName('stacked-chart');
            for (var i = 0; i < stackedCharts.length; i++) {
                var chart = stackedCharts[i];
                var vegtype = chart.getAttribute('vegtype');
                var svg = chart.children[0].innerHTML;
                configuration['stacked_charts'].push({
                    'svg': svg,
                    'vegtype': vegtype
                })
            }

            // Collect column charts
            var columnCharts = document.getElementsByClassName('column-chart');
            for (var i = 0; i < columnCharts.length; i++) {
                var chart = columnCharts[i];
                var vegtype = chart.getAttribute('vegtype');
                var svg = chart.children[0].innerHTML;
                configuration['column_charts'].push({
                    'svg': svg,
                    'vegtype': vegtype
                })
            }
        }

        $('#download-data').val('Downloading...');
        var filename = reportToDownload + reportConfig.ext;
        var url = reportConfig.url;
        if (url != requestSpatialDataURL && url != requestPDFDataURL) {
            downloadReport(reportConfig.url, filename, configuration);
        }
        else {
            downloadSpatialData(reportConfig.url, filename, reportConfig.ext, configuration);
        }
    })
}

/***************************** Restructure Web API Results  & Create Charts *******************************************/

var modelRunCache = [];   // Cache the results from every model run we perform on the client.
var reportCache = [];

// Process Web API Results. Restructure data, and create the charts.
function processStateClassSummaryReport(reportData) {
    var config = reportData.config;
    modelRunCache.push(reportData);
    var data = reportData["results"];
    var cache = {};  
    var iterations = config.run_control.max_iteration;
    var timesteps = config.run_control.max_timestep;
    for (var i = 1; i <= iterations; i++) {
        cache[i] = {};
        var iterationObjectList = $.grep(data, function(e){ return e.iteration == i; });
        for (var j = 0; j <= timesteps; j++){
            var timestepObjectList = $.grep(iterationObjectList, function(e){ return e.timestep == j; });
            cache[i][j] = {};
            $.each(timestepObjectList, function(index, object) {
                var strataObj = $.grep(currentProject.definitions.strata, function(e){ return e.id == object.stratum; });
                var strataName = strataObj[0].name;
                if (!(strataName in cache[i][j])) {
                    cache[i][j][strataName] = {}
                }
                var stateclassObj = $.grep(currentProject.definitions.stateclasses, function(e){ return e.id == object.stateclass; });
                var state_class_name = stateclassObj[0].name;
                cache[i][j][strataName][state_class_name] = object.proportion_of_landscape
            });
        }
    }

    reportCache.push(cache);  
}

// Change the currently visible results in the results sidebar.
function updateResultsViewer(run) {
    var cache = reportCache[run];
    update_results_table(cache, run);
    createAreaCharts(cache, run);
    createColumnCharts(cache, run);
    updateOutputLayers(run);
}


/****************************************  Results Table & Output Charts **********************************************/

// Create the Results Table
function update_results_table(cache, run) {

    $("#results_table").html([
    ].join(''));
    
    $("#results_viewer").append([
        "<div id='area_charts' class='results_charts' ></div>",
        "<div id='column_charts' class='results_charts' style='display:none'> </div>"
    ].join(''))

    // Probabilistic Transitions Row
    if (typeof probabilistic_transitions_slider_values != "undefined") {
        var sum_probabilities = 0;
        $.each(probabilistic_transitions_slider_values, function (transition_type, probability) {
            sum_probabilities += Math.abs(probability)
        });

        if (sum_probabilities != 0) {
            $("#results_table").append([
                "<tr class='probabilistic_transitions_tr'>",
                "<td class='probabilistic_transitions_th' id='probabalistic_transitions_th_" + run + "' colspan='2'>Probabilistic Transitions</td>",
                "<td class='probabilistic_transitions_values_header'>",
                "<span class='show_disturbance_probabilities_link'>",
                "<span class='show_disturbance_probabilities_link_text'>Show</span>",
                "<img class='dropdown_arrows_disturbance' src='/static/img/down_arrow.png'>",
                "</span>",
                "</td>",
                "</tr>"
            ].join(''));
            
            var sign;
            $.each(probabilistic_transitions_slider_values, function (transition_type, probability) {
                if (probability != 0) {
                    if (probability > 0) {
                        sign = "+"
                    }
                    else {
                        sign = ""
                    }
                    $("#results_table").append([
                        "<tr class='probabilistic_transitions_tr_values'>",
                        "<td class='probabilistic_transitions_values' id='probabilistic_transitions_values_" + run + "' colspan='3'>",
                        transition_type + ": " + sign + (probability * 100) + "%",
                        "</td>",
                        "</tr>"
                    ].join(''));
                }
            });
        }
        else {
            $("#results_table").append([
                "<tr class='probabilistic_transitions_tr'>",
                "<td class='probabilistic_transitions_th' id='probabalistic_transitions_th_" + run + "' colspan='2'>",
                "Probabilistic Transitions",
                "</td>",
                "<td class='probabilistic_transitions_values_header'>",
                "Defaults",
                "</td>",
                "</tr>"
            ].join(''));
        }
    }

    // Chart Type row
    $("#results_table").append([
        "<tr class='chart_type_tr'>",
        "<td class='chart_type_th' colspan='1'>Chart Type</td>",
        "<td class='unselected_td_button' id='column_chart_td_button'>Column</td>",
        "<td class='selected_td_button' id='stacked_area_chart_td_button'>Area</td>", 
        "</td>"
    ].join(''));


    var timestepText = currentScenario.config.run_control.max_timestep + " " + unitConfig[$(".model_selection").val()].timesteps

    // Chart button click functions
    $("#column_chart_td_button").click(function () {
        $(this).removeClass("unselected_td_button")
        $(this).addClass("selected_td_button")
        $("#stacked_area_chart_td_button").addClass("unselected_td_button")
        $("#stacked_area_chart_td_button").removeClass("selected_td_button")
        $(this).addClass("selected_td_button")
        $("#column_charts").show()
        //$("#iteration_tr_" + run).hide()
        $("#area_charts").hide()
        $("#veg_output_th").html("Vegetation Cover in " + timestepText)
    });

    // Chart button click functions
    $("#stacked_area_chart_td_button").click(function () {
        $(this).removeClass("unselected_td_button")
        $(this).addClass("selected_td_button")
        $("#column_chart_td_button").addClass("unselected_td_button")
        $("#column_chart_td_button").removeClass("selected_td_button")
        $("#column_charts").hide()
        //$("#iteration_tr_" + run).show()
        $("#area_charts").show()
        $("#veg_output_th").html("Vegetation Cover over " + timestepText)
    });


    // Iteration row
    // TODO - Re-evaluate how iterations are handled in the viewer.
    /*
    $("#results_table").append("<tr class='iteration_tr' id='iteration_tr_" + run + "'><td class='iteration_th' colspan='2'>Iteration to Display</td><td colspan='1'><input class='iteration_to_plot' id='iteration_to_plot_" + run + "' type='text' size='3' value=1></td></tr>");

    $("#iteration_to_plot_" + run).on('keyup', function () {
        if (this.value != '') {
            $("#area_charts_" + run).empty();
            create_area_charts(cache, run, this.value);

            // Redraw the map and show the new iteration
            outputStateClassLayers[run].options.it=parseInt(this.value);
            outputStateClassLayers[run].redraw();
        }
    });
    */

    $("#results_table").append([
        "<tr class='veg_output_tr'>",
        "<td class='veg_output_th' id='veg_output_th' colspan='3'>",
        "Vegetation Cover in " + timestepText,
        "</td>",
        "</tr>"
    ].join(''));

    // Show/Hide state class data
    $('.show_state_classes_results_link').unbind('click');
    $('.show_state_classes_results_link').click(function () {
        if ($(this).children('img').attr('src') == '/static/img/down_arrow.png') {
            $(this).children('img').attr('src', '/static/img/up_arrow.png')
        }
        else {
            $(this).children('img').attr('src', '/static/img/down_arrow.png')
        }
        $(this).closest('tr').nextUntil('tr.veg_type_percent_tr').slideToggle(0);
    });

    // Show/Hide run specific annual disturbances probabilities
    $('.show_disturbance_probabilities_link').unbind('click');
    $('.show_disturbance_probabilities_link').click(function () {
        if ($(this).children('img').attr('src') == '/static/img/down_arrow.png') {
            $(this).children('img').attr('src', '/static/img/up_arrow.png');
            $(this).children('.show_disturbance_probabilities_link_text').html('Hide')
        }
        else {
            $(this).children('img').attr('src', '/static/img/down_arrow.png');
            $(this).children('.show_disturbance_probabilities_link_text').html('Show')
        }
        $(this).closest('tr').nextUntil('tr.chart_type_tr').slideToggle(0);
    });
}

var colorMap;
var rgbString = function(color) {
    var rgb = (color.split(","))
    rgb.shift();
    return rgb.join();
}

function createColorMap(defs){
    colorMap = {
        'State Classes': {},
        'Vegetation Types': {}
    };
    $.each(defs.stateclasses, function(index, object){
        colorMap["State Classes"][object.name] = "rgb(" + rgbString(object.color) + ")";
    });
    $.each(defs.strata, function(index, object){
        colorMap["Vegetation Types"][object.name] = "rgb(" + rgbString(object.color) + ")";
    });
}
