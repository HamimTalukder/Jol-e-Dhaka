// A smaller map just for picking a location
var reportMap = L.map('report-map').setView([23.8103, 90.4125], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18
}).addTo(reportMap);

var marker;

// When the user clicks the map, save the coordinates into the hidden form fields
reportMap.on('click', function (e) {
    document.getElementById('latitude').value = e.latlng.lat;
    document.getElementById('longitude').value = e.latlng.lng;

    if (marker) {
        marker.setLatLng(e.latlng);
    } else {
        marker = L.marker(e.latlng).addTo(reportMap);
    }
});

// Try to center the map on the user's current location, if they allow it
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
        reportMap.setView([position.coords.latitude, position.coords.longitude], 14);
    });
}
