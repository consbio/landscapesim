L.Control.Button = L.Control.extend({

    onAdd: function(map) {

        // Outer Div
        var controlDiv = L.DomUtil.create('div', 'leaflet-control-command-button-container');

        // Inner Div
        var controlUI = L.DomUtil.create('div', 'leaflet-control-command-button', controlDiv);

        var img = L.DomUtil.create('img', 'leaflet-control-button-img', controlUI);

        img.src = 'static/img/cost_button.png';

        // Click Event
        L.DomEvent
            .addListener(controlUI, 'click', function () {
                openCostTable()
            });

        // Title
        controlUI.title = 'Set the available management actions';

        return controlDiv;
    }
});

L.control.button = function(opts) {
    return new L.Control.Button(opts);
};


