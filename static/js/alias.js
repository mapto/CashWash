$(document).ready(function() {
	var url = new URL(location.href);
	var name = url.searchParams.get("alias");
    var country = url.searchParams.get("country");
	if (name) {
        var params = country !== undefined ? [name, country]  : [name];
		$.ajax({
		  url: "../api/open_corporates/" + params.join("/") ,
		  success: function(d) {
		  	$("#orgName").text(name);
		  	loadAlias(d);
		  },
		  loadAlias: "json"
		});
	}
});

function loadAlias(d) {
    console.log(d);
    // ## Render the Charts
    // Generate initial data
    generate_segment_data(swimlane_timeline.data);
    // Call `render()` on the charts to initially render them.
    swimlane_timeline.render();
}


// ## C3 Swimlane Timelines
// _Demonstrate how to create timelines with swimlanes._
// ## Prepare the Segment Data
// A function to generate random swimlane data
function generate_segment_data(data) {
    data.length = 0;
    var color_scale = d3.scale.category10();
    var color = color_scale('seed');
    for (var swimlane = 0; swimlane < 4; swimlane++)
        for (var time = Math.random() * 5; time < 100; time += Math.random() * 15) {
            var duration = Math.random() * 15;
            if (Math.random() > 0.75)
                color = color_scale(Math.random().toString());
            data.push({
                swimlane: swimlane,
                time: time,
                duration: time + duration > 100 ? 100 - time : duration,
                color: color
            });
            time += duration;
        }
    console.log(data);
    c3.array.sort_up(data, function (d) { return d.time; });
    console.log(data);
}

// ## Create the Segment Swimlane Chart
// Create a `c3.Plot` chart.
var segment_layer;
var swimlane_timeline = new c3.Plot.Zoomable({
    anchor: '#swimlanes',
    width: '95%',
    height: 300,
    zoomable: 'h',
    data: [],
    // Setup the **scales** to go from 0-100 horizontally and 4 swimlanes vertically.
    h: d3.scale.linear().domain([0, 100]),
    v: d3.scale.linear().domain([0, 4]),
    // Add an **x axis** with grid lines.
    axes: [
        new c3.Axis.X({
            grid: true,
            ticks: false
        }),
    ],
    layers: [
        // Add a _segment swimlane_ *layer*
        segment_layer = new c3.Plot.Layer.Swimlane.Segment({
            // Accessor functions which describe how to get **x**, **dx** and **y** values from the data elements.
            x: function (d) { return d.time; },
            dx: function (d) { return d.duration; },
            y: function (d) { return d.swimlane; },
            rect_options: {
                // Static styles are more efficiently handled in a CSS file, this is just an example.
                styles: {
                    'fill': function (d) { return d.color; },
                    'stroke': function (d) { return d3.rgb(d.color).darker().toString(); },
                    'stroke-width': 2,
                    'rx': 5,
                    'shape-rendering': 'geometricPrecision'
                }
            },
            // Create **lables** for each segment
            label_options: {
                text: function (d) { return Math.round(d.duration); },
                styles: {
                    'font-weight': 'bold',
                    'text-shadow': function (d) { return '1px 1px 1px ' + d3.rgb(d.color).brighter().toString(); }
                }
            },
            // An HTML tooltip
            hover: function (d) { return d ? Math.round(d.duration) : null; },
            // Add a border between swimlanes
            lane_options: {
                styles: {
                    'fill': 'none',
                    'stroke': 'gray'
                }
            }
        }),
    ]
});
// ## Create the Sampled Swimlane Charts
// Create a `c3.Plot` chart.

// Resize the chart to fit the window
window.onresize = function () {
    swimlane_timeline.resize();
};
