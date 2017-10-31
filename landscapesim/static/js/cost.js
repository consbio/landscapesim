function openCostTable() {
    var costTableText = "<div id='cost_table_div'><table id='cost_table'></table></div>";

    // If there's already one entry per transition group, don't show the add entry button.
    var remaining = currentProject.definitions.transition_groups.length - currentScenario.config.transition_attribute_values.length;
    var buttonVisibility;
    if (remaining > 0) {
        buttonVisibility = "block";
    }
    else {
        buttonVisibility = "none";
    }

    var addEntryButton = "<img src='static/img/add.png' id='add_entry_button' style='display:"+ buttonVisibility + "'>";
    alertify.confirm(costTableText + addEntryButton, function(e){

        if (e){
            // Update existing values (Cost)
            $.each(currentScenario.config.transition_attribute_values, function (index, obj) {
                obj.value = parseInt($("#cost_" + obj.id).val());
            });

            // Go through each of the costRecordsToDelete and remove them from the main dictionary.
            $.each(costRecordsToDelete, function (index, id) {
                currentScenario.config.transition_attribute_values = $.grep(currentScenario.config.transition_attribute_values, function (e) {
                    return e.id != id;
                });
            });

            costRecordsToDelete = [];

            // Add new values
            $.each($(".new_row"), function () {
                var transitionGroupID = parseInt($(this).find('td:nth-child(1) select').val());
                var transitionAttributeTypeID = parseInt($(this).find('td:nth-child(2) select').val());
                var transitionGroupValue = parseInt($(this).find('td:nth-child(3) input[type=number]').val());
                var randomID = 1 + Math.floor(Math.random() * 9999999);
                currentScenario.config.transition_attribute_values.push({
                    'id': randomID,
                    'iteration': null,
                    'secondary_stratum': null,
                    'stateclass': null,
                    'stratum': null,
                    'timestep': null,
                    'transition_attribute_type': transitionAttributeTypeID,
                    'transition_group': transitionGroupID,
                    'value': transitionGroupValue
                });
            });
        }

    });

    var costTable = $("#cost_table");
    costTable.append("<tr><th>Management Action</th><th>Type</th><th>Value</th><th>Delete</th></tr>");

    // Write current values out to the cost table
    $.each(currentScenario.config.transition_attribute_values, function(index, transitionAttributeValues) {
        $.each(currentProject.definitions.transition_groups, function(index, transitionGroup) {
            if (transitionAttributeValues.transition_group == transitionGroup.id) {
                var transitionGroupName = transitionGroup.name;
                var transitionAttributeValue = transitionAttributeValues.value;
                $.each(currentProject.definitions.transition_attributes, function (index, transitionAttribute) {
                    if (transitionAttribute.id == transitionAttributeValues.transition_attribute_type) {
                        var name = transitionAttribute.name;
                        var id = transitionAttributeValues.id;
                        var units = transitionAttribute.units;
                        $("#cost_table").append(
                            "<tr><td>" + transitionGroupName +
                            "</td><td>" + name +
                            "</td><td>" + "<input class ='cost_value_input' id='cost_" + id + "' type=number value='" + transitionAttributeValue + "'> " + units + "/acre" +
                            "</td><td>" + "<img record_to_delete=" + id + " src='static/img/delete.png' class='delete_entry_button'>" +
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
        costTable.append("<tr class='new_row'>" +

            "<td><select></select></td>" +
            "<td><select></select></td>" +
            "<td><input class ='cost_value_input' type='number'></td>" +
            "<td><img src='static/img/delete.png' class='delete_entry_button'>" +
            "</td></tr>"
        );

        var lastCostRow = costTable.find("tr").last();

        // Populate new row dropdowns with available options

        // First dropdown (Transition Groups)
        var transitionGroupEntries = [];
        $.each(currentScenario.config.transition_attribute_values, function(index, transitionGroup) {
            transitionGroupEntries.push(transitionGroup.transition_group)
        });

        var managementActionsKeys = [];
        $.each(store[currentLibrary.id].management_actions_filter, function(key, value) {
            managementActionsKeys.push(key)
        });

        $.each(currentProject.definitions.transition_groups, function(index, transitionGroup) {
            if(jQuery.inArray(transitionGroup.id, transitionGroupEntries) == -1){
                if(jQuery.inArray(transitionGroup.name, managementActionsKeys) != -1)  {
                    $(lastCostRow).find('td:nth-child(1) select').append("<option value='" + transitionGroup.id + "'>" + store[currentLibrary.id].management_actions_filter[transitionGroup.name] + "</option>");
                }
            }
        });

        // Second dropdown (Transition Attribute Name (e.g., Cost))
        $.each(currentProject.definitions.transition_attributes, function(index, transitionAttribute) {
            $(lastCostRow).find('td:nth-child(2) select').append("<option value='" + transitionAttribute.id + "'>" + transitionAttribute.name + "</option>");
        });

        var remaining = currentProject.definitions.transition_groups.length - currentScenario.config.transition_attribute_values.length - 1;
        if (remaining > 0) {
             $("#add_entry_button").show();
        }
        else{
             $("#add_entry_button").hide();
        }
    });
}

// Array of records to delete. When the user pushes the "X" button, the id for that record gets added to the array.
// And the row is removed from the table.
var costRecordsToDelete = [];
$(document).on("click", ".delete_entry_button", function(){
    costRecordsToDelete.push($(this).attr('record_to_delete'));
    $(this).closest("tr").remove()
});

