// context_help.js


var context_config = {
    "welcome": {
        "title": '<div class="steps">General Settings</div>',
        "hover": "<div class='context_basic'>" +
                 "<p>Decide which ST-Sim model library to use, number of " +
                 "timesteps, and number of Monte-Carlo iterations.</p>" +
                 "</div>",
        "detail": "<table class='general_settings_table'>" +
                    "<tr>" +
                    "<td>" +
                    "<div class='general_settings_div'>" +
                    "Library" +
                    "</div>" +
                    "</td>" +
                    "<td>The active ST-Sim library for the current area.</td>" +
                    "</tr>" +
                    "<tr>" +
                    "<td>" +
                    "<div class='general_settings_div'>" +
                    "Spatial Output" +
                    "</div>" +
                    "</td>" +
                    "<td>Toggle spatial run output (currently in development).</td>" +
                    "</tr>" +
                    "<tr>" +
                    "<td>" +
                    "<div class='general_settings_div'>" +
                    "Timesteps" +
                    "</div>" +
                    "<td>Specify the number of (annual) timesteps to project.</td>" +
                    "</tr>" +
                    "<tr>" +
                    "<td>" +
                    "<div class='general_settings_div'>" +
                    "Iterations" +
                    "</div>" +
                    "<td>Specify the number of Monte-Carlo iterations to perform.</td>" +
                    "</tr>" +
                    "</table>"
    },
    "library": {
        "title": "",
        "hover": "",
        "detail": "",
    },
    "veg-cover": {
        "title": "",
        "hover": "",
        "detail": "",
    },
    "probabilities": {
        "title": "",
        "hover": "",
        "detail": "",
    },
    "run-control": {
        "title": "",
        "hover": "",
        "detail": "",
    },
}


/**
    Return basic help content
    @param helpID Integer ID key pointing towards which help context was selected.
    @return string An HTML string based on which ID help icon they are hovering over
 */
function helpContentBasic(helpID) {
	switch (helpID) {
		case 1:
			return  "<div class='context_basic'>" +
                    "<p>Decide which ST-Sim model library to use, number of " +
                    "timesteps, and number of Monte-Carlo iterations.</p>" +
                    "</div>";
		case 2:
			return  "<div class='context_basic'>" +
                    "<p>Vegetation present in this study area, separated by percent cover." +
                    "</div>";
		case 3:
			return  "<div class='context_basic'>" +
                    "<p>Adjust climate scenarios for temperature and precipitation." +
                    "</div>";
		case 4:
			return  "<div class='context_basic'>" +
                    "<p>Adjust probabilities to affect the rate at which vegetation will change due to disturbances." +
                    "</div>";
		default:
			return '';
	}
}

/**
    Return titles to help content
    @param helpID Integer ID key pointing towards which help context was selected.
    @return string An HTML string based on which ID help icon they are hovering over
 */
function helpContentTitle(helpID) {
    switch (helpID) {
        case 1:
            return '<div class="steps">General Settings</div>';
        case 2:
            return '<div class="steps">Specify Initial Vegetation Cover</div>';
        case 3:
            return '<div class="steps">Climate Change Projections</div>';
        case 4:
            return '<div class="steps">Annual Disturbance Probabilities</div>';
        default:
            return '';
    }
}

/**
    Return in-depth help content
    @param helpID Integer ID key pointing towards which help context was selected.
    @return string An HTML string based on which ID help icon they are hovering over
 */
function helpContentInDepth(helpID) {

    switch (helpID) {

        case 1:
            return "<table class='general_settings_table'>" +
                    "<tr>" +
                    "<td>" +
                    "<div class='general_settings_div'>" +
                    "Library" +
                    "</div>" +
                    "</td>" +
                    "<td>The active ST-Sim library for the current area.</td>" +
                    "</tr>" +
                    "<tr>" +
                    "<td>" +
                    "<div class='general_settings_div'>" +
                    "Spatial Output" +
                    "</div>" +
                    "</td>" +
                    "<td>Toggle spatial run output (currently in development).</td>" +
                    "</tr>" +
                    "<tr>" +
                    "<td>" +
                    "<div class='general_settings_div'>" +
                    "Timesteps" +
                    "</div>" +
                    "<td>Specify the number of (annual) timesteps to project.</td>" +
                    "</tr>" +
                    "<tr>" +
                    "<td>" +
                    "<div class='general_settings_div'>" +
                    "Iterations" +
                    "</div>" +
                    "<td>Specify the number of Monte-Carlo iterations to perform.</td>" +
                    "</tr>" +
                    "</table>";
        case 2:
            return  "<div style='text-align: left'>" +
                    "<p>Each slider present represents a recorded vegetation type visible in the region. " +
                    "Adjusting the value will change the proportion of the landscape the vegetation/strata covers.</p>" +

                    "</div>" +
                    "<div><tr><td>" +
                    "<table class='initial_veg_cover_input_table' style='background-color: #E9E9E9;'>" +
                    "<tr><td colspan='4'>" +
                    "<label for='amount_veg1'><div class='imageOverlayLink' style='width: 328px;'>Vegetation/Strata Type </div></label>" +
                    "</td></tr>" +
                    "<tr><td>" +
                    "<div class='slider_bars_disabled ui-slider ui-slider-horizontal ui-widget ui-widget-content ui-corner-all' id='vegNothing_slider' aria-disabled='false'>" +
                    "<div class='ui-slider-range ui-widget-header ui-slider-range-min' style='width: 33%;'>" +
                    "</div><a class='ui-slider-handle ui-state-default ui-corner-all' href='#' style='left: 33%;'>" +
                    "</a></div>" +
                    "</td><td>" +
                    "<input type='text' style='width:60px!important' class='current_slider_setting' value='Pct. Cover' readonly>" +
                    "</td>" +
                    "<td>" +
                    "<div class='show_state_classes_link state_class_div'> <span class='state_class_span'>State Classes</span></div>" +
                    "<div class='sub_slider_text_inputs_demo' style='display:none'>" +
                    "<div class='callout right '>" +
                    "<table class='sub_slider_table' title='Vegtype'></table>" +
                    "</div></div>" +
                    "</td><td>" +
                    "<div class='manage_div'><span class='manage_span'>Manage</span></div>" +
                    "<div class='management_action_inputs' style='display:none'>" +
                    "<div class='manage_callout_demo callout_demo right'>" +
                    "<table class='sub_slider_table' title='Vegtype'></table>" +
                    "</div>" +
                    "</div>" +
                    "</td></tr></table>" +
                    "</td></tr>" +
                    "<div style='text-align: left'>" +
                    "<p>Note: the 3D viewer will not update the percent on the landscape. " +
                    "Changes in the proportion are relative to the overall proportion of the landscape, and are valid only for the selected location.</p>" +
                    "</div>" +
                    "<div class='sub_slider_text_inputs_demo' style='display: block; position: relative!important; left: 0px;'>" +
                    "<div class='callout_demo right'><table id='noID' class='sub_slider_table' title='1010451'>" +
                    "<tbody>" +
                    "<tr><td>Early1:ALL </td><td><input class='veg_state_class_entry' id='noID' type='text' size='2' value='1.021'>%</td></tr>" +
                    "<tr><td>Late1:CLS </td><td><input class='veg_state_class_entry' id='noID' type='text' size='2' value='0.184'>%</td></tr>"+
                    "<tr><td>Late1:OPN </td><td><input class='veg_state_class_entry' id='noID' type='text' size='2' value='0.427'>%</td></tr>" +
                    "<tr><td>Mid1:CLS </td><td><input class='veg_state_class_entry' id='noID' type='text' size='2' value='0.118'>%</td></tr>" +
                    "<tr><td>Mid1:OPN </td><td><input class='veg_state_class_entry' id='noID' type='text' size='2' value='3.802'>%</td></tr>" +
                    "</tbody></table></div></div>" +
                    "<div class='management_action_inputs_demo' style='display: block; position: relative!important; left: 0px;'>" +
                    "<div class='manage_callout_demo right'>" +
                    "<table id='noID_management' class='sub_slider_table' title='1210110'>" +
                    "<tbody><tr><td>Insect/Disease</td>" +
                    "<td><input class='management_action_entry' id='management_noID_manage' type='text' size='2' value='150'> Acres</td></tr>" +
                    "<tr><td>AllFire</td><td><input class='management_action_entry' id='management_1_5_manage' type='text' size='2' value='250'> Acres</td></tr>" +
                    "</tbody></table></div></div>" +
                    "</div>" +
                    "<div style='text-align: left'>" +
                    "<p>Each vegetation/strata is broken down by state class, which is defined by the ST-Sim library.</p>" +
                    "<p>Each state class is defined with a development stage and a structural stage.</p>" +
                    "</div>" +
                    "<div style='text-align: left'>" +
                    "<p>Each vegetation/strata also has a group of management actions associated with it, also defined by " +
                    "the ST-Sim library. Each management action defines a target number of acres to apply the management action to, " +
                    "adjusting the model to aim for the targeted number of actions by utilizing the specified action.</p>" +
                    "</div>";
        case 3:
            return  '<table class="sliderTable climateFutureSliderTable_disabled">' +
                    '<tbody><tr><td>' +
                    '<label for="amount_climate_temp"><span class="transition_type">Temperature: </span></label>' +
                    '<input type="text" class="current_climate_future_slider_setting" value="Hot" readonly="">' +
                    '<div class="slider_bars probabilistic_transition_sliders ui-slider ui-slider-horizontal ui-widget ui-widget-content ui-corner-all" id="climate_future_temp_slider" aria-disabled="false">' +
                    '<a class="ui-slider-handle ui-state-default ui-corner-all" href="#" style="left: 50%;"></a>' +
                    '</div></td>' +
                    '<td><label for="amount_climate_precip"><span class="transition_type">Precipitation: </span></label>' +
                    '<input type="text" class="current_climate_future_slider_setting" value="Wet" readonly="">' +
                    '<div class="slider_bars_disabled probabilistic_transition_sliders ui-slider ui-slider-horizontal ui-widget ui-widget-content ui-corner-all" id="climate_future_precip_slider" aria-disabled="false">' +
                    '<a class="ui-slider-handle ui-state-default ui-corner-all" href="#" style="left: 0%;">' +
                    '</a></div></td></tr></tbody></table>' +
                    '<div style="text-align: left">' +
                    '<p>Climate futures relate potential climate scenarios to increased or ' +
                    'decreased occurrence of probable events that promote changes in vegetation or state classes outside of stand age. </p>' +
                    '</div>';
        case 4:
            return  '<table class="sliderTable">' +
                    '<tbody><tr><td><label for="amount_veg1"><span class="transition_type">Replacement Fire: </span></label>' +
                    '<input type="text" class="current_probability_slider_setting" value="Moderately High (+25%)" readonly="">' +
                    '<div class="slider_bars_disabled probabilistic_transition_sliders ui-slider ui-slider-horizontal ui-widget ui-widget-content ui-corner-all" aria-disabled="false">' +
                    '<div class="ui-slider-range ui-widget-header ui-slider-range-min" style="width: 62.5%;"></div>' +
                    '<a class="ui-slider-handle ui-state-default ui-corner-all" href="#" style="left: 62.5%;"></a></div></td></tr>' +
                    '</tbody></table>' +
                    '<div style="text-align: left">' +
                    '<p>Disturbance probabilities relate the probability of changes from one state to another.</p>' +
                    '<p>For many STSM models, this is demonstrated by a change between state classes within a vegetation type, while others demonstrate changes by replacing complete strata types with another. ' +
                    'Adjusting these sliders will affect the probability that the vegetation type will be influenced by a probabilistic event caused by the transition type, such as fire or disease.' +
                    'Disturbance probabilities will often cause stand ages to reset, moving state classes down from Late stage to Early stage.</p>' +
                    '<p>For example, an increase in the probability of "Replacement Fire" will increase the probability that a replacement fire will occur,' +
                    'causing vegetation to shift from Mid or Late stages to Early stages.</p>' +
                    '</div>';
        default:
            return '';
    }

}

// Tooltip popup on context help icons
$(document).on({
    click: function(e) {
        e.stopPropagation();    // Prevent slideUp
        var helpID = Number(this.id.split('_').slice(-1)[0]);
        alertify.alert(helpContentTitle(helpID) + helpContentInDepth(helpID));
    },
    mouseenter: function (e) {
        var popup = $("#pop-up");
        var moveLeft = 50;
        var moveDown = -20;

        var helpID = Number(this.id.split('_').slice(-1)[0]);
        
        popup.html(helpContentBasic(helpID));  // split and get last element of the id. Ids look like 'help_step_x'
        popup.show();

        $('.context_button').mousemove(function (e) {
            popup.css('top', e.pageY + moveDown).css('left', e.pageX + moveLeft);
        });
    },
    mouseleave: function(e) {
        $("#pop-up").hide();
    }
}, '.context_button');
