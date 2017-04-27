//var ctx = $("#spectrum-chart");
var the_chart
function get_labels(){
   
    var a = [];
    var start = 350;
    var interval = .47
    for (var i = 350; i < (350+950); i++) {
        a.push(Math.floor(start));
        start+=interval;
    }
    return a;

}
var xlabels = get_labels()
$( document ).ready(function() {
    var ctx = document.getElementById("spectrum-chart").getContext("2d");

    var data = {
    labels: xlabels,
    datasets: [
            {
                label: 'Spectral Signature', //"My First dataset",
                fill: false,
                lineTension: 0.1,
                backgroundColor: "rgba(75,192,192,0.4)",
                borderColor: "rgba(75,192,192,1)",
                borderWidth: 1,
                borderCapStyle: 'butt',
                borderDash: [],
                borderDashOffset: 0.0,
                borderJoinStyle: 'miter',
                pointBorderColor: "rgba(75,192,192,1)",
                pointBackgroundColor: "#fff",
                pointBorderWidth: 1,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: "rgba(75,192,192,1)",
                pointHoverBorderColor: "rgba(220,220,220,1)",
                pointHoverBorderWidth: 2,
                pointRadius: 0,
                pointHitRadius: 10,

                data: [],
                spanGaps: false,
            }
        ]
    };

    the_chart = new Chart(ctx, {
    type: 'bar',
    data: data,
    options:{
                scales: {
                    yAxes: [{
                        ticks: {
                            max: 1,
                            min: 0,
                            stepSize: 0.2
                        }
                    }],
                    xAxes: [{
                            //type: 'time',
                            ticks: {

                                    autoSkip: true,
                                    maxTicksLimit: 6
                            },
                             scaleLabel: {
                                    display: true,
                                    labelString: 'wavelength (nm)'
                            }
                    }],

                },
                title: {
                            display: true,
                            text: 'Spectral Signature'

                        },
                legend:{
                            display:false

                       }

            }
    });

});

var GetChartData = function () {
    $.ajax({
        url: serviceUri,
        method: 'GET',
        dataType: 'json',
        success: function (d) {
           chartData = {
                labels: d.AxisLabels,
                datasets: [
                    {
                        fillColor: "rgba(220,220,220,0.5)",
                        strokeColor: "rgba(220,220,220,1)",
                        pointColor: "rgba(220,220,220,1)",
                        pointStrokeColor: "#fff",
                        data: d.DataSets[0]
                    }
                ]
            };

            max = Math.max.apply(Math, d.DataSets[0]);
            steps = 10;

            respondCanvas();
        }
    });
};

function updateSpectrumChart(touched){
    console.log('whats up', touched.spectrum.reading);
    the_chart.data.datasets[0].data = touched.spectrum.reading;
    the_chart.update();

}
function respondCanvas() {
    var c = $('#summary');
    var ctx = c.get(0).getContext("2d");
    var container = c.parent();

    var $container = $(container);

    c.attr('width', $container.width()); //max width

    c.attr('height', $container.height()); //max height                   

    //Call a function to redraw other content (texts, images etc)
    var chart = new Chart(ctx).Line(chartData, {
        scaleOverride: true,
        scaleSteps: steps,
        scaleStepWidth: Math.ceil(max / steps),
        scaleStartValue: 0
    });
}
    // var ctx = document.getElementById("spectrum-chart").getContext("2d");

    // var myChart = new Chart(ctx, {
    //     type: 'bar',
    //     data: {
    //         labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
    //         datasets: [{
    //             label: '# of Votes',
    //             data: [12, 19, 3, 5, 2, 3],
    //             backgroundColor: [
    //                 'rgba(255, 99, 132, 0.2)',
    //                 'rgba(54, 162, 235, 0.2)',
    //                 'rgba(255, 206, 86, 0.2)',
    //                 'rgba(75, 192, 192, 0.2)',
    //                 'rgba(153, 102, 255, 0.2)',
    //                 'rgba(255, 159, 64, 0.2)'
    //             ],
    //             borderColor: [
    //                 'rgba(255,99,132,1)',
    //                 'rgba(54, 162, 235, 1)',
    //                 'rgba(255, 206, 86, 1)',
    //                 'rgba(75, 192, 192, 1)',
    //                 'rgba(153, 102, 255, 1)',
    //                 'rgba(255, 159, 64, 1)'
    //             ],
    //             borderWidth: 1
    //         }]
    //     },
    //     options: {
    //         scales: {
    //             yAxes: [{
    //                 ticks: {
    //                     beginAtZero:true
    //                 }
    //             }]
    //         }
    //     }
    // });






// var max = 0;
// var steps = 10;
// var chartData = {};

// function respondCanvas() {
//     var c = $('#summary');
//     var ctx = c.get(0).getContext("2d");
//     var container = c.parent();

//     var $container = $(container);

//     c.attr('width', $container.width()); //max width

//     c.attr('height', $container.height()); //max height                   

//     //Call a function to redraw other content (texts, images etc)
//     var chart = new Chart(ctx).Line(chartData, {
//         scaleOverride: true,
//         scaleSteps: steps,
//         scaleStepWidth: Math.ceil(max / steps),
//         scaleStartValue: 0
//     });
// }

// var GetChartData = function () {
//     $.ajax({
//         url: serviceUri,
//         method: 'GET',
//         dataType: 'json',
//         success: function (d) {
//            chartData = {
//                 labels: d.AxisLabels,
//                 datasets: [
//                     {
//                         fillColor: "rgba(220,220,220,0.5)",
//                         strokeColor: "rgba(220,220,220,1)",
//                         pointColor: "rgba(220,220,220,1)",
//                         pointStrokeColor: "#fff",
//                         data: d.DataSets[0]
//                     }
//                 ]
//             };

//             max = Math.max.apply(Math, d.DataSets[0]);
//             steps = 10;

//             respondCanvas();
//         }
//     });
// };

// $(document).ready(function() {
//     $(window).resize(respondCanvas);

//     GetChartData();
// });
