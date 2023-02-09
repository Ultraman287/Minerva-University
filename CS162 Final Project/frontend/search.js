
const allMarkers = [];
function initMap(markers) {
    // Calculating the center of the map
    console.log('This function is called');
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

    // Splitting the markers array into two arrays


    markers.forEach(function (marker) {
        var markerOptions = {
            title: marker[2],
            clickable: true};
        var lmarker = L.marker([marker[0],marker[1]], markerOptions);
        const markerData = JSON.parse(marker[3].replace(/'/g, '"'));
        popupContent = `<div class="popup">
        <h3><a href="${marker[4]}">${marker[2]}</a></h3>
        <ul class="list-group">
        `;
        markerData.forEach(function (data) {
            popupContent += `<li>${data}</li>`;
        });
        popupContent += '</ul>';
        popupContent += '</div>';
        lmarker.bindPopup(popupContent);
        lmarker.addTo(map);
    }); 


}