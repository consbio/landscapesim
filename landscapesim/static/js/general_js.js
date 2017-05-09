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

                var job = res;

                (function poll() {
                    setTimeout(function() {
                        $.getJSON(run_model_url + job.uuid).done(function (update) {
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

    $(".model_selection").on("change", function(){

        $("#welcome").hide();
        $("#inputs").show();

        current_library = available_libraries[$(this).val()];
        available_projects = current_library.projects;
        project_url = available_projects[0];

        $.getJSON(project_url).done(function (project) {
            console.log(project);
            current_project = project;
            available_scenarios = current_project.scenarios;

            // Get project definitions
            $.getJSON(project_url + 'definitions').done(function (definitions) {
                console.log(definitions);
                current_project.definitions = definitions;
            });

            // Select scenario from list; here we are just taking the top one
            scenario_url = available_scenarios[0];

            // Get scenario information
            $.getJSON(scenario_url).done(function (scenario) {
                console.log(scenario);
                current_scenario = scenario;

                // Scenario configuration (at import)
                $.getJSON(scenario_url + 'config').done(function (config) {
                    console.log(config);
                    current_scenario.config = config;
                    current_scenario.config.output_options.raster_tr=false;
                    current_scenario.config.output_options.raster_tr_t=-1;
                })

            });
        })
    });

});





