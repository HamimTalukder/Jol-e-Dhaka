// Set up the map, centered on Dhaka
var map = L.map('map').setView([23.8103, 90.4125], 12);

// Add OpenStreetMap tiles (free, no API key needed)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18
}).addTo(map);

// A color for each severity level, used for markers, dots, and sort buttons
var colors = {
    light: '#22C55E',
    moderate: '#F59E0B',
    severe: '#EF4444'
};

var allReports = [];
var activeFilter = null;

// Ask our own Flask backend for the current list of active reports
fetch('/api/reports')
    .then(function (response) {
        return response.json();
    })
    .then(function (reports) {
        allReports = reports;
        drawMarkers();
        renderList();
    });

function drawMarkers() {
    allReports.forEach(function (report) {
        var marker = L.circleMarker([report.latitude, report.longitude], {
            radius: 10,
            color: colors[report.severity] || 'gray',
            fillColor: colors[report.severity] || 'gray',
            fillOpacity: 0.85,
            className: 'blink-marker'
        }).addTo(map);

        var popupHtml =
            '<b>' + (report.area_name || 'Unknown area') + '</b><br>' +
            'Severity: ' + report.severity + '<br>' +
            (report.description ? report.description + '<br>' : '') +
            '<small>Reported: ' + report.created_at + '</small><br>' +
            '<form action="/confirm/' + report.id + '" method="post" style="display:inline">' +
            '<button type="submit">Still there</button></form> ' +
            '<form action="/clear/' + report.id + '" method="post" style="display:inline">' +
            '<button type="submit">Cleared</button></form>';

        marker.bindPopup(popupHtml);
    });
}

// Builds the "Active Reports" list on the right of the map
function renderList() {
    var listEl = document.getElementById('reports-list');
    listEl.innerHTML = '';

    var filtered = activeFilter
        ? allReports.filter(function (r) { return r.severity === activeFilter; })
        : allReports;

    if (filtered.length === 0) {
        listEl.innerHTML = '<li class="empty">No reports right now.</li>';
        return;
    }

    filtered.forEach(function (report, index) {
        var li = document.createElement('li');
        li.innerHTML =
            '<span class="list-index">' + (index + 1) + '.</span>' +
            '<span class="dot ' + report.severity + '"></span>' +
            '<span class="list-area">' + (report.area_name || 'Unknown area') + '</span>' +
            '<span class="list-time">' + report.created_at + '</span>';
        listEl.appendChild(li);
    });
}

// Wire up the three severity sort/filter buttons
document.querySelectorAll('.sort-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
        var severity = btn.dataset.severity;

        if (activeFilter === severity) {
            // Clicking the already-active button turns the filter back off
            activeFilter = null;
            btn.classList.remove('active');
        } else {
            activeFilter = severity;
            document.querySelectorAll('.sort-btn').forEach(function (b) {
                b.classList.remove('active');
            });
            btn.classList.add('active');
        }

        renderList();
    });
});
