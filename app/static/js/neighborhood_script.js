var geojson;
var map = L.map('mapid',{zoomControl:false}).setView([39.3110, -76.6122], 11.50);
L.tileLayer('http://{s}.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png').addTo(map);
$.getJSON('static/json/neighborhood.json',function (data) {
       geojson = L.geoJson(data,{style:polystyle,onEachFeature: onEachFeature}).addTo(map);
});

function getColor(d) {
    return d > 7000 ? '#800026' :
               d > 5000 ? '#BD0026' :
               d > 3000  ? '#E31A1C' :
               d > 2000  ? '#FC4E2A' :
               d > 1000   ? '#FD8D3C' :
               d > 500   ? '#FEB24C' :
               d > 100   ? '#FED976' :
                          '#FFEDA0';
}
function polystyle(feature) {
    return {
        fillColor: getColor(feature.properties.NoOfCrimes),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 4,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }

    info.update(layer.feature.properties);
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    info.update();
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight
//        click: zoomToFeature
    });
}
//
var info = L.control({position:'topleft'});

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
    this._div.innerHTML = '<h5>Baltimore Neighborhood </h5><b>Number of Crimes</b><br/>' +
    (props ? '<br/><b>' + props.Name + '</b><br/>' + Math.floor(props.NoOfCrimes) + '</b><br />' : 'Hover over a state');
};

info.addTo(map);

var legend = L.control({position: 'bottomright'});

legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0,100, 500, 1000, 2000, 3000, 5000, 7000],
        labels = [];

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
};

legend.addTo(map);