// stacked_area.js

function createAreaChart(vegtype, chartDivID) {

    $(function () {
        $('#' + chartDivID).highcharts({
            chart: {
                type: 'areaspline',
                width: 308,
                height: 230,
                marginBottom: 50,
                marginLeft: 58,
                marginRight: 10,
                marginTop: 5
            },
            title: {
                enabled: false,
                text: "",
                margin: 5,
                x: 15,
                style: {
                    fontSize: '1.1em'
                }
            },
            credits: {
                enabled: false
            },
            subtitle: {
                text: ''
            },
            legend: {
                enabled: false
            },
            xAxis: {
                startOnTick: false,
                endOnTick: false,
                tickInterval: 1,
                title: {
                    text: 'Year'
                },
                style: {
                    "textOverflow": "none"
                }
            },
            yAxis: {
                endOnTick: false,
                title: {
                    text: 'Percent of Landscape'
                },
                labels: {
                    formatter: function () {
                        return this.value;
                    }
                }
            },
            tooltip: {
                shared: true,
                hideDelay: 100,
                formatter: function () {
                    var points = this.points;
                    var pointsLength = points.length;
                    var tooltipMarkup = '<div id="areaChartTooltipContainer">';
                    tooltipMarkup += pointsLength ? '<span style="font-size: 12px">Year: ' + points[0].key + '</span><br/>' : '';
                    var index;
                    var y;

                    for (index = 0; index < pointsLength; index += 1) {
                        y = (points[index].y).toFixed(1)

                        if (y > 0) {
                            tooltipMarkup += '<span style="color:' + points[index].series.color + '">\u25CF</span> ' + points[index].series.name + ': <b>' + y + '%</b><br/>';
                        }
                    }
                    tooltipMarkup += '</div>';

                    return tooltipMarkup;
                }
            },
            plotOptions: {
                areaspline: {
                    pointStart: 0,
                    stacking: 'normal',
                    lineColor: '#666666',
                    lineWidth: 0,
                    marker: {
                        radius: 0,
                        enabled: false,
                        lineWidth: 0,
                        lineColor: '#666666',
                        states: {
                            hover: {
                                radius: 5
                            }
                        }

                    },
                    series: {
                        marker: {
                            enabled: false
                        }
                    }
                }
            }
        });
    });

}

function createAreaCharts(data, run, iteration) {

    // Remove existing area charts
    $("#area_charts").empty();
    if (typeof iteration == "undefined") iteration = 1;

    var config = modelRunCache[run].config;
    var ratio = config.run_control.is_spatial ? 1.0 : getNonspatialRatio();

    //Restructure Dictionary
    var chartDict = {};
    $.each(data[iteration], function (timestep, results) {
        $.each(results, function (vegtype, value) {
            if (typeof chartDict[vegtype] == "undefined") {
                chartDict[vegtype] = {}
            }
            $.each(vegtypeStateclassesDictionary[vegtype], function (index, stateclass) {
                if (typeof chartDict[vegtype][stateclass] == "undefined") {
                    chartDict[vegtype][stateclass] = []
                }
                if (stateclass in results[vegtype]) {
                    value = results[vegtype][stateclass];
                    chartDict[vegtype][stateclass].push((parseFloat(value) * 100 * ratio))
                }
                else {
                    chartDict[vegtype][stateclass].push(0);
                }
            })
        })
    });

    // Go through each veg type in the results and make a chart out of the state class values
    var chartCount = 1;
    $.each(chartDict, function(vegtype, value) {
        var chartDivID = "chart_" + run + "_" + chartCount;
        var container = $("#area_charts");
        container.append("<div class='stacked_area_chart_title'>" + vegtype +
            "<span class='show_chart_link' id='show_stacked_area_chart_link_" + chartCount + "_" + run + "'> <img class='dropdown_arrows' src='/static/img/up_arrow.png'></span></div>")

        //add a new chart div
        container.append("<div id='" + chartDivID + "' vegtype='" + vegtype + "' class='stacked-chart'></div>");

        // Create the chart
        createAreaChart(vegtype, chartDivID);

        var ac = $('#' + chartDivID).highcharts();

        // Add a series for each state class
        $.each(chartDict[vegtype], function (name, values) {
            ac.addSeries({
                name: name,
                color: colorMap["State Classes"][name],
                data: values,
                lineWidth: 0,
                stacking: 'normal',
                point: {
                    events: {
                        mouseOver: function () {
                        }
                    }
                }
            })
        });

        $("#show_stacked_area_chart_link_" + chartCount + "_" + run).click(function () {
            var div = $("#" + chartDivID);
            if (div.is(":visible")) {
                $(this).html(" <img class='dropdown_arrows' src='/static/img/down_arrow.png'>");
                div.hide()
            }
            else {
                $(this).html(" <img class='dropdown_arrows' src='/static/img/up_arrow.png'>");
                div.show()
            }
        });
        chartCount++;
    });
}
