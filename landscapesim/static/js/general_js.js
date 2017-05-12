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
            $(".model_selection").append("<option value ='" + index + "'>" + library_array.name)
        });
        $("select").prop("selectedIndex",0);

    });

    /******************************************* Run Model Button Functions *******************************************/
    run=0;
    iteration=1;
    timestep=1;

    // Send the scenario and initial conditions to ST-Sim.
    settings=[];
    settings["spatial"]=false;
    feature_id = current_library.name;

    $('#run_button').on('click', function() {

        settings["library"]= current_library.name;
        settings["timesteps"]= $("#settings_timesteps").val();
        settings["iterations"]= $("#settings_iterations").val();
        settings["spatial"]= $("#spatial_button").hasClass('selected')

        iterations = settings["iterations"];
        timesteps = settings["timesteps"]

        $(".slider_bars").slider( "option", "disabled", true );
        $('input:submit').attr("disabled", true);
        $("#run_button").addClass('disabled');
        $("#run_button").val('Please Wait...');
        $("#run_button").addClass('please_wait');
        $("#running_st_sim").show()

        //$("#results_table").empty()
        $("#output").show();
        $("#running_st_sim").html("Running ST-Sim...");
        $("#results_loading").html("<img src='/static/img/spinner.gif'>")

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
                                result_url = update.result_scenario;

                                // Determine the reports URL
                                var url_array = result_url.split('/');
                                var base_url = url_array[2];
                                var results_model_id = url_array[url_array.length -2];
                                reports_url = "http://" + base_url + "/api/scenarios/" + results_model_id + "/reports/";

                                // Get the list of reports
                                $.getJSON(reports_url).done(function (res) {

                                    // Get the state class summary report url
                                    stateclass_summary_report_url = res['stateclass_summary_report'];

                                    $("#results_loading").empty();
                                    $("#column_charts_" + run).empty();
                                    $("#area_charts_" + run).empty();

                                    // Get the output data
                                    $.getJSON(stateclass_summary_report_url).done(function (res) {
                                        // Restructure the results to create the results_data_json object.
                                        processStateClassSummaryReport(res);
                                    });

                                    // Maximum of 4 model runs
                                    if (run == 4) {
                                        run = 1;
                                    }
                                    else {
                                        run += 1;
                                    }
                                    $("#tab_container").css("display", "block");

                                });

                                $("#run_button").val('Run Model');
                                $("#run_button").removeClass('disabled');
                                $("#run_button").removeClass('please_wait');
                                $('input:submit').attr("disabled", false);
                                $('#button_container').attr("disabled", false);


                            } else if (update.status === 'failure') {
                                alert('An error occurred. Please try again.')

                                $("#run_button").val('Run Model');
                                $("#run_button").removeClass('disabled');
                                $("#run_button").removeClass('please_wait');
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

    /********************************************** Change Model Functions ********************************************/
    $(".model_selection").on("change", function(){

        var collapsible_div = $("#welcome_header").siblings(".collapsible_div");
        collapsible_div.slideToggle(400, function(){});

        var collapse_icon = $("#welcome_header").children(".collapse_icon");
        toggleIcon(collapse_icon)

        $("#inputs").show();

        current_library = available_libraries[$(this).val()];
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
                    current_scenario.config.output_options.raster_tr=false;
                    current_scenario.config.output_options.raster_tr_t=-1;

                    // Create objects from Web API data
                    createVegInitialConditionsDict();
                    createVegTypeStateClassesJSON(veg_initial_conditions);

                    // Set Initial Conditions (Veg sliders & Probabilistic Transitions)
                    setInitialConditionsSidebar(veg_initial_conditions)
                })

            });
        })

    });

    /**************************************General Initialization Functions *******************************************/

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
                $(this).siblings(element).hide()
            }
            else {
                $(this).siblings(element).show()
            }
        });
    }

    delegatedPopupContext('.show_state_classes_link', '.sub_slider_text_inputs');
    delegatedPopupContext('.manage_div', '.management_action_inputs');

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


});

/***************************************** Create objects from Web API ************************************************/

// Creates two objects used to create the sliders
//  veg_initial_conditions
//  veg_type_state_classes_json

function createVegInitialConditionsDict(){

    veg_initial_conditions = {};
    veg_initial_conditions["veg_sc_pct"] = {};

    $.each(current_scenario.config.initial_conditions_nonspatial_distributions, function(index, object){
        var strata_object = $.grep(current_project.definitions.strata, function(e){ return e.id == object.stratum; });
        var strata_name = strata_object[0].name;
        if (! (strata_name in veg_initial_conditions["veg_sc_pct"])){
            veg_initial_conditions["veg_sc_pct"][strata_name] = {};
        }

        var state_class_object = $.grep(current_project.definitions.stateclasses, function(e){ return e.id == object.stateclass; });
        var state_class_name = state_class_object[0].name;
        if (object.relative_amount != 0 ) {
            veg_initial_conditions["veg_sc_pct"][strata_name][state_class_name] = object.relative_amount
        }
    });
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
            "<label for='amount_veg1'><div class='imageOverlayLink'>" + veg_type + " </div></label>" +
            "</td></tr>" +
            "<tr><td>" +
            "<div class='slider_bars' id='veg" + veg_id + "_slider'></div>" +
            "</td><td>" +
            "<input type='text' id='veg" + veg_id + "_label' class='current_slider_setting' readonly>" +
            "</td>" +
            "<td>" +
            "<div class='show_state_classes_link state_class_div'> <span class='state_class_span'>State Classes</span></div>" +
            "<div class='sub_slider_text_inputs' style='display:none'>" +
            "<div class='callout right '>" +
            "<table id='" + veg_id + "' class='sub_slider_table' title='" + veg_type + "'><tr><td colspan='2'><div class='state_class_header'>" + veg_type + "<img class='close_state_class' src='static/img/close.png'></div></td></tr></table>" +
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

            $("#" + veg_id).append("<tr><td>" + state_class + " </td><td><input class='veg_state_class_entry' id='" + "veg_" + veg_id + "_" + state_class_id + "' type='text' size='2' value=" + pct_cover +  ">%</td></tr>")
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
                    // Modify the values in the veg_slider_values_state_class
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
                    probabilistic_transitions_slider_values[transition_type] = ui.value
                },
            });

        });
    }

    //initializeStateClassColorMap();
    $(".current_probability_slider_setting").val("Default Probabilities");
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
    window.removeEventListener('resize', landscape_viewer.resize, false);
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
    window.addEventListener('resize', landscape_viewer.resize, false);
    landscape_viewer.resize();
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

/*********************************************** Other Functions ******************************************************/

$(document).on('change', '#settings_library', function() {
    var newLibraryName = $(this).val();
    $.getJSON(newLibraryName + '/info/').done(function(definitions) {
        setLibrary(newLibraryName, definitions);
        if (definitions.has_predefined_extent) {
            feature_id = newLibraryName;
        }
    })
});

$(document).ready(function () {
    $(".header").click(function () {
        var collapsible_div = $(this).siblings(".collapsible_div");
        collapsible_div.slideToggle(400, function(){
            // Go through each collapsible div and calculate the max-height based on
            $.each($(".collapsible_div"), function(){
                var this_div_position = $(this).offset().top;
                var max_height = $(window).height() - this_div_position - 100;
                $(this).addClass('transition_ease');
                $(this).css('max-height',max_height);
                $(this).removeClass('transition_ease')

            });
        });

        collapse_icon = $(this).children(".collapse_icon");
        toggleIcon(collapse_icon)

    });
});

$(document).on("click", ".close_state_class", function(){
    $(this).parents(".sub_slider_text_inputs").hide()
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


function processStateClassSummaryReport(res){

    data = res["results"];
    results_data_json={};

    for (var i=1; i <= iterations; i++ ){

        results_data_json[i]={};
        this_iteration_object_list = $.grep(data, function(e){ return e.iteration == i; });

        for (var j=1; j <= timesteps; j++){

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
    //create_column_charts(results_data_json, run, iteration)
    $("#view" + run + "_link").click();
}

/****************************************  Results Table & Output Charts **********************************************/

//function update_results_table(timestep,run) { // see TODO below
function update_results_table(run) {
    console.log(1)
    // Create the Results Table
    $("#results_table_" + run).html("<tr class='location_tr'><td class='location_th' colspan='1'>Location </td><td colspan='2'>" + feature_id + "</td></tr>");
    console.log(2)

    $("#view" + run).append("<table id='selected_location_table_" + run + "' class='selected_location_table' ><tr></tr></table> <div id='area_charts_" + run + "' class='area_charts' style='display:none'></div><div id='column_charts_" + run + "' class='column_charts'> </div>")

    console.log(3)
    // Probabilistic Transitions Row
    if (typeof probabilistic_transitions_slider_values != "undefined") {
        var sum_probabilities = 0

        $.each(probabilistic_transitions_slider_values, function (transition_type, probability) {
            sum_probabilities += Math.abs(probability)
        });
        console.log(4)

        if (sum_probabilities != 0) {

            $("#results_table_" + run).append("<tr class='probabilistic_transitions_tr'><td class='probabilistic_transitions_th' id='probabalistic_transitions_th_" + run + "' colspan='2'>Disturbance Probabilities</td><td class='probabilistic_transitions_values_header'> <span class='show_disturbance_probabilities_link'> <span class='show_disturbance_probabilities_link_text'>Show</span> <img class='dropdown_arrows_disturbance' src='/static/img/down_arrow.png'></span></td></tr>");
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
    console.log(5)

    // Chart Type row
    $("#results_table_" + run).append("<tr class='chart_type_tr'>" +
        "<td class='chart_type_th' colspan='1'>Chart Type</td>" +
        "<td class='selected_td_button' id='column_chart_td_button_" + run + "'>Column</td>" +
        "<td class='unselected_td_button' id='stacked_area_chart_td_button_" + run + "'>Area</td>" +
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
        $("#veg_output_th_" + run).html("Vegetation Cover in " + settings["timesteps"] + " Years")
    });

    console.log(6)


    // Chart button click functions
    $("#stacked_area_chart_td_button_" + run).click(function () {
        $(this).removeClass("unselected_td_button")
        $(this).addClass("selected_td_button")
        $("#column_chart_td_button_" + run).addClass("unselected_td_button")
        $("#column_chart_td_button_" + run).removeClass("selected_td_button")
        $("#column_charts_" + run).hide()
        $("#iteration_tr_" + run).show()
        $("#area_charts_" + run).show()
        $("#veg_output_th_" + run).html("Vegetation Cover across " + settings["timesteps"] + " Years")
    });


    // Iteration row
    $("#results_table_" + run).append("<tr class='iteration_tr' id='iteration_tr_" + run + "'><td class='iteration_th' colspan='2'>Iteration to Display</td><td colspan='1'><input class='iteration_to_plot' id='iteration_to_plot_" + run + "' type='text' size='3' value=1></td></tr>");

    $("#iteration_to_plot_" + run).on('keyup', function () {
        if (this.value != '') {
            $("#area_charts_" + run).empty()
            create_area_charts(results_data_json, run, this.value)
        }
    });

    // Create a list of all the veg types and create a sorted list.
    var veg_type_list = new Array()
    $.each(results_data_json[iteration][timestep], function (key, value) {
        veg_type_list.push(key)
    });
    console.log(7)

    var sorted_veg_type_list = veg_type_list.sort()

    $("#running_st_sim").html("ST-Sim Model Results")

    $("#results_table_" + run).append("<tr class='veg_output_tr'><td class='veg_output_th' id='veg_output_th_" + run + "' colspan='3'>Vegetation Cover in " + settings["timesteps"] + " Years</td></tr>");
    // Go through each sorted veg_type
    $.each(sorted_veg_type_list, function (index, value) {

        console.log(8)

        var veg_type = value

        // Write veg type and % headers
        $("#results_table").html("<tr class='veg_type_percent_tr'><td class='veg_type_th' colspan='3'>" + value +
            "<span class='show_state_classes_results_link'> <img class='dropdown_arrows' src='/static/img/down_arrow.png'></span>" +
            "</td></tr>");

        // Create a list of all the state classes and create a sorted list.
        var state_list = new Array()
        $.each(results_data_json[iteration][timestep][value], function (key, value) {
            state_list.push(key)
        })

        var sorted_state_list = state_list.sort()

        // Go through each sorted state class within the veg_type in this loop and write out the values
        $.each(sorted_state_list, function (index, value) {
            $("results_table").find("tr:gt(0)").remove();
            $('#results_table').append('<tr class="state_class_tr"><td>' + value + '</td><td>' + (results_data_json[iteration][timestep][veg_type][value] * 100).toFixed(1) + '%</td></tr>');
        });

    });

    console.log(9)

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

    console.log(10)

    // Show/Hide run specific annual disturbances probabilities
    $('.show_disturbance_probabilities_link').unbind('click');
    $('.show_disturbance_probabilities_link').click(function () {

        if ($(this).children('img').attr('src') == '/static/img/down_arrow.png') {

            $(this).children('img').attr('src', '/static/img/up_arrow.png')
            $(this).children('.show_disturbance_probabilities_link_text').html('Hide')

        }
        else {
            $(this).children('img').attr('src', '/static/img/down_arrow.png')
            $(this).children('.show_disturbance_probabilities_link_text').html('Show')
        }
        $(this).closest('tr').nextUntil('tr.chart_type_tr').slideToggle(0);
    });
}



