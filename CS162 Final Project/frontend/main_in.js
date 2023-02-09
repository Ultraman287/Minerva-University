
const allMarkers = [];

function initMap(markers) {
    console.log('initMap() called');
    // Calculating the center of the map
    var center = markers.reduce(function (x,y) {
        return [x[0] + y[0]/markers.length, x[1] + y[1]/markers.length];
    }, [0,0]);


    // Creating map options

    var mapOptions = {
        center: center,
        zoom: 16
            };
    
    // Creating a map object

    var map = new L.map('map-to-be', mapOptions);

    // Creating a Layer object

    var layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');

    // Adding layer to the map

    map.addLayer(layer);

    // Adding markers to the map

    markers.forEach(function (marker) {
        L.marker(marker).addTo(map);
    }); 

}