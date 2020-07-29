// Function to get colors on map
function getColor(d) {
    return d > 44000 ? '#800026' :
                   d > 42500  ? '#BD0026' :
               d > 38500  ? '#E31A1C' :
               d > 34500  ? '#FC4E2A' :
               d > 28500   ? '#FD8D3C' :
               d > 26500   ? '#333333':
               d > 24500   ? '#FEB24C' :
               d > 20500   ? '#FED976' :
                          '#FFEDA0';
}

// Map style used to color code police districts on map
function polystyle(feature) {
    return {
        fillColor: getColor(feature.properties.noOfCrimes),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

function nstyle(feature){
    return {
        weight: 2,
        opacity: 1,
        color: 'grey',
        dashArray: '3',
        fillOpacity: 0
    };
}
function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 2,
//        color: '#666',
        dashArray: ''
//        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }

    info.update(layer.feature.properties);
}

function resetHighlight(e) {
    geojson2.resetStyle(e.target);
    info.update();
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
    });
}

// Map showing intersections.
var map = L.map('mapid',{zoomControl:false}).setView([39.2904, -76.6122], 11.50);
L.tileLayer('http://{s}.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png').addTo(map);

// get police district data
$.getJSON('static/json/police_district.json',function (data) {
     geojson1 =  L.geoJson(data,{style:polystyle}).addTo(map);
});

// get the neighborhood data
$.getJSON('static/json/neighborhood.json',function (data) {
       geojson2 = L.geoJson(data,{style:nstyle,onEachFeature: onEachFeature}).addTo(map);
});


// code block for showing crime count  and other information
var info = L.control();
info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};
info.update = function (props) {
    this._div.innerHTML = '<h4>Baltimore Number Of Crimes</h4>' +  (props ?
        '<b>' + props.Name + '</b><br />' + props.NoOfCrimes + '</b><br />'+
        '<br><h4>Population density</h4>'+
        '<b>' + props.Name + '</b><br />' + props.Pop_dens
        : 'Hover over a state');
};
info.addTo(map);

// code to find intersection
$.getJSON('static/json/neighborhood.json',function (data) {
      //neighborhood feature collection
      n_feature_collection = data.features;

      $.getJSON('static/json/police_district.json',function (data) {
       // police district feature collection
        pd_feature_collection = data.features;

        pd_feature_collection.forEach(function(pd_feature){

            //change the name of district here
            if(pd_feature.properties.dist_name == 'Northern'){
                var poly1 = turf.polygon(pd_feature.geometry.coordinates[0]);

               n_feature_collection.forEach(function(n_feature){
                     var name = n_feature.properties.Name ;

                     // change the name of neighborhood here
                     if(name == 'Barclay'){
                     var poly2 = turf.polygon(n_feature.geometry.coordinates[0]);

                     var intersect = turf.intersect(poly1, poly2);

                     // view the intersection details in console
                     console.log(intersect);

                     // use when geometry consist of one polygon
//                     console.log(turf.area(turf.polygon(intersect.geometry.coordinates)));

                     // use when geometry consist of multipolygon

//                        var a1 = turf.area(turf.polygon(intersect.geometry.coordinates[0]));
//                        var a2 = turf.area(turf.polygon(intersect.geometry.coordinates[1]));


                     // use when geometry consist of 4 polygons

                        // var a1 = turf.area(turf.polygon(intersect.geometry.geometries[6].coordinates));
                        //var a2 = turf.area(turf.polygon(intersect.geometry.geometries[7].coordinates));
                        //var a3 = turf.area(turf.polygon(intersect.geometry.geometries[8].coordinates));
                        //var a4 = turf.area(turf.polygon(intersect.geometry.geometries[8].coordinates));

//                        console.log(a1+a2);


                      // highlight the overlapping polygon
                      if(intersect != null){
                          L.geoJson(intersect,{style:{color:'black', fillColor:'blue',opacity:0, weight:5}}).addTo(map);
                      }

                     }
                });
            }
        });
      });
});



