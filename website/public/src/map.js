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

    //icon: `<div style="font-size:12px; font-weight:bold;">${rssi}</div>` //how to put number on marker
    function getIconByRSSI(rssi) {
            if(rssi>=-81 && rssi<=-71){
              return L.ExtraMarkers.icon({
                icon: 'fa-number',
                markerColor: 'blue',
                shape: 'circle',
                prefix: 'fa'
              });
            }
            else if(rssi>=-70 && rssi<=-61){
              return L.ExtraMarkers.icon({
                icon: 'fa-number',
                markerColor: 'orange',
                shape: 'circle',
                prefix: 'fa'
            });
          }
          else if(rssi>=-60 && rssi<=-51){
            return L.ExtraMarkers.icon({
              icon: 'fa-number',
              markerColor: 'red',
              shape: 'circle',
              prefix: 'fa'
          });
          } 
        }

    function getIconByRoughness(roughness) {
          if(roughness<=7.5){
            return L.ExtraMarkers.icon({
              icon: 'fa-number',
              markerColor: 'green',
              shape: 'circle',
              prefix: 'fa'
            });
          }
          else if(roughness>7.5 && roughness<=14.5){
            return L.ExtraMarkers.icon({
              icon: 'fa-number',
              markerColor: 'orange',
              shape: 'circle',
              prefix: 'fa'
          });
        }
        else if(roughness>=14.5){
          return L.ExtraMarkers.icon({
            icon: 'fa-number',
            markerColor: 'red',
            shape: 'circle',
            prefix: 'fa'
        });
        } 
      }
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
            marker.bindPopup(`<b>RSSI:</b> ${point.rssi}<br>
                               <b>Lat:</b> ${point.latitude}<br>
                               <b>Lon:</b> ${point.longitude}<br>
                              <b> norm:</b> ${-(point.rssi+120)/(-63)}`).addEventListener('click', function() {
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
            // markersLayer.addTo(map);
            // heatLayer.addTo(map);
             // GET THE BOUNDS FROM THE PYTHON SCRIPT
        let imageBounds = [[38.284498332777595, 21.7837], [38.2895,21.791402567522507]];
        let imageOverlay=L.imageOverlay('/media/rssi_overlay_colored.png', imageBounds,{opacity:0.7 }).addTo(map);
        //GET THE COLORBAR FROM THE PYTHON SCRIPT
        // Add a custom colorbar (similar to Branca's functionality)
        var legend = L.control({ position: "bottomright" });
        legend.onAdd = function (map) {
            var div = L.DomUtil.create("div", "legend");
            div.innerHTML = `
                <div class="legend-title" style="color:black">RSSI Signal Strength</div>
                <div style="width: 200px; height: 15px; background: linear-gradient(to right, blue, white, red);"></div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color:black">-120 dBm</span>
                    <span style="color:black">-58 dBm</span>
                </div>
            `;
            return div;
        };
        legend.addTo(map);
        var overlayMaps = {
            "Markers": markersLayer,
            "Alt. Heatmap": heatLayer,
            "Heatmap": imageOverlay
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
      else if(projectName=="Signal Coverage - 4G"){
        let markersLayer=L.layerGroup();
        let pathLayer=L.layerGroup();
        let pathUniLayer=L.layerGroup();
        let markerCoords=[];
        let markerCoordsUni=[];
        let lastpoint;
        let distance;
        function getDistance(coord1, coord2) {
          var R = 6371e3; // Earth radius in meters
          var lat1 = (coord1[0] * Math.PI) / 180;
          var lat2 = (coord2[0] * Math.PI) / 180;
          var deltaLat = lat2 - lat1;
          var deltaLng = ((coord2[1] - coord1[1]) * Math.PI) / 180;
          var a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
                  Math.cos(lat1) * Math.cos(lat2) *
                  Math.sin(deltaLng / 2) * Math.sin(deltaLng / 2);
          var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
          return R * c; // Distance in meters
      }

        map.setView([38.246739, 21.73776]);
        fetch('/api/measurements/4G')
        .then(response => response.json())
        .then(data => {
          data.forEach(point => {
            var marker = L.marker([point.latitude, point.longitude], {icon: getIconByRSSI(point.rssi)}).addTo(markersLayer);
            if(point._time>="2025-02-05T10:51:20Z")
            {
              markerCoordsUni.push([point.latitude, point.longitude]);
            }
            else{

              //THE CODE TO FILTER JUMPS STARTS HERE

              // if(markerCoords.length!=0){
              //   lastpoint=markerCoords[markerCoords.length-1];
              //   console.log(lastpoint);
              //   distance = getDistance(lastpoint, [point.latitude, point.longitude]);
              //   if (distance < 1830) {
              //     markerCoords.push([point.latitude, point.longitude]);
              //       }
              //     }
              // else{
              //   markerCoords.push([point.latitude, point.longitude]);
              // }
              // }

              //THE CODE TO FILTER JUMPS ENDS HERE
              markerCoords.push([point.latitude, point.longitude]);
            }
            
            marker.bindPopup(`<b>RSSI</b>: ${point.rssi}<br>
                              <b>Altitude</b>: ${point.altitude}<br>
                              <b>Speed</b>: ${point.speed}<br>
                              <b>Timestamp</b>: ${point._time}`).addEventListener('click', function() {
              marker.openPopup();
            });
          });

          let polyline=L.polyline(markerCoords,{color:'blue'}).addTo(pathLayer);
          let unipolyline=L.polyline(markerCoordsUni,{color:'red'}).addTo(pathUniLayer);

          let imageBounds = [[38.24049463154385, 21.7265], [38.2566,21.762712070690228]];
        let imageOverlay=L.imageOverlay('/media/4g_rssi_overlay_colored.png', imageBounds,{opacity:0.7 }).addTo(map);

        let imageUniBounds = [[38.27969503167722, 21.7782], [38.2946,21.7945054351450488]];
        let imageUniOverlay=L.imageOverlay('/media/4g_uni_rssi_overlay_colored.png', imageUniBounds,{opacity:0.7 }).addTo(map);

        //GET THE COLORBAR FROM THE PYTHON SCRIPT
        // Add a custom colorbar (similar to Branca's functionality)
        var legend = L.control({ position: "bottomright" });
        legend.onAdd = function (map) {
            var div = L.DomUtil.create("div", "legend");
            div.innerHTML = `
                <div class="legend-title" style="color:black">RSSI Signal Strength</div>
                <div style="width: 200px; height: 15px; background: linear-gradient(to right, blue, white, red);"></div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color:black">-81 dBm</span>
                    <span style="color:black">-51 dBm</span>
                </div>
            `;
            return div;
        };
        legend.addTo(map);
        var overlayMaps = {
            "Markers": markersLayer,
            "Path": pathLayer,
            "Uni Path": pathUniLayer,
            "Heatmap Center": imageOverlay,
            "Heatmap Uni": imageUniOverlay
            };
        L.control.layers(baseMap, overlayMaps).addTo(map);
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
                    <b>ID:</b> ${entry.id}<br>
                    <a href="http://150.140.186.118:4943/photo/${entry.id}"><img src="http://150.140.186.118:4943/photo/${entry.id}" class="popup-img" alt="Photo"></a>
                `);
            });
        })
      }
      else if (projectName=="Live Status"){
    map.setZoom(12);
    let markers = {};
    const carIds = [0,1, 2, 3, 4, 5, 6, 7];
    const colors = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "black"];
    const vehicletype= ["car","car","car","car","car","car","car","bus"];
    function getCustomIcon(color,vehicletype) {
        return L.ExtraMarkers.icon({
          icon: `fa-${vehicletype}`,
          markerColor: color,
          shape: 'circle',
          prefix: 'fa'
        });
    }
    function updateMarker(carId, color,vehicletype) {
        fetch(`/api/demo/measurements/car/${carId}`)
            .then(response => response.json())
            .then(data => {
                let lat = data.location.value.coordinates[1];
                let lon = data.location.value.coordinates[0];
                if (markers[carId]) {
                    markers[carId].setLatLng([lat, lon]);
                } else {
                    markers[carId] = L.marker([lat, lon], { icon: getCustomIcon(color,vehicletype) }).addTo(map);
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
            updateMarker(carId, colors[index],vehicletype[index]);
        });
    }
    updateAllMarkers(); // Initial fetch
    setInterval(updateAllMarkers, 2000); // Refresh every 2 seconds
      }
      else if(projectName=="Contact Us"){
    var marker = L.marker([38.28864841960415, 21.788658751750393],{icon:custom}).addTo(map);
    marker.bindPopup("AutoSense").addEventListener(this.onclick, function() {
        marker.bindPopup("AutoSense").openPopup();});
      }
      else if (projectName == "Road Roughness") {
        map.setView([38.259933, 21.742374], 13);
        let markersLayer = L.layerGroup();
        let markerCluster = L.markerClusterGroup({ maxClusterRadius: 40, disableClusteringAtZoom: 15 });
        let heatLayer = L.layerGroup();
        let photoLayer = L.layerGroup();
    
        // Fetch IMU measurements
        fetch('/api/measurements/imu')
            .then(response => response.json())
            .then(data => {
                let roughnessScores = data.map(point => point.roughness);
                let minRoughness = Math.min(...roughnessScores);
                let maxRoughness = Math.max(...roughnessScores);
                let minDistanceThreshold = 0.0001;
    
                function filterClosePoints(points, minDistance) {
                    let filteredPoints = [];
                    points.forEach(point => {
                        let isFarEnough = filteredPoints.every(filteredPoint => {
                            let dLat = point.latitude - filteredPoint.latitude;
                            let dLng = point.longitude - filteredPoint.longitude;
                            let distance = Math.sqrt(dLat * dLat + dLng * dLng);
                            return distance > minDistance;
                        });
                        if (isFarEnough) {
                            filteredPoints.push(point);
                        }
                    });
                    return filteredPoints;
                }
    
                let filteredData = filterClosePoints(data, minDistanceThreshold);
    
                let heatData = filteredData.map(point => {
                    let normalizedRoughness = (point.roughness - minRoughness) / (maxRoughness - minRoughness);
                    return [point.latitude, point.longitude, normalizedRoughness];
                });
    
                let heat = L.heatLayer(heatData, {
                    radius: 30,
                    blur: 20,
                    maxZoom: 17
                }).addTo(heatLayer);
    
                data.forEach(point => {
                    let marker = L.marker([point.latitude, point.longitude], { icon: getIconByRoughness(point.roughness) });
                    marker.bindPopup(`Roughness: ${point.roughness}`);
                    markerCluster.addLayer(marker);
                    markersLayer.addLayer(marker);
                });
    
                heatLayer.addTo(map);
            })
            .catch(error => console.error('Error fetching IMU data:', error));
    
        // Fetch Photo Data
        fetch('http://150.140.186.118:4943/api/photos')
            .then(response => response.json())
            .then(data => {
                data.forEach(entry => {
                    let marker = L.marker([entry.latitude, entry.longitude]);
                    marker.bindPopup(`
                        <b>Timestamp:</b> ${entry.timestamp}<br>
                        <b>Acc X:</b> ${entry.accx}<br>
                        <b>Acc Y:</b> ${entry.accy}<br>
                        <b>Acc Z:</b> ${entry.accz}<br>
                        <b>ID:</b> ${entry.id}<br>
                        <a href="http://150.140.186.118:4943/photo/${entry.id}" target="_blank">
                            <img src="http://150.140.186.118:4943/photo/${entry.id}" class="popup-img" style="width:100px;height:auto;" alt="Photo">
                        </a>
                    `);
                    photoLayer.addLayer(marker);
                });
                // Add overlay layers control
                  var overlayMaps = {
                    "Markers": markersLayer,
                    "Cluster": markerCluster,
                    "Heatmap": heatLayer,
                    "Photos": photoLayer
                };
            
                L.control.layers(baseMap, overlayMaps).addTo(map);
            })
            .catch(error => console.error('Error fetching photo data:', error));
    
        
    }
    }
    catch(error){
      console.error('Error fetching data:', error);
      
      // var marker = L.marker([38.28864841960415, 21.788658751750393],{icon:custom}).addTo(map);
      // marker.bindPopup("AutoSense").addEventListener(this.onclick, function() {
      //     marker.bindPopup("AutoSense").openPopup();});
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

          var layer4=L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            maxZoom: 17,
            attribution: 'Map data: © OpenStreetMap contributors, SRTM'
        }).addTo(map);


        let baseMap = {
            "Elevation Map": layer4,
            "Mapbox Satellite": layer3,
            "Mapbox Dark": layer2,
            "Mapbox Streets": layer1,
        };
        let projectName = document.getElementById("welcomecomp").innerText;
        if(projectName!="Signal Coverage - LoRA" && projectName!="Signal Coverage - 4G" && projectName!="Road Roughness"){
            L.control.layers(baseMap).addTo(map);
        }
        // L.control.layers(baseMap).addTo(map);
});
