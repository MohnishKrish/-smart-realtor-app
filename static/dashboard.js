// dashboard.js
document.addEventListener('DOMContentLoaded', function() {
  // Chart.js trend chart
  const ctx = document.getElementById('trendChart');
  if (ctx) {
    const months = (typeof trendMonths !== 'undefined' && trendMonths.length) ? trendMonths : ['2020-01','2020-02','2020-03','2020-04','2020-05'];
    const prices = (typeof trendPrices !== 'undefined' && trendPrices.length) ? trendPrices : [15, 22, 33, 40, 55];
    new Chart(ctx.getContext('2d'), {
      type: 'line',
      data: {
        labels: months,
        datasets: [{
          label: 'Avg Predicted Price',
          data: prices,
          fill: true,
          backgroundColor: 'rgba(59,130,246,0.08)',
          borderColor: 'rgba(59,130,246,1)',
          tension: 0.3
        }]
      },
      options: {responsive:true, maintainAspectRatio:false}
    });
  }

  // Leaflet map
  if (typeof coords !== 'undefined' && document.getElementById('map')) {
    const [lat, lng] = coords;
    const map = L.map('map').setView([lat, lng], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // marker icon (if you have house-icon.png)
    const icon = L.icon({
      iconUrl: '/static/house-icon.png',
      iconSize: [36,36],
      iconAnchor: [18,36]
    });

    // if custom icon exists, use it; otherwise default
    let marker;
    fetch('/static/house-icon.png', {method:'HEAD'}).then(res=>{
      if (res.ok) marker = L.marker([lat,lng], {icon: icon}).addTo(map);
      else marker = L.marker([lat,lng]).addTo(map);
      marker.bindPopup("Selected Location").openPopup();
    }).catch(err=>{
      marker = L.marker([lat,lng]).addTo(map);
      marker.bindPopup("Selected Location").openPopup();
    });
  }
});