var map = L.map('mapid',{zoomControl:false}).setView([39.2980, -76.6121], 11.50);
L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png').addTo(map);
//L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
//L.tileLayer('http://{s}.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png').addTo(map);
//L.tileLayer('http://tiles.mapc.org/basemap/{z}/{x}/{y}.png').addTo(map);

//
$.getJSON('static/json/police_district.json',function (data) {
       geojson = L.geoJson(data,{style:function(feature){
           var fillColor,
               density = feature.properties.noOfCrimes;
           if ( density > 39000 ) fillColor = "#006837";
           else if ( density > 35000 ) fillColor = "#1A9850";
           else if ( density > 28000 ) fillColor = "#66BD63";
           else if ( density > 22000 ) fillColor = "#A6D96A";
           else if ( density > 20000 ) fillColor = "#D9EF8B";
           else fillColor = "#FFFFBF";  // no data
           return { color: "#999", weight: 1, fillColor: fillColor, fillOpacity: .6 };
         },
       onEachFeature: function( feature, layer ){
          layer.bindPopup( "<strong>" + feature.properties.dist_name + "</strong><br/>" + feature.properties.noOfCrimes)
        }
       }).addTo(map);
});

$.getJSON("static/json/homicides.json",function(data){
    var crimes = L.geoJson(data,{
      pointToLayer: function(feature,latlng){
        var marker = L.marker(latlng);
        marker.bindPopup(feature.properties.Location + '<br/>' + feature.properties.District);
        return marker;
      }
    });
    var clusters = L.markerClusterGroup({showCoverageOnHover: false});
    clusters.addLayer(crimes);
    map.addLayer(clusters);
 });
