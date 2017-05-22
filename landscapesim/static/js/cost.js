function openCostTable(){
    var count_transition_groups = current_project.definitions.transition_groups.length;

    var cost_table_html = "<div id='cost_table_div'><table id='cost_table'></table></div>";

    // If there's already one entry per transition group, don't show the add entry button.
    var remaining_entries = current_project.definitions.transition_groups.length - current_scenario.config.transition_attribute_values.length;
    var button_visibility;
    if (remaining_entries > 0) {
        button_visibility = "block";
    }
    else {
        button_visibility = "none";
    }

    var add_entry_button_html = "<img src='static/img/add.png' id='add_entry_button' style='display:"+ button_visibility + "'>";

    alertify.confirm(cost_table_html + add_entry_button_html, function(e){

        if (e){
            // Update existing values (Cost)
            $.each(current_scenario.config.transition_attribute_values, function (index, obj) {
                obj.value = parseInt($("#cost_" + obj.id).val());
            });

            // Go through each of the records_to_delete and remove them from the main dictionary.
            $.each(records_to_delete, function (index, id) {
                current_scenario.config.transition_attribute_values = $.grep(current_scenario.config.transition_attribute_values, function (e) {
                    return e.id != id;
                });
            });

            records_to_delete = [];

            // Add new values
            $.each($(".new_row"), function () {
                test = this
                var transition_group_id = parseInt($(this).find('td:nth-child(1) select').val());
                var transition_attribute_type_id = parseInt($(this).find('td:nth-child(2) select').val());
                var transition_group_value = parseInt($(this).find('td:nth-child(3) input[type=number]').val());
                var random_id = 1 + Math.floor(Math.random() * 9999999);
                current_scenario.config.transition_attribute_values.push({
                    'id': random_id,
                    'iteration': null,
                    'secondary_stratum': null,
                    'stateclass': null,
                    'stratum': null,
                    'timestep': null,
                    'transition_attribute_type': transition_attribute_type_id,
                    'transition_group': transition_group_id,
                    'value': transition_group_value
                });
            });
        }

    });

    // Write current values out to the cost table
    $.each(current_scenario.config.transition_attribute_values, function(index,transition_attribute_values_dict){

        $.each(current_project.definitions.transition_groups, function(index, transition_group_dict) {

            if (transition_attribute_values_dict.transition_group == transition_group_dict.id){
                var transition_group_name = transition_group_dict.name;

                    var transition_attribute_value = transition_attribute_values_dict.value;

                    $.each(current_project.definitions.transition_attributes, function (index, transition_attributes_dict) {
                        if (transition_attributes_dict.id == transition_attribute_values_dict.transition_attribute_type) {
                            var transition_attributes_name = transition_attributes_dict.name;
                            var transition_attributes_id = transition_attribute_values_dict.id;
                            var transition_attributes_units = transition_attributes_dict.units;
                            $("#cost_table").append(
                                "<tr><td>" + transition_group_name +
                                "</td><td>" + transition_attributes_name +
                                "</td><td>" + "<input class ='cost_value_input' id='cost_" + transition_attributes_id + "' type=number value='" + transition_attribute_value + "'> " + transition_attributes_units +
                                "</td><td>" + "<img record_to_delete=cost_" + transition_attributes_id + " src='static/img/delete.png' class='delete_entry_button'>" +
                                "</td></tr>"
                            );
                        }
                    });
            }
        });
    });

    // On "+" button click...
    $("#add_entry_button").on("click", function (){

        // Add a new row to the cost table.
        $("#cost_table").append("<tr class='new_row'>" +

            "<td><select></select></td>" +
            "<td><select></select></td>" +
            "<td><input class ='cost_value_input' type='number'></td>" +
            "<td><img src='static/img/delete.png' class='delete_entry_button'>" +
            "</td></tr>"
        );

        var last_row = $("#cost_table").find("tr").last();

        // Populate new row dropdowns with available options

        // First dropdown (Transition Groups)
        current_transition_group_entries  = [];
        $.each(current_scenario.config.transition_attribute_values, function(index,current_transition_group_dict){
            current_transition_group_entries.push(current_transition_group_dict.transition_group)
        });

        $.each(current_project.definitions.transition_groups, function(index, transition_group_dict) {
            if(jQuery.inArray(transition_group_dict.id, current_transition_group_entries) == -1){
                if(jQuery.inArray(transition_group_dict.name, library_config[1].management_actions_filter) != -1)  {
                    $(last_row).find('td:nth-child(1) select').append("<option value='" + transition_group_dict.id + "'>" + transition_group_dict.name + "</option>");
                }
            }
        });

        // Second dropdown (Transition Attribute Name (e.g., Cost))
        $.each(current_project.definitions.transition_attributes, function(index, transition_attributes_dict) {
            $(last_row).find('td:nth-child(2) select').append("<option value='" + transition_attributes_dict.id + "'>" + transition_attributes_dict.name + "</option>");
        });

        var remaining_entries = current_project.definitions.transition_groups.length - current_scenario.config.transition_attribute_values.length - 1;
        if (remaining_entries > 0) {
             $("#add_entry_button").show();
        }
        else{
             $("#add_entry_button").hide();
        }

    });

};

// Array of records to delete. When the user pushes the "X" button, the id for that record gets added to the array.
// And the row is removed from the table.
records_to_delete = [];
$(document).on("click", ".delete_entry_button", function(){
    records_to_delete.push($(this).attr('record_to_delete'));
    $(this).closest("tr").remove()
});

