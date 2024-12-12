// Ensure that the HTML element with id "map" exists

document.addEventListener("DOMContentLoaded", function() {
    // Ensure that the HTML element with id "map" exists
    var mapElement = document.getElementById("map");
    
    
    if (!mapElement) {
        console.error("Element with id 'map' not found.");
        return;
    }

    var map = L.map("map").setView([38.29, 21.7946], 14);

    
    custom=L.ExtraMarkers.icon({
        icon: 'fa-number',
        markerColor: 'cyan',
        shape: 'circle',
        prefix: 'fa'
      });
    try{
      let projectName = document.getElementById("welcomecomp").innerText;
      if(projectName=="Signal Coverage - LoRA"){
        fetch('http://localhost:3000/api/measurements/lora')
        .then(response => response.json())
        .then(data => {
          data.forEach(point => {
            var marker = L.marker([point.latitude, point.longitude], {icon: custom}).addTo(map);
            marker.bindPopup(`RSSI: ${point.rssi}`).addEventListener('click', function() {
              marker.openPopup();
            });
          });
        })
        .catch(error => console.error('Error fetching data:', error));
      }
      else if(projectName=="Access Point Mapping - eduroam"){
        fetch('http://localhost:3000/api/measurements/wifi')
        .then(response => response.json())
        .then(data => {
          data.forEach(point => {
            var marker = L.marker([point.latitude, point.longitude], {icon: custom}).addTo(map);
            marker.bindPopup(`RSSI: ${point.rssi}`).addEventListener('click', function() {
              marker.openPopup();
            });
          });
        })
        .catch(error => console.error('Error fetching data:', error));
      }
    }
    catch(error){
      console.error('Error fetching data:', error);
      var marker = L.marker([38.28864841960415, 21.788658751750393],{icon:custom}).addTo(map);
      marker.bindPopup("AutoSense").addEventListener(this.onclick, function() {
          marker.bindPopup("AutoSense").openPopup();});
    }
    
    

   
      
   

        var layer1=L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 50,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'pk.eyJ1IjoiZ2RzdGVyZ2lvcG91bG9zIiwiYSI6ImNsdW1wdWxhYzB4ZmkyaWxuaDFjZjhoYnUifQ.M331BKPLXLd5K1jl6nFHcQ'
          }).addTo(map);
        
        var layer2 = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
          attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
          maxZoom: 50,
          id: 'mapbox/dark-v11',
          tileSize: 512,
          zoomOffset: -1,
          accessToken: 'pk.eyJ1IjoiZ2RzdGVyZ2lvcG91bG9zIiwiYSI6ImNsdW1wdWxhYzB4ZmkyaWxuaDFjZjhoYnUifQ.M331BKPLXLd5K1jl6nFHcQ'
        }).addTo(map);
            
        
          var layer3=L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 50,
            id: 'mapbox/satellite-v9',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'pk.eyJ1IjoiZ2RzdGVyZ2lvcG91bG9zIiwiYSI6ImNsdW1wdWxhYzB4ZmkyaWxuaDFjZjhoYnUifQ.M331BKPLXLd5K1jl6nFHcQ'
          }).addTo(map); 

        baseMap = {
            "Mapbox Satellite": layer3,
            "Mapbox Streets": layer1,
            "Mapbox Dark": layer2,

        };

        L.control.layers(baseMap).addTo(map);
});

    



