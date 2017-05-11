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
    $('#run_button').on('click', function() {

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

                job = res;

                (function poll() {
                    setTimeout(function() {
                        $.getJSON(run_model_url + job.uuid).done(function (update) {
                            test=update
                            console.log(update);
                            if (update.status === 'success') {
                                result_url = update.result_scenario;
                                alert('Model run complete!')
                            } else if (update.status === 'failure') {
                                alert('Something has gone terribly, terribly wrong...')
                            } else {
                                poll();
                            }
                        })
                    }, 5000)
                })();

            })
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
    //$(".veg_state_class_entry").keyup(function(){
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
                var max_height = $(window).height() - this_div_position - 100
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


