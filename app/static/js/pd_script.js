var geojson;
var map = L.map('mapid',{zoomControl:false}).setView([39.3110, -76.6121], 11.50);
L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png').addTo(map);

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
      layer.bindPopup( "<h7>" + feature.properties.dist_name +
      " District</h7><h7> Number of crimes: " + feature.properties.noOfCrimes+"</h7>")
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

var title = L.control({position: 'topleft'});
title.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'title');
    div.innerHTML += "<strong>Total Number of Crimes in Baltimore Police Districts</strong>";
    return div;
};

title.addTo(map);

/*Filters for Crime type*/
var crime_filters_div = L.control({position: 'bottomleft'});
crime_filters_div.onAdd = function (map) {
    var div = L.DomUtil.create('form', 'crime_filters');
    var labels =['Homicides','Shootings','Robbery - Street', 'Robbery - Commercial'];
    var ids = ['Homicide','Shooting','StreetRobbery','CommercialRobbery'];

    for(var i=0; i< labels.length && i < ids.length; i++){
        div.innerHTML += "</br><input type='checkbox' id="+ ids[i] +" onchange='crime_type_filter(this.id)'><label>&nbsp"+
        labels[i]+"<label>";
    }

    return div;
};

crime_filters_div.addTo(map);

function crime_type_filter(crime_type_id){

    var crime_data_url = "";
    switch(crime_type_id){
        case 'Homicide':
            crime_data_url = "static/json/homicides.json";
            $.getJSON(crime_data_url,function(data){
                var crimes = L.geoJson(data,{
                  pointToLayer: function(feature,latlng){
                    var marker = L.marker(latlng);
                    marker.bindPopup("<h6> District: " + feature.properties.District +
                    "</h6><h6> Location: " + feature.properties.Location+"</h6><h6>Crime Type: "+ crime_type_id +"</h6>");
                    return marker;
                  }
                });

                var homicides = L.markerClusterGroup({showCoverageOnHover: false });
                homicides.addLayer(crimes);
                document.querySelector(".leaflet-pane .leaflet-marker-pane").innerHTML="";
                map.addLayer(homicides);
             });
            break;

        case 'Shooting':
            crime_data_url = "static/json/shootings.json";
            $.getJSON(crime_data_url,function(data){
                var crimes = L.geoJson(data,{
                  pointToLayer: function(feature,latlng){
                    var marker = L.marker(latlng);
                    marker.bindPopup("<h6> District: " + feature.properties.District +
                    "</h6><h6> Location: " + feature.properties.Location+"</h6><h6>Crime Type: "+ crime_type_id +"</h6>");
                    return marker;
                  }
                });

                var shootings = L.markerClusterGroup({showCoverageOnHover: false });
                shootings.addLayer(crimes);
                document.querySelector(".leaflet-pane .leaflet-marker-pane").innerHTML="";
                map.addLayer(shootings);
            });
            break;

        case 'StreetRobbery':
            crime_data_url = "static/json/street_robbery.json";
            $.getJSON(crime_data_url,function(data){
                var crimes = L.geoJson(data,{
                  pointToLayer: function(feature,latlng){
                    var marker = L.marker(latlng);
                    marker.bindPopup("<h6> District: " + feature.properties.District +
                    "</h6><h6> Location: " + feature.properties.Location+"</h6><h6>Crime Type: "+ crime_type_id +"</h6>");
                    return marker;
                  }
                });

                var street_robbery = L.markerClusterGroup({showCoverageOnHover: false });
                street_robbery.addLayer(crimes);
                document.querySelector(".leaflet-pane .leaflet-marker-pane").innerHTML="";
                map.addLayer(street_robbery);
            });
            break;
        case 'CommercialRobbery':
            crime_data_url = "static/json/commercial_rob.json";
            $.getJSON(crime_data_url,function(data){
                var crimes = L.geoJson(data,{
                  pointToLayer: function(feature,latlng){
                    var marker = L.marker(latlng);
                    marker.bindPopup("<h6> District: " + feature.properties.District +
                    "</h6><h6> Location: " + feature.properties.Location+"</h6><h6>Crime Type: "+ crime_type_id +"</h6>");
                    return marker;
                  }
                });

                var commercial_rob = L.markerClusterGroup({showCoverageOnHover: false });
                commercial_rob.addLayer(crimes);
                document.querySelector(".leaflet-pane .leaflet-marker-pane").innerHTML="";
                map.addLayer(commercial_rob);
            });
            break;

        default:
            crime_data_url = "static/json/homicides.json";
            $.getJSON(crime_data_url,function(data){
            var crimes = L.geoJson(data,{
                  pointToLayer: function(feature,latlng){
                    var marker = L.marker(latlng);
                    marker.bindPopup("<h6> District: " + feature.properties.District +
                    "</h6><h6> Location: " + feature.properties.Location+"</h6><h6>Crime Type: "+ crime_type_id +"</h6>");
                    return marker;
                  }
                });

                var homicides = L.markerClusterGroup({showCoverageOnHover: false });
                homicides.addLayer(crimes);
                document.querySelector(".leaflet-pane .leaflet-marker-pane").innerHTML="";
                map.addLayer(homicides);
            });
    }

     var inputs = document.querySelectorAll('input');
        for(var i=0; i<inputs.length; i++){
            if(inputs[i].id != crime_type_id){
                inputs[i].checked = false;
            }
        }



}




