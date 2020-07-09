var map = L.map('mapid',{zoomControl:false}).setView([39.2980, -76.6121], 11.50);
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
