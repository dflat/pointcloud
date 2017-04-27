//var ctx = $("#spectrum-chart");
$( document ).ready(function() {
    var ctx = document.getElementById("spectrum-chart").getContext("2d");

    var data = {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: [
            {
                label: 'Spectrum', //"My First dataset",
                fill: false,
                lineTension: 0.1,
                backgroundColor: "rgba(75,192,192,0.4)",
                borderColor: "rgba(75,192,192,1)",
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
                pointRadius: 1,
                pointHitRadius: 10,
                data: [65, 59, 80, 81, 56, 55, 40],
                spanGaps: false,
            }
        ]
    };

    var the_chart = new Chart(ctx, {
    type: 'line',
    data: data,
    options: null //options
    });

});
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
