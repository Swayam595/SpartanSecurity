var geojson;
var map = L.map('mapid',{zoomControl:false}).setView([39.2980, -76.6121], 11.50);
//L.tileLayer('http://{s}.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png').addTo(map);
L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png').addTo(map);
//L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

$.getJSON('static/json/police_district.json',function (data) {
       geojson = L.geoJson(data,{style:function(feature){
       var fillColor,
           density = feature.properties.noOfCrimes;
           if(density > 39000) fillColor = '#BD0026';
       else if ( density > 35000 ) fillColor = "#E31A1C";
       else if ( density > 28000 ) fillColor = "#FC4E2A";
       else if ( density > 26000 ) fillColor = "#FD8D3C";
       else if ( density > 24000 ) fillColor = "#FEB24C";
       else if ( density > 22000 ) fillColor = "#FED976";
       else fillColor = "#FFEDA0";  // no data
       return { color: "#999", weight: 1, fillColor: fillColor, fillOpacity: .6 };
     },

     onEachFeature: function( feature, layer ){
      layer.bindPopup( "<h6>" + feature.properties.dist_name +
      " District</h6><h6> Number of crimes: " + feature.properties.noOfCrimes+"</h6>")
    }}).addTo(map);
});

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
//function polystyle(feature) {
//    return {
//        fillColor: getColor(feature.properties.noOfCrimes),
//        weight: 2,
//        opacity: 1,
//        color: 'white',
//        dashArray: '3',
//        fillOpacity: 0.7
//    };
//}
//
//function highlightFeature(e) {
//    var layer = e.target;
//    layer.setStyle({
////        weight: 4,
////        color: '#666',
//        dashArray: '',
//        fillOpacity: 0.7
//    });
//
//    info.update(layer.feature.properties);
//}

//function resetHighlight(e) {
//    geojson.resetStyle(e.target);
//    info.update();
//}
//
//function zoomToFeature(e) {
//    map.fitBounds(e.target.getBounds());
//}
//
//function onEachFeature(feature, layer) {
//    layer.on({
//        mouseover: highlightFeature,
//        mouseout: resetHighlight,
//        click: zoomToFeature
//    });
//}

//var info = L.control();
//
//info.onAdd = function (map) {
//    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
//    this.update();
//    return this._div;
//};
//
//// method that we will use to update the control based on feature properties passed
//info.update = function (props) {
//    this._div.innerHTML = '<h4>Baltimore Number Of Crimes by Police Districts </h4>' +  (props ?
//        '<b>' + props.dist_name + '</b><br />' + props.noOfCrimes
//        : 'Hover over a state');
//};
//
////info.addTo(map);


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


//var data_url =  "";
var crime_filters = L.control({position: 'bottomleft'});

crime_filters.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'crime_filters');
    var labels =['Homicides','Shootings','Robbery - Street', 'Robbery - Commercial'];
    var ids = ['homicide','shooting','rob_st','rob_com'];
    var i=0;
//    div.innerHTML = '<form>';
//
//    while(i < labels.length && i < ids.length)
//        div.innerHTML += "</br><input type='checkbox' id="+ ids[i] +"><label>&nbsp"+ labels[i]+"<label>";
//        i++;
//    }
//
//    div.innerHTML+= '</form>';

    div.innerHTML = "<form></br><input type='checkbox' id='homicide'><label>&nbsp Homicide</label></br><input type='checkbox' id='shooting'><label>&nbsp Shootings</label></br><input type='checkbox' id='rob_com'><label>&nbsp Robbery- Commercial</label></br><input type='checkbox' id='rob_st'><label>&nbsp Robbery - Street</label></form>";
    return div;
};

crime_filters.addTo(map);


$.getJSON("static/json/homicides.json",function(data){
    var crimes = L.geoJson(data,{
      pointToLayer: function(feature,latlng){
        var marker = L.marker(latlng);
        marker.bindPopup("<h6> DISTRICT: " + feature.properties.District +
        "</h6><h6> LOCATION: " + feature.properties.Location+"</h6>");
        return marker;
      }
    });
    var clusters = L.markerClusterGroup({showCoverageOnHover: false });
    clusters.addLayer(crimes);
    map.addLayer(clusters);
 });
