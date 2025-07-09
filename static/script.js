var map = L.map('harita').setView([39.0, 35.0], 6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
}).addTo(map);

var redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

var yellowIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

var defaultIcon = new L.Icon.Default();

fetch("/deprem")
  .then(res => res.json())
  .then(veriler => {
    veriler.forEach(veri => {
      const magnitude = parseFloat(veri.ML);
      let icon = defaultIcon;
      
      if (magnitude >= 5) {
        icon = redIcon;
        if ("Notification" in window && Notification.permission === "granted") {
          new Notification("⚠️ Şiddetli Deprem", {
            body: veri.Yer + " - ML: " + veri.ML,
          });
        }
      } else if (magnitude >= 3.5) {
        icon = yellowIcon;
      }

      L.marker([veri.Enlem, veri.Boylam], { icon: icon })
        .addTo(map)
        .bindPopup(`
          <b>${veri.Yer}</b><br>
          Şiddet: ${veri.ML}<br>
          ${veri.Tarih}
        `);
    });
  });

let mysBtn = document.getElementById('scrollbuttonid');

window.addEventListener('scroll', function () {
    if (document.body.scrollTop > 0
        || document.documentElement.scrollTop > 20) {
        mysBtn.style.display = 'block';
    } else {
        mysBtn.style.display = 'none';
    }
});
