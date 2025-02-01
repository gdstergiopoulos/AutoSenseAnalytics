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
        fetch('/api/measurements/processed')
        .then(response => response.json())
        .then(data => {
            var markersLayer = L.layerGroup();
            var heatLayer = L.layerGroup();
            var overlappingPoints = [];
            let nonOverlappingPoints=[];

          //   data.forEach(point => {
          //     point.latitude += (Math.random() - 0.5) * 0.00001; // Small latitude jitter
          //     point.longitude += (Math.random() - 0.5) * 0.00001; // Small longitude jitter
          // });
          

            data.forEach((point, index) => {
              for (let i = index + 1; i < data.length; i++) {
                if (point.latitude === data[i].latitude && point.longitude === data[i].longitude) {
                  overlappingPoints.push(point);
                  break;
                }
              }
            });

            var uniquePoints = {};

            overlappingPoints.forEach(point => {
              var key = `${point.latitude},${point.longitude}`;
              if (!uniquePoints[key]) {
                uniquePoints[key] = { ...point, count: 1 };
              } else {
                uniquePoints[key].rssi += point.rssi;
                uniquePoints[key].count += 1;
              }
            });

            var averagedPoints = Object.values(uniquePoints).map(point => ({
              latitude: point.latitude,
              longitude: point.longitude,
              rssi: point.rssi / point.count
            }));

            data = data.filter(point => !overlappingPoints.includes(point)).concat(averagedPoints);
            
            data.forEach((point, index) => {
              if (!overlappingPoints.includes(point)) {
                nonOverlappingPoints.push(point);
              }
            });

            console.log("Overlapping Points:", overlappingPoints);
            console.log("Non-Overlapping Points:", nonOverlappingPoints);
            console.log("averagedPoints:", averagedPoints);

            var validPoints = nonOverlappingPoints.concat(averagedPoints);
            console.log("Valid Points:", validPoints);
            
            validPoints.forEach(point => {
            var marker = L.marker([point.latitude, point.longitude], {icon: custom}).addTo(markersLayer);
            marker.bindPopup(`RSSI: ${point.rssi}, Lat: ${point.latitude}, Lon: ${point.longitude},norm: ${-(point.rssi+120)/(-63)}`).addEventListener('click', function() {
              marker.openPopup();
            });
            });


            var rssiValues = validPoints.map(point => point.rssi).filter(rssi => rssi > -200);
            var minRssi = Math.min(...rssiValues);
            var maxRssi = Math.max(...rssiValues);
            console.log(minRssi, maxRssi);

            var heatData = validPoints.map(point => {
              var normalizedRssi = (point.rssi-minRssi) / (maxRssi - minRssi);
              return [point.latitude, point.longitude, normalizedRssi];
            });

            console.log(heatData)
            var heat = L.heatLayer(heatData, {
            radius: 25,
            blur: 15,
            maxZoom: 17
            }).addTo(heatLayer);

            markersLayer.addTo(map);
            heatLayer.addTo(map);

            var overlayMaps = {
            "Markers": markersLayer,
            "Heatmap": heatLayer
            };

            L.control.layers(baseMap, overlayMaps).addTo(map);
            
        })
        .catch(error => console.error('Error fetching data:', error));
      }
      else if(projectName=="Access Point Mapping - eduroam"){
        fetch('/api/measurements/wifi')
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
      else if(projectName=="3D Reconstruction"){
        // fetch('/api/photos')
        // .then(response => response.json())
        // .then(data => {
        //     data.forEach(entry => {
        //         console.log(entry);
        //         // Create a marker for each photo
        //         const marker = L.marker([entry.lat, entry.lon]).addTo(map);

        //         // Bind a popup with the photo and metadata
        //         marker.bindPopup(`
        //             <b>Timestamp:</b> ${new Date(entry.timestamp).toLocaleString()}<br>
        //             <img src="http://localhost:5000/photo/7" class="popup-img" alt="Photo">
        //         `);
        //     });
        // })
        // .catch(error => {
        //     console.error('Error fetching metadata:', error);
        // });

        //for camera controller

        fetch('http://150.140.186.118:4943/api/photos')
        .then(response => response.json())
        .then(data => {
            data.forEach(entry => {
                console.log(entry);
                // Create a marker for each photo
                const marker = L.marker([entry.latitude, entry.longitude]).addTo(map);

                // Bind a popup with the photo and metadata
                marker.bindPopup(`
                    <b>Timestamp:</b> ${entry.timestamp}<br>
                    <b>Acc X:</b> ${entry.accx}<br>
                    <b>Acc Y:</b> ${entry.accy}<br>
                    <b>Acc Z:</b> ${entry.accz}<br>
                    <img src="http://150.140.186.118:4943/photo/${entry.id}" class="popup-img" alt="Photo">
                `);
            });
        })
      }
      else if (projectName=="Live Status"){
        map.setZoom(12);
        let markers = {};
        const carIds = [0,1, 2, 3, 4, 5, 6, 7];
        const colors = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown"];
    
        function updateMarker(carId, color) {
            fetch(`/api/demo/measurements/car/${carId}`)
                .then(response => response.json())
                .then(data => {
                    let lat = data.location.value.coordinates[1];
                    let lon = data.location.value.coordinates[0];
    
                    if (markers[carId]) {
                        markers[carId].setLatLng([lat, lon]);
                    } else {
                        markers[carId] = L.circleMarker([lat, lon], {
                            color: color,
                            radius: 8
                        }).addTo(map);
                    }
    
                    markers[carId].bindPopup(`
                        <b>Car ID:</b> ${carId}<br>
                        <b>Battery:</b> ${data.battery.value}%<br>
                        <b>Camera:</b> <a href="${data.camera.value}" target="_blank">View Photo</a><br>
                        <b>IMU Roughness:</b> ${data.imu_roughness.value}<br>
                        <b>RSSI Cellular:</b> ${data.rssi_cellular.value}<br>
                        <b>RSSI LoRa:</b> ${data.rssi_lora.value}<br>
                        <b>RSSI WiFi:</b> ${data.rssi_wifi.value}<br>
                        <b>Speed:</b> ${data.speed.value} km/h<br>
                        <b>Timestamp:</b> ${new Date(data.timestamp.value).toLocaleString()}
                    `);
    
                    markers[carId].on('click', function() {
                        markers[carId].openPopup();
                    });
                })
                .catch(error => console.error(`Error fetching data for car ${carId}:`, error));
        }
    
        function updateAllMarkers() {
            carIds.forEach((carId, index) => {
                updateMarker(carId, colors[index]);
            });
        }
    
        updateAllMarkers(); // Initial fetch
        setInterval(updateAllMarkers, 2000); // Refresh every 2 seconds
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
            "Mapbox Dark": layer2,
            "Mapbox Streets": layer1,

        };
        let projectName = document.getElementById("welcomecomp").innerText;
        if(projectName!="Signal Coverage - LoRA"){
            L.control.layers(baseMap).addTo(map);
        }
        // L.control.layers(baseMap).addTo(map);
});

    



