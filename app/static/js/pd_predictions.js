var map = L.map('mapid',{zoomControl:false}).setView([39.3110, -76.6121], 11.50);
L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png').addTo(map);

$.getJSON('static/json/pd_predictions.json',function (data) {

       geojson = L.geoJson(data,{style:function(feature){
           var fillColor,
               density = feature.properties.NoOfCrimes;
           if ( density > 200 ) fillColor = "#A50026";
           else if ( density > 170 ) fillColor = "#D73027";
           else if ( density > 160 ) fillColor = "#F46D43";
           else if ( density > 150 ) fillColor = "#FDAE61";
           else if ( density > 140 ) fillColor = "#FEE090";
           else fillColor = "#FFFFBF";  // no data
           return { color: "#999", weight: 1, fillColor: fillColor, fillOpacity: .6 };
         },
       onEachFeature: function( feature, layer ){

          layer.bindPopup( "<h6>" + feature.properties.Dist_Name +
          " District</h6><h6> Number of crimes: " + feature.properties.NoOfCrimes+"</h6>")
        }
       }).addTo(map);
});

var title = L.control({position: 'topleft'});
title.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'title');
    div.innerHTML += "<strong>Number of Crimes Predicted for Next week</strong>";
    return div;
};

title.addTo(map);
function getColor(d) {
    return d > 44000 ? '#800026' :
              d > 42500  ? '#BD0026' :
               d > 38500  ? '#E31A1C' :
               d > 34500  ? '#FC4E2A' :
               d > 28500   ? '#FD8D3C' :
               d > 24500   ? '#FEB24C' :
               d > 20500   ? '#FED976' :
                          '#FFEDA0';
}

var legend = L.control({position: 'bottomright'});
legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0,20500, 24500, 28500, 34500, 38500, 42500, 44000],
        labels = ['a'];
    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
};
legend.addTo(map);