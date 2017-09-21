var action_list = [];
var totalCost = 0;
$("#totalCost").text(totalCost);

// Basemaps
var topographic = L.esri.basemapLayer("Topographic").addTo(map);

var drawnItems = L.featureGroup().addTo(map);

L.control.button({ position: 'topleft' }).addTo(map);

L.control.shapefile({ position: 'topleft' }).addTo(map);

// Leaflet.draw
map.addControl(new L.Control.Draw({
    edit:{
        featureGroup: drawnItems,
        remove: false,
    },
    draw: {
        marker: false,
        circle: false,
        polyline:false,
        rectangle : {
            metric: false,
            showArea: true
        },
        polygon : {
            allowIntersection: false,
            metric: false,
            showArea: true
        }
    }
}));


// BEGIN DRAW FUNCTION
map.on('draw:created', function(event){
    initializePolygon(event.layer)
});

function initializePolygon(layer){

    // On draw...
    layer._cost = 0;

    // Set the color of the polygon
    /*
    var colorR = Math.floor((Math.random() * (255-0+1)+0));
    var colorG = Math.floor((Math.random() * (255-0+1)+0));
    var colorB = Math.floor((Math.random() * (255-0+1)+0));
    var randColor = "rgb(" + colorR + "," + colorG + "," + colorB + ")";
    layer.options.color = randColor;
    */

    layer.options.color = "#00FFFF";
    layer.options.fillOpacity = 0;

    // Add the shape to map
    drawnItems.addLayer(layer);

    // Get the polygon ID
    var polyID = (layer._leaflet_id).toString();

    // Set the popup message content (dropdown menu, timesteps, etc).
    var popupMessage =
         "<div class='popupHeader'> Choose a Management Action</div>" +
             "<form polyID='" + polyID + "' class='managementActionForm' onsubmit='return false'>" +
                "<select id='action_" + polyID + "' class='managementActionSelect'/>";

                // Set the dropdown options using list of those that have dollar amounts set for them in the table.
                $.each(current_scenario.config.transition_attribute_values, function (index, object) {

                       var this_transition_group_id = object["transition_group"];

                       // Need the transition group name. Get the matching transition group object that has the id and the name in it.
                       var transition_group_match = $.grep(current_project.definitions.transition_groups, function(e){return e.id == this_transition_group_id })[0];

                        popupMessage += "<option value=" + transition_group_match['id'] + ">" + library_config[current_library.id]['management_actions_filter'][transition_group_match['name']] + "</option>";
                });

                popupMessage += "</select>" +

                "<p><div class='popupHeader' style='height:15px'> Timesteps " +

                    "<span id='selectTimestepOptions'>" +
                        "(<span class='selectTimestepLinks selectAllTimesteps' id='selectAllTimesteps'>all</span class='selectTimestepLinks'>|" +
                        "<span class='selectTimestepLinks selectEvenTimesteps' id='selectEvenTimesteps'>even</span class='selectTimestepLinks'>|" +
                        "<span class='selectTimestepLinks selectOddTimesteps' id='selectOddTimesteps'>odd</span class='selectTimestepLinks'>|" +
                        "<span class='selectTimestepLinks selectNoTimesteps' id='selectNoTimesteps'>none</span class='selectTimestepLinks'>)" +
                    "</span>" +

                "</div>" +

                "<div id='timestepDiv' class='timelineTableDiv'><table class='timelineTable'><tr>";

                for(var i = 1; i <= current_scenario.config.run_control.max_timestep ; i++){
                    popupMessage += "<td>" + i.toString() + "</td>"
                }

                popupMessage += "</tr><tr>";

                for(var i = 1; i <= current_scenario.config.run_control.max_timestep; i++){
                    popupMessage += "<td><input name='timestep' type='checkbox'></td>"
                }

                popupMessage += "</tr></table></div>" +

                "</select><input class='okButton' type='submit' value='OK'>" +

             "</form>" +

         "<div class='deletePolyDiv'><input type='button' class='deletePolyButton' polyToDelete='" + polyID + "' value='Delete'/></div><br><br>";

    // Open the popup.
    layer.bindPopup(popupMessage,{closeButton:false}).openPopup();

}
//END DRAW FUNCTION
//BEGIN POPUP FUNCTION
map.on('popupopen', function(e) {

    // Triggered on layer draw or layer click. Sets the selected options to what the user had previously selected.

    var polyID = e.popup._source._leaflet_id;

    // Get the current action.
    var currentActionList = $.grep(action_list, function(e) {
        if (typeof e != "undefined" && e.poly_id == polyID){
            return e
        }
    });

    // Set the current action.
    if (currentActionList.length > 0) {
        var currentAction = currentActionList[0].action_id;
        $("#action_" + polyID).val(currentAction);
    }

    // Get the current timesteps.
    var layer = map._layers[polyID];
    var allTimesteps = layer._timesteps;
    var index = 0;

    // Set the current timesteps.
    $("#timestepDiv input[type=checkbox]").each(function() {

        if (typeof allTimesteps != 'undefined' && allTimesteps[index]) {
            $(this).prop('checked', true);
        }

        index+=1;
    });

});
// END POPUP FUNCTION

// BEGIN SUBMIT FUNCTION
$(document).on("submit", ".managementActionForm", function(){

    // On "OK" button push, get the polygon ID.
    var polyID = parseInt($(this).attr('polyID'));

    var layer = map._layers[polyID];

    // Check to see if the polygon exists in the action_list object list.
    var exists = action_list.some( function(obj) {
        return obj.poly_id === polyID;
    });

    // If it exists, remove it.
    if (exists){
        action_list = $.grep(action_list, function(e){
            if (typeof e != "undefined") {
                return e.poly_id != polyID;
            }
        });
    }

    //var polyWKT = calculateWKT(layer);
    var geoJSON = layer.toGeoJSON()

    // Add a new object to the action_list and set some of the layer properties.
    var actionObj = {};
    var actionID = parseInt($(this).find('.managementActionSelect option:selected').val())
    layer._actionID = actionID;

    // Timesteps
    var sumTimesteps = 0;
    var allTimesteps = [];
    $("#timestepDiv input[type=checkbox]").each(function() {
        if (this.checked) {
            allTimesteps.push(1);
            sumTimesteps+=1
        }
        else {
            allTimesteps.push(0);
        }
    });

    layer._timesteps = allTimesteps;
    layer._sumTimesteps = sumTimesteps;

    actionObj["poly_id"] = polyID;
    //actionObj["wkt"] = polyWKT;
    actionObj["geoJSON"] = geoJSON;
    actionObj["action_id"] = actionID;
    actionObj["timesteps"] = allTimesteps;

    action_list.push(actionObj);

    $.each(current_project.definitions.transition_groups, function (index, object) {
        if (typeof object != "undefined") {
            if (object["id"] == layer._actionID) {
                layer._actionText = library_config[current_library.id]["management_actions_filter"][object["name"]]
            }
        }
    });

    // Calculate the area.
    calcArea(layer);

    // Calculate the cost.
    calcCost(layer);

    // Update the tooltip.
    updateTooltip(layer);

    map.closePopup();
    return false;

});
// END SUBMIT FUNCTION

// BEING POLYGON DELETING FUNCTION (button push)
$(document).on("click", ".deletePolyButton", function(){

    var polyToDelete = parseInt($(this).attr('polyToDelete'));
    var layerToRemove = map._layers[polyToDelete];

    // Update the cost.
    var cost = map._layers[polyToDelete]._cost;

    // Handle the case where a user creates a polygon and deletes it before saving it.
    if (typeof cost != "undefined"){
        totalCost -= cost;
        $("#totalCost").text(totalCost.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
    }

    map.removeLayer(layerToRemove);

    $.each(action_list, function (index, object) {
        if (typeof object != "undefined") {
            if (object["poly_id"] == polyToDelete) {
                delete action_list[index];
            }
        }
    });
});
// END POLYGON DELETING FUNCTION (button push)

// BEING POLYGON EDITING FUNCTION
map.on('draw:edited', function(event) {

    // Triggered on SAVE.

    var layers = event.layers;

    layers.eachLayer(function(layer){

        layer.unbindTooltip();

        // update the WKT & store it as a property of the layer and in the action_list
        //var polyWKT = calculateWKT(layer);
        var geoJSON = layer.toGeoJSON();
        calcArea(layer);
        calcCost(layer);
        updateTooltip(layer);

        $.each(action_list, function (index, object) {
            if (typeof object != "undefined") {
                if (object["poly_id"] == parseInt(layer._leaflet_id)) {
                    //this.wkt = polyWKT
                    this.geoJSON = geoJSON
                }
            }
        });

    });
});
// END POLYGON EDITING FUNCTION

// BEGIN LAYER CALCULATION FUNCTIONS
function calculateWKT(layer) {
    // calculate the WKT based on layer geometry
    var geojson = layer.toGeoJSON();
    var polyWKT = Terraformer.WKT.convert(geojson.geometry);
    layer._wkt  = polyWKT;
    return polyWKT;
}

function calcArea(layer){
    var latlngs = layer._defaultShape ? layer._defaultShape() : layer.getLatLngs();
    var area = L.GeometryUtil.geodesicArea(latlngs);
    layer._area = area;
    return area;
}

function calcCost(layer){

    // If a cost has already been associated with this polygon, remove it from the total cost.
    if (typeof layer._cost  != "undefined"){
        totalCost-=(layer._cost);
    }

    // area is in meters2
    var acres =  layer._area * 0.0002471044;

    var costArray = $.grep(current_scenario.config.transition_attribute_values, function(e) {
        if (typeof e != "undefined" && typeof layer._actionID != "undefined" && e.transition_group == layer._actionID.toString()){
            return e
        }
    });

    // Set the current action.
    if (costArray.length > 0) {
        var cost = parseInt(costArray[0].value * acres * layer._sumTimesteps);
        layer._cost = cost;
        // Update the total cost.
        totalCost += cost;
        $("#totalCost").text(totalCost.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        return cost
    }
}

function updateTooltip(layer) {

    var actionText = "<b>" + layer._actionText + "</b>";

    // Messages for the tooltip (label).
    var areaMessage = "Area: " + L.GeometryUtil.readableArea(layer._area, false);
    var timestepMessage = "Timesteps: " + layer._sumTimesteps;
    var costMessage = "Cost: $" + layer._cost.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    // Open the tooltip (label).
    layer.unbindTooltip();
    layer.bindTooltip(actionText + "<br>" + areaMessage + "<br>" + timestepMessage + "<br>" + costMessage, {permanent: true}).addTo(map);

}
// END LAYER CALCULATION FUNCTIONS

// Add actions to bulk timestep selection links in the popup.
$(document).on("click", ".selectTimestepLinks", function(){
    $("#timestepDiv input[type=checkbox]").each(function() {
        $(this).prop("checked", false)
    });
});

$(document).on("click", ".selectAllTimesteps", function(){
    $("#timestepDiv input[type=checkbox]").each(function() {
        $(this).prop("checked", true)
    });
});

$(document).on("click", ".selectNoTimesteps", function(){
    $("#timestepDiv input[type=checkbox]").each(function() {
        $(this).prop("checked", false)
    });
});

$(document).on("click", ".selectEvenTimesteps", function(){
    $("#timestepDiv input[type=checkbox]:odd").each(function() {
        $(this).prop("checked", true)
    });
});

$(document).on("click", ".selectOddTimesteps", function(){
    $("#timestepDiv input[type=checkbox]:even").each(function() {
        $(this).prop("checked", true)
    });
});

