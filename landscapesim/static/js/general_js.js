// where all the magic happens (i.e. the data store)
var available_libraries = [];
var current_library = {};
var project_url = '';
var available_projects = [];
var current_project = {};
var available_scenarios = [];
var scenario_url = '';
var current_scenario = {};
var run_model_url = '/api/jobs/run-model/';
var result_url = '';

$(document).ready(function() {

    // Top-level endpoint, get list of available libraries
    $.getJSON('/api/libraries/').done(function (res) {

        available_libraries = res.results;

        // Add each library to the library selection dropdown.
        $.each(available_libraries, function(index,library_array){
            $(".model_selection").append("<option value ='" + library_array.id + "'>" + library_array.name)
        });

        $("select").prop("selectedIndex",0);
        // Option to select the first library
        // $("select").prop("selectedIndex",1);
        // showLibraryInfo()

        $("#spatial_switch")[0].checked = true

    });

    /************************************************* Run Model  ****************************************************/
    run=0;
    iteration=1;
    timestep=1;

    // Send the scenario and initial conditions to ST-Sim.
    settings = [];
    settings["spatial"] = false;

    $('#run_button').on('click', function() {

        $.each(action_list, function(index,object){
            if (typeof object != "undefined") {
                $.each(object.timesteps, function (index, value) {
                    if (value == 1) {
                        current_scenario.config.transition_spatial_multipliers.push(
                            {
                                transition_group: object.action_id,
                                timestep: index + 1,
                                iteration: null,
                                transition_multiplier_type: null,
                                transition_multiplier_file_name: null,
                                geojson: object.geoJSON,
                            }
                        )
                    }
                });
            }
        }) ;

        $("#start_button").attr("disabled", true);
        $("#start_button").addClass('disabled');

        settings["library"] = current_library.name;
        settings["spatial"] = $("#spatial_button").hasClass('selected')

        iterations = current_scenario.config.run_control.max_iteration;
        timesteps = current_scenario.config.run_control.max_timestep;

        $(".slider_bars").slider( "option", "disabled", true );
        $('input:submit').attr("disabled", true);
        $("#run_button").addClass('disabled');
        $("#run_button").html("Running ST-Sim...<div id='results_loading'><img src='/static/img/spinner.gif'></div>");
        $("#running_st_sim").show()

        //$("#results_table").empty()

        $(".leaflet-right").css("right", "380px");

        var inputs = {
            'sid': current_scenario.sid,
            'pid': current_project.pid,
            'library_name': current_library.name,
            'config': current_scenario.config
        };

        $.post(run_model_url, {'inputs': JSON.stringify(inputs)})
            .done(function (res) {
                console.log('Job running:');
                console.log(res);

                var job = res;

                (function poll() {
                    setTimeout(function() {
                        $.getJSON(run_model_url + job.uuid).done(function (update) {
                            console.log(update);
                            if (update.status === 'success') {

                                $("#output").show();
                                result_url = update.result_scenario;

                                // Determine the reports URL
                                var url_array = result_url.split('/');
                                var base_url = url_array[2];
                                var results_model_id = url_array[url_array.length -2];
                                var reports_url = "http://" + base_url + "/api/scenarios/" + results_model_id + "/reports/";
                                var results_scenario_configuration_url = "http://" + base_url + "/api/scenarios/" + results_model_id + "/config/";

                                // Maximum of 4 model runs
                                if (run == 4) {
                                    run = 1;
                                }
                                else {
                                    run += 1;
                                }

                                // Get the list of reports
                                $.getJSON(reports_url).done(function (res) {

                                    // Get the state class summary report url
                                    stateclass_summary_report_url = res['stateclass_summary_report'];

                                    $("#results_loading").empty();
                                    // Get the output data
                                    $.getJSON(stateclass_summary_report_url).done(function (res) {
                                        // Restructure the results to create the results_data_json object.
                                        results_scenario_report =  res

                                        processStateClassSummaryReport(results_scenario_report);

                                    });

                                });

                                // Get the result scenario object for output services
                                $.getJSON(results_scenario_configuration_url).done(function (res) {

                                    results_scenario_configuration =  res;
                                    loadOutputLayers(results_scenario_configuration, run);

                                    $("#model_results_header").click();
                                });


                                $("#run_button").html('Run Model');
                                $("#run_button").removeClass('disabled');
                                $('input:submit').attr("disabled", false);
                                $(".slider_bars").slider( "option", "disabled", false );
                                $("#button_container").attr("disabled", false);
                                $("#running_st_sim").removeClass("full_border_radius");

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
                    }, 5000)
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
        var library_info = library_config[$(".model_selection").val()];
        var extent = library_info.extent;

        // Create a layer from the extent
        var bounding_box = [{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                [extent[0][1],extent[1][0]],
                [extent[1][1], extent[1][0]],
                [extent[1][1], extent[0][0]],
                [extent[0][1], extent[0][0]]
                ]]
            }
        }];

        // Show the layer
        bounding_box_layer = L.geoJSON(bounding_box).addTo(map);
        bounding_box_layer.bindPopup(library_info.name + " Extent").openPopup();

        // Upate the values in the library_info table
        $("#library_author").html(library_info.author);
        $("#library_date").html(library_info.date);
        $("#library_description").html(library_info.description);

    };

    /********************************************** Load Library (Start) **********************************************/

    $("#start_button").on("click", function(){

        $("#welcome_header").addClass("full_border_radius");
        $("#library_header").addClass("full_border_radius");

        current_library = $.grep(available_libraries, function(e) {return e.id == $(".model_selection").val()})[0];
        available_projects = current_library.projects;
        project_url = available_projects[0];

        // Get Stuff from the Web API
        $.getJSON(project_url).done(function (project) {
            console.log("current_project ->");
            console.log(project);
            current_project = project;
            available_scenarios = current_project.scenarios;

            // Get project definitions
            $.getJSON(project_url + 'definitions').done(function (definitions) {
                console.log("current_project.definitions ->");
                console.log(definitions);
                current_project.definitions = definitions;
                createColorMap(current_project.definitions)
            });

            // Select scenario from list; here we are just taking the top one
            scenario_url = available_scenarios[0];

            // Get scenario information
            $.getJSON(scenario_url).done(function (scenario) {
                console.log("current_scenario ->");
                console.log(scenario);
                current_scenario = scenario;


                // Scenario configuration (at import)
                $.getJSON(scenario_url + 'config').done(function (config) {
                    console.log("current_scenario.config->")
                    console.log(config);
                    current_scenario.config = config;

                    // Spatial by default:
                    setSpatialOutputOptions(true);

                    // Store the original transition values to reference when adjusting probabilistic transition sliders.
                    $.each(current_scenario.config.transitions, function(index, object){
                        object.original_probability = object.probability;
                    });

                    // Create objects from Web API data
                    veg_initial_conditions = createVegInitialConditionsDict();
                    createVegTypeStateClassesJSON(veg_initial_conditions);

                    // Set Initial Conditions (Veg sliders & Probabilistic Transitions)
                    setInitialConditionsSidebar(veg_initial_conditions);

                    loadLayers(current_scenario.config.scenario_input_services);

                    $(".veg_slider_bars").slider("disable");
                    $(".veg_slider_bars").addClass("disabled");
                    $(".veg_state_class_entry").addClass("disabled");
                    $(".veg_state_class_entry").prop("disabled", true);

                    $("#settings_timesteps").val(current_scenario.config.run_control.max_timestep)
                })

            });

            //map.fitBounds(bounding_box_layer.getBounds(),{"paddingTopLeft":[0,1]});
            map.fitBounds(bounding_box_layer.getBounds());
            map.removeLayer(bounding_box_layer);

            // Collapse the Welcome and Library divs.

            $("#welcome_header").siblings(".collapsible_div").slideUp(400, function(){});
            $("#library_header").siblings(".collapsible_div").slideUp(400, function(){});

            $("#welcome_header").children(".collapse_icon").addClass("rotate90");
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

            library_selected = true


        })

    });

    /********************************************* General UI Functions ***********************************************/

    // Collapse div on header click
    $(document).on("click", ".header", function () {

            // Get this collapsible div
            var this_collapsible_div = $(this).siblings(".collapsible_div");

            // If a library has been loaded, collapse other divs on header click.
            if (typeof library_selected != "undefined" && library_selected == true){
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
            if ($(this).siblings(element).is(":visible")) {
                $(this).siblings(element).hide();
                map.removeLayer(inputStateClassLayer);
            }
            else {
                $(".sub_slider_text_inputs").hide();
                $(this).siblings(element).show();
                inputStateClassLayer.addTo(map);

            }
        });
    }

    delegatedPopupContext('.show_state_classes_link', '.sub_slider_text_inputs');
    delegatedPopupContext('.manage_div', '.management_action_inputs');


    $(".tab_container").on("click", function(){

        this_tab_run = $(this).attr('run')

        changeOutputStateClass(this_tab_run);

    });



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

        current_scenario.config.run_control.is_spatial = setting;
        current_scenario.config.output_options.raster_sc = setting;

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

        current_scenario.config.output_options.raster_sc_t = raster_frequency;

        /* Taylor's suggestion for temporarily fixing the 20 timestep error */
        current_scenario.config.output_options.raster_tr = false;
        current_scenario.config.output_options.raster_tr_t = -1;

        /* Other setting don't currently work

        $.each(current_scenario.config.output_options, function (key, value) {

            if (key.indexOf("raster") > -1) {

                if ((key).split("_").pop() == "t") {
                    current_scenario.config.output_options[key] = timesteps;
                }
                else {
                    current_scenario.config.output_options[key] = setting;
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
        //total_input_percent=total_input_percent - veg_slider_values[veg_type]
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

        $.each(current_scenario.config.initial_conditions_nonspatial_distributions, function (index, veg_type_state_class_object) {
            if (veg_type_state_class_object.stratum == parseInt(veg_type_id) && veg_type_state_class_object.stateclass == parseInt(state_class_id)) {
                veg_type_state_class_object.relative_amount = state_class_value;
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

         /* Old Version */
        // On keyup, go through each state class in the given veg type and add the values in each text entry field to the veg_slider_values_state_class dictionary
        /*
        $.each(veg_type_state_classes_json[veg_type],function(index, state_class){
            var veg_state_class_id=index+1
            var veg_state_class_value=$("#veg_"+veg_type_id+"_"+veg_state_class_id).val()
            if (veg_state_class_value == ''){
                veg_state_class_value = 0;
            }
            veg_state_class_value_totals+=parseFloat(veg_state_class_value)
            veg_slider_values_state_class[veg_type][state_class]=veg_state_class_value

        });
        */

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
        $("#climate_future_disabled").hide();
        $("#climate_future_precip_slider").slider("value",0);
        $("#climate_future_temp_slider").slider("value",0);
        $("#climate_future_precip_label").val(climate_future_precip_labels[1]);
        $("#climate_future_temp_label").val(climate_future_temp_labels[0]);
        temp_previous_value=0;
        precip_previous_value=0;
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

        current_scenario.config.run_control.max_timestep = parseInt($(this).val())
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
        current_scenario.config.run_control.max_iteration = parseInt($(this).val());
    });

});

/***************************************** Create objects from Web API ************************************************/

// Takes the data returned from the web api and restructure it to create the the objects below
// which are then used to create the sliders
// veg_initial_conditions
// veg_type_state_classes_json

function createVegInitialConditionsDict(){

   // current_proejct.definitions can be slow to initialize. Keep trying until it's defined.

   if (typeof current_project.definitions != "undefined") {

       var veg_initial_conditions = {};
       veg_initial_conditions["veg_sc_pct"] = {};

       $.each(current_scenario.config.initial_conditions_nonspatial_distributions, function (index, object) {
           var strata_object = $.grep(current_project.definitions.strata, function (e) {
               return e.id == object.stratum;
           });
           var strata_name = strata_object[0].name;
           if (!(strata_name in veg_initial_conditions["veg_sc_pct"])) {
               veg_initial_conditions["veg_sc_pct"][strata_name] = {};
           }

           var state_class_object = $.grep(current_project.definitions.stateclasses, function (e) {
               return e.id == object.stateclass;
           });
           var state_class_name = state_class_object[0].name;
           if (object.relative_amount != 0) {
               veg_initial_conditions["veg_sc_pct"][strata_name][state_class_name] = object.relative_amount
           }
       });

       return veg_initial_conditions

   } else {

       setTimeout(createVegInitialConditionsDict,250);
   }
}


function createVegTypeStateClassesJSON(veg_initial_conditions){
    veg_type_state_classes_json = {};

    $.each(veg_initial_conditions["veg_sc_pct"], function(veg_type,state_class_object){
        var count=0;
        veg_type_state_classes_json[veg_type] = [];
        $.each(state_class_object, function(state_class, relative_amount){
            veg_type_state_classes_json[veg_type][count] = state_class;
            count+=1;
        });

    });

}

/*************************************** Initial Vegetation Cover Inputs **********************************************/

var veg_slider_values = {};
var slider_values = {};
var veg_proportion = {};

function setInitialConditionsSidebar(veg_initial_conditions) {

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
    $.each(veg_initial_conditions["veg_sc_pct"], function (veg_type, state_class_object) {

        if (!(veg_type in veg_initial_conditions.veg_sc_pct)) {
            return true;    // skips this entry
        }

        // Get the Veg ID for this veg type from the Web API current project definitions
        var veg_match = $.grep(current_project.definitions.strata, function(e){ return e.name == veg_type; });
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
        veg_slider_values_state_class = veg_initial_conditions["veg_sc_pct"];

        // Create a slider bar
        create_slider(veg_id, veg_type, state_class_count);

        // Make a row in the state class table for each state class.
        $.each(state_class_object, function (state_class, pct_cover) {

            var state_class_match = $.grep(current_project.definitions.stateclasses, function(e){ return e.name == state_class; });
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
        // veg_id is currently based on the order in which the veg types occur in the veg_type_state_classes_json
        // This happens to be mappable to the id in curent_project.definitions.strata. Will this always be true?

        $(function () {

            var initial_slider_value = 0;

            // Loop through all the state class pct cover values and sum them up to set the initial veg slider bar value.
            $.each(veg_initial_conditions['veg_sc_pct'][veg_type], function (key, value) {
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
                    $.each(current_scenario.config.initial_conditions_nonspatial_distributions, function(index, veg_type_state_class_object){
                        if (veg_type_state_class_object.stratum ==  veg_id){
                            veg_type_state_class_object.relative_amount =  veg_proportion[veg_id];
                        }
                    });

                    /* Old Version */
                    // Modify the values in the veg_slideravalues_state_class
                    /*
                    $.each(veg_type_state_classes_json[veg_type], function (index, state_class) {
                        veg_slider_values_state_class[veg_type][state_class] = veg_proportion[veg_id];

                    })
                    */
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

    $.each(current_project.definitions.transition_groups, function(index, object){
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
                    $("#climate_future_disabled").show()
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
    var transition_type_id = $.grep(current_project.definitions.transition_groups, function(e){ return e.name == transition_type} )[0].id;

    // Go through each of the transitions and if the transition type matches, update the value
    $.each(current_scenario.config.transitions, function(index, object){
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

function activate_map() {
    $("#map_button").addClass("selected");
    $("#scene_button").removeClass("selected");
    $("#map").show();
    $("#scene").hide();
    $("#selected_features").hide();
    //window.removeEventListener('resize', landscape_viewer.resize, false);
    $("#scene_legend").hide();
    $("#general_settings_instructions").html("Select an area of interest by clicking on a reporting unit (e.g., a watershed), or by using the rectangle tool to define your own area of interest.");
    $("div.leaflet-control-layers:nth-child(1)").css("top","55px")
}

function activate_scene(){
    $("#map_button").removeClass("selected");
    $("#scene_button").addClass("selected");
    $("#scene").show();
    $("#map").hide();
    $("#step1").hide();
    $("#selected_features").show();
    //window.addEventListener('resize', landscape_viewer.resize, false);
    //landscape_viewer.resize();
    $("#scene_legend").show();
    $("#general_settings_instructions").html("Now use the controls below to define the scenario you'd like to simulate. When you are ready, push the Run Model button to conduct a model run.");
}

$("#spatial_link").click(function(){
    var button = $('#spatial_button');
    if (button.hasClass('selected')) {
        button.removeClass('selected');
    } else {
        button.addClass('selected');
    }
    settings['spatial'] = button.hasClass('selected');
});

function hideSceneLoadingDiv() {
    $('#scene_loading_div').hide();
}

function showSceneLoadingDiv() {
    $('#scene_loading_div').show();
}

/***************************** Restructure Web API Results  & Create Charts *******************************************/

// Process Web API Results. Restructure data, and create the charts.
function processStateClassSummaryReport(res){

    var data = res["results"];
    results_data_json={};

    for (var i=1; i <= iterations; i++ ){

        results_data_json[i]={};
        this_iteration_object_list = $.grep(data, function(e){ return e.iteration == i; });

        for (var j=0; j <= timesteps ; j++){

            this_timestep_object_list = $.grep(this_iteration_object_list, function(e){ return e.timestep == j; });


            results_data_json[i][j]={};

            $.each(this_timestep_object_list, function(index, object){

                var strata_object = $.grep(current_project.definitions.strata, function(e){ return e.id == object.stratum; });
                var strata_name = strata_object[0].name;
                if (! (strata_name in results_data_json[i][j]) ) {
                    results_data_json[i][j][strata_name] = {}
                }
                var state_class_object = $.grep(current_project.definitions.stateclasses, function(e){ return e.id == object.stateclass; });
                var state_class_name = state_class_object[0].name;
                results_data_json[i][j][strata_name][state_class_name] = object.proportion_of_landscape

            });

        }

    }

    update_results_table(run);
    create_area_charts(results_data_json, run, iteration);
    create_column_charts(results_data_json, run, iteration);
}

/****************************************  Results Table & Output Charts **********************************************/

// Create the Results Table
//function update_results_table(timestep,run) { // see TODO below
function update_results_table(run) {

    $("#results_table_" + run).html("<tr class='location_tr'><td class='location_th' colspan='1'>Library</td><td colspan='2'>" + current_library.name + "</td></tr>");

    $("#view" + run).append("<table id='selected_location_table_" + run + "' class='selected_location_table' ><tr></tr></table> <div id='area_charts_" + run + "' class='area_charts' ></div><div id='column_charts_" + run + "' class='column_charts' style='display:none'> </div>")

    // Probabilistic Transitions Row
    if (typeof probabilistic_transitions_slider_values != "undefined") {
        var sum_probabilities = 0;

        $.each(probabilistic_transitions_slider_values, function (transition_type, probability) {
            sum_probabilities += Math.abs(probability)
        });

        if (sum_probabilities != 0) {

            $("#results_table_" + run).append("<tr class='probabilistic_transitions_tr'><td class='probabilistic_transitions_th' id='probabalistic_transitions_th_" + run + "' colspan='2'>Probabilistic Transitions</td><td class='probabilistic_transitions_values_header'> <span class='show_disturbance_probabilities_link'> <span class='show_disturbance_probabilities_link_text'>Show</span> <img class='dropdown_arrows_disturbance' src='/static/img/down_arrow.png'></span></td></tr>");
            var sign;
            $.each(probabilistic_transitions_slider_values, function (transition_type, probability) {
                if (probability != 0) {

                    if (probability > 0) {
                        sign = "+"
                    }
                    else {
                        sign = ""
                    }
                    $("#results_table_" + run).append("<tr class='probabilistic_transitions_tr_values'><td class='probabilistic_transitions_values' id='probabilistic_transitions_values_" + run + "' colspan='3'>" + transition_type + ": " + sign + (probability * 100) + "%</td></tr>");

                }
            });
        }
        else {
            $("#results_table_" + run).append("<tr class='probabilistic_transitions_tr'><td class='probabilistic_transitions_th' id='probabalistic_transitions_th_" + run + "' colspan='2'>Disturbance Probabilities</td><td class='probabilistic_transitions_values_header'>Defaults</td></tr>");
        }
    }

    // Chart Type row
    $("#results_table_" + run).append("<tr class='chart_type_tr'>" +
        "<td class='chart_type_th' colspan='1'>Chart Type</td>" +
        "<td class='unselected_td_button' id='column_chart_td_button_" + run + "'>Column</td>" +
        "<td class='selected_td_button' id='stacked_area_chart_td_button_" + run + "'>Area</td>" +
        "</td>");


    // Chart button click functions
    $("#column_chart_td_button_" + run).click(function () {
        $(this).removeClass("unselected_td_button")
        $(this).addClass("selected_td_button")
        $("#stacked_area_chart_td_button_" + run).addClass("unselected_td_button")
        $("#stacked_area_chart_td_button_" + run).removeClass("selected_td_button")
        $(this).addClass("selected_td_button")
        $("#column_charts_" + run).show()
        $("#iteration_tr_" + run).hide()
        $("#area_charts_" + run).hide()
        $("#veg_output_th_" + run).html("Vegetation Cover in " + current_scenario.config.run_control.max_timestep + " Years")
    });

    // Chart button click functions
    $("#stacked_area_chart_td_button_" + run).click(function () {
        $(this).removeClass("unselected_td_button")
        $(this).addClass("selected_td_button")
        $("#column_chart_td_button_" + run).addClass("unselected_td_button")
        $("#column_chart_td_button_" + run).removeClass("selected_td_button")
        $("#column_charts_" + run).hide()
        $("#iteration_tr_" + run).show()
        $("#area_charts_" + run).show()
        $("#veg_output_th_" + run).html("Vegetation Cover over " + current_scenario.config.run_control.max_timestep + " Years")
    });


    // Iteration row
    $("#results_table_" + run).append("<tr class='iteration_tr' id='iteration_tr_" + run + "'><td class='iteration_th' colspan='2'>Iteration to Display</td><td colspan='1'><input class='iteration_to_plot' id='iteration_to_plot_" + run + "' type='text' size='3' value=1></td></tr>");

    $("#iteration_to_plot_" + run).on('keyup', function () {
        if (this.value != '') {
            $("#area_charts_" + run).empty();
            create_area_charts(results_data_json, run, this.value);

            // Redraw the map and show the new iteration
            outputStateClassLayers[run].options.it=parseInt(this.value);
            outputStateClassLayers[run].redraw();
        }
    });

    // Create a list of all the veg types and create a sorted list.
    var veg_type_list = new Array()
    $.each(results_data_json[iteration][timestep], function (key, value) {
        veg_type_list.push(key)
    });

    var sorted_veg_type_list = veg_type_list.sort();
    $("#running_st_sim").html("ST-Sim Model Results <img class='collapse_icon' src='/static/img/collapse_down_arrow.png' >");

    $("#results_table_" + run).append("<tr class='veg_output_tr'><td class='veg_output_th' id='veg_output_th_" + run + "' colspan='3'>Vegetation Cover in " + settings["timesteps"] + " Years</td></tr>");
    // Go through each sorted veg_type
    $.each(sorted_veg_type_list, function (index, value) {

        var veg_type = value;

        // Write veg type and % headers
        $("#results_table").html("<tr class='veg_type_percent_tr'><td class='veg_type_th' colspan='3'>" + value +
            "<span class='show_state_classes_results_link'> <img class='dropdown_arrows' src='/static/img/down_arrow.png'></span>" +
            "</td></tr>");

        // Create a list of all the state classes and create a sorted list.
        var state_list = new Array();
        $.each(results_data_json[iteration][timestep][value], function (key, value) {
            state_list.push(key)
        });

        var sorted_state_list = state_list.sort();

        // Go through each sorted state class within the veg_type in this loop and write out the values
        $.each(sorted_state_list, function (index, value) {
            $("results_table").find("tr:gt(0)").remove();
            $('#results_table').append('<tr class="state_class_tr"><td>' + value + '</td><td>' + (results_data_json[iteration][timestep][veg_type][value] * 100).toFixed(1) + '%</td></tr>');
        });

    });

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

function createColorMap(project_definitions){

    colorMap={};
    colorMap["State Classes"]={};
    colorMap["Vegetation Types"]={};
    state_class_color_map={};
    veg_type_color_map={};

    $.each(project_definitions.stateclasses, function(index,object){
        var rgb = (object.color).split(",");
        rgb.shift();
        var rgb_string = rgb.join();
        colorMap["State Classes"][object.name] = "rgb(" + rgb_string + ")";

    });

    $.each(project_definitions.strata, function(index,object){
        var rgb = (object.color).split(",");
        rgb.shift();
        var rgb_string = rgb.join();
        colorMap["Vegetation Types"][object.name] = "rgb(" + rgb_string + ")";

    });

}


