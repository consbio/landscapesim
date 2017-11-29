function createColumnChart(vegtype, chartDivID, xAxisCategories) {
    $(function () {
        $('#'+chartDivID).highcharts({
            chart: {
                type: 'column',
                width:308,
                height:250,
                marginBottom: 100,
                marginLeft:58,
                marginRight:10,
                marginTop:10
            },
            title: {
                text: ''
            },
            subtitle: {
                text: ''
            },
            credits: {
                enabled:false
            },
            tooltip: {
                valueSuffix: '%',
                shared: true,
                hideDelay:100
            },
            legend: {
            },
            xAxis: {
                categories:xAxisCategories,
                crosshair: true
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Percent of Landscape'
                }
            },
            plotOptions: {
                column: {
                    pointPadding:0,
                    borderWidth: 1
                },
                series: {
                    groupPadding: 0.05,
                    borderWidth: 1
                }
            }
        });
    });
}

function createColumnCharts(data, run) {

    //$("#iteration_tr_" + run).hide();
    $("#column_charts").empty();
    var cached_config = modelRunCache[run].config;
    var iterations = cached_config.run_control.max_iteration;
    var timesteps = cached_config.run_control.max_timestep;
    var ratio = cached_config.run_control.is_spatial ? 1.0 : getNonspatialRatio();

    //Restructure Dictionary
    //Creates a dictionary of all the final timestep values by vegtype/state class.
    var columnChartDictionary = {};
    for (var iteration = 1; iteration <= iterations; iteration++) {
        $.each(data[iteration][timesteps], function (vegtype, stateclassDictionary) {
            if (typeof columnChartDictionary[vegtype] == "undefined") columnChartDictionary[vegtype] = {}
            $.each(stateclassDictionary, function (stateclass, value) {
                if (typeof columnChartDictionary[vegtype][stateclass] == "undefined") columnChartDictionary[vegtype][stateclass] = []
                columnChartDictionary[vegtype][stateclass].push(parseFloat(value) * 100 * ratio)
            })
        })
    }

    //Get the min/median/max from the dictionary above. Store in a new dictionary.
    var columnChartDictionaryFinal = {};
    $.each(columnChartDictionary, function (vegtype, stateclasses) {
        columnChartDictionaryFinal[vegtype] = {};
        $.each(stateclasses, function (stateclass, values) {
            var min = Math.min.apply(Math, values);
            var max = Math.max.apply(Math, values);
            var sorted = values.sort();
            //var length_of_array = sorted.length;
            var low = Math.floor((sorted.length - 1) / 2);
            var high = Math.ceil((sorted.length - 1) / 2);
            var median = (sorted[low] + sorted[high]) / 2;
            columnChartDictionaryFinal[vegtype][stateclass] = [];
            columnChartDictionaryFinal[vegtype][stateclass].push(min);
            columnChartDictionaryFinal[vegtype][stateclass].push(median);
            columnChartDictionaryFinal[vegtype][stateclass].push(max);
        })
    });

    // Go through each veg type in the min/median/max dictionary and make a chart out of the state class values
    var chartCount = 1;
    $.each(columnChartDictionaryFinal, function (vegtype, stateclasses) {

        var chartDivID = "column_chart_" + run + "_" + chartCount;

        $("#column_charts").append("<div class='stacked_area_chart_title' id='stacked_area_chart_title_" + chartCount + "'>" + vegtype +

            "<span class='show_chart_link' id='show_column_chart_link_" + chartCount + "_" + run + "'> <img class='dropdown_arrows' src='/static/img/up_arrow.png'></span></div>")

        //add a new chart div
        $("#column_charts").append("<div id='" + chartDivID + "' vegtype='" + vegtype + "' class='column-chart'></div>");

        var medians = [];
        var minMaxValues = [];
        var stateClassNames = [];

        $.each(stateclasses, function (name, value) {
            stateClassNames.push([name]);
            var median = parseFloat(value[1].toFixed(1));
            var min = parseFloat(value[0].toFixed(1));
            var max = parseFloat(value[2].toFixed(1));
            medians.push({y: median, color: colorMap["State Classes"][name]});
            minMaxValues.push([min, max])
        });

        // Create the chart
        createColumnChart(vegtype, chartDivID, stateClassNames);
        var cc = $('#' + chartDivID).highcharts();

        // Add a series for each of the median values
        cc.addSeries({
            name: 'Percent Cover',
            data: medians,
            showInLegend: false,
        })

        // If the model is only run for one iteration, error bars don't make sense since there is no uncertainty.
        if (iterations > 1) {
            cc.addSeries({
                name: 'Error Bars',
                type: 'errorbar',
                data: minMaxValues,
            })    
        }

        $("#show_column_chart_link_" + chartCount + "_" + run).click(function () {
            var div = $("#" + chartDivID);
            if (div.is(":visible")) {
                $(this).html(" <img class='dropdown_arrows' src='/static/img/down_arrow.png'>")
                div.hide()
            }
            else {
                $(this).html(" <img class='dropdown_arrows' src='/static/img/up_arrow.png'>")
                div.show()
            }
        });
        chartCount++;
    });
}
