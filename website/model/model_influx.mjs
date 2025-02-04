import { InfluxDB } from '@influxdata/influxdb-client';

export async function getMeasurementsWifi() {
    
    const influxdb_url = "http://150.140.186.118:8086"
    const bucket = "AutoSenseAnalytics"
    const org = "students"
    const token = "oOsRHLaYY8_Wp_89wMVENUlChhoGpJ4x9VwjXDQK69Pb3IYTs0Mw9XsfXl5aOWd7MuX82DtAxiChfajweZIWFA=="

    const client = new InfluxDB({ url: influxdb_url, token });

    let withGps = [];
    let allMeasurements = [];
    const queryApi = client.getQueryApi(org);
    
    try {
        // Time range in UTC
        const start = '2024-12-06T10:19:35Z';
        const stop = '2024-12-06T10:48:57Z';

        // Flux query
        const query = `
            from(bucket: "${bucket}")
                |> range(start: ${start}, stop: ${stop})
                |> filter(fn: (r) => r._measurement == "rssi_bssid")
                |> filter(fn: (r) => r._field == "rssi" or r._field == "mac_address" or r._field == "latitude" or r._field == "longitude")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> keep(columns: ["_time", "rssi", "mac_address", "latitude", "longitude"])
        `;
        let localwithGps = [];
        let all=[];
        // Execute query and process results
        await new Promise((resolve, reject) => {
            queryApi.queryRows(query, {
            next: (row, tableMeta) => {
                const record = tableMeta.toObject(row);
                if (record.latitude !== 0.0 && record.longitude !== 0.0) {
                localwithGps.push(record);
                }
                all.push(record);
            },
            error: (error) => {
                console.error('Error querying data:', error);
                reject(error);
            },
            complete: () => {
                withGps = localwithGps;
                allMeasurements = all;
                resolve();
            },
            });
        });
        
        return withGps;
    } catch (error) {
        console.error(`Error retrieving data: ${error.message}`);
    }
}

export async function getMeasurementsLoRa() {
    const influxdb_url = "http://150.140.186.118:8086"
    const bucket = "AutoSenseAnalytics_LoRa"
    const org = "students"
    const token = "gyQjt9HYA8gzzQG1EjpW8GZV7RtbYBulx6UuCLRZUbqCagI9FR5FziuKy4CRIfTS-MY8t_z_-8g70v1ldFuriw=="

    const client = new InfluxDB({ url: influxdb_url, token });

    let withGps = [];
    let allMeasurements = [];
    const queryApi = client.getQueryApi(org);
    
    try {
        // Time range in UTC
        // const start = '2024-12-10T10:50:33Z';
        // const stop = '2024-12-10T11:09:16Z';

        const start = '2024-12-17T09:30:33Z';
        const stop = '2024-12-17T13:14:13.601Z';

        // Flux query
        const query = `
            from(bucket: "${bucket}")
                |> range(start: ${start}, stop: ${stop})
                |> filter(fn: (r) => r._measurement == "LoraMeasurement")
                |> filter(fn: (r) => r._field == "rssi" or r._field == "latitude" or r._field == "longitude")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> keep(columns: ["_time", "rssi", "latitude", "longitude"])
        `;
        let localwithGps = [];
        let all=[];
        // Execute query and process results
        await new Promise((resolve, reject) => {
            queryApi.queryRows(query, {
            next: (row, tableMeta) => {
                const record = tableMeta.toObject(row);
                if (record.latitude !== 0.0 && record.longitude !== 0.0) {
                localwithGps.push(record);
                }
                all.push(record);
            },
            error: (error) => {
                console.error('Error querying data:', error);
                reject(error);
            },
            complete: () => {
                withGps = localwithGps;
                allMeasurements = all;
                resolve();
            },
            });
        });
        // client.close();
        return withGps;
    } catch (error) {
        console.error(`Error retrieving data: ${error.message}`);
    }
}

export async function getMeasurementsLoRaproc() {
    console.log("getMeasurementsLoRaproc")
    const influxdb_url = "http://150.140.186.118:8086"
    const bucket = "testproc"
    const org = "students"
    const token = "Om7csZjKnfCnYUXFZRYo1BSo7TeXDikSkAAZcWv8hqJqzMKMbFnKc0WqcbaJ69FIk9R-E88JU2OCW8WbacJaTA=="

    const client = new InfluxDB({ url: influxdb_url, token });

    let withGps = [];
    let allMeasurements = [];
    const queryApi = client.getQueryApi(org);
    
    try {
        // Time range in UTC
        // const start = '2024-12-10T10:50:33Z';
        // const stop = '2024-12-10T11:09:16Z';

        const start = '2024-12-17T09:30:33Z';
        const stop = '2024-12-17T13:14:13.601Z';

        // Flux query
       
        const query = `
            from(bucket: "${bucket}")
                |> range(start: -2y)
                |> filter(fn: (r) => r._measurement == "LoraMeasurement_proc")
                |> filter(fn: (r) => r._field == "rssi" or r._field == "latitude" or r._field == "longitude")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> keep(columns: ["rssi", "latitude", "longitude"])
                |> group(columns: ["rssi", "latitude", "longitude"])
                |> distinct()
        `;
        let localwithGps = [];
        let all=[];
        // Execute query and process results
        await new Promise((resolve, reject) => {
            queryApi.queryRows(query, {
            next: (row, tableMeta) => {
                const record = tableMeta.toObject(row);
                if (record.latitude !== 0.0 && record.longitude !== 0.0) {
                localwithGps.push(record);
                }
                all.push(record);
            },
            error: (error) => {
                console.error('Error querying data:', error);
                reject(error);
            },
            complete: () => {
                withGps = localwithGps;
                allMeasurements = all;
                resolve();
            },
            });
        });
        // client.close();
        return withGps;
    } catch (error) {
        console.error(`Error retrieving data: ${error.message}`);
    }
}

export async function getMeasurements4G() {
    console.log("getMeasurements4G")
    const influxdb_url = "http://150.140.186.118:8086"
    const bucket = "AutoSenseAnalytics4G"
    const org = "students"
    const token = "fRML93YyZozXXQI-torGL3PbHXSq04sAbweQTtb4ZKfWGushczd_jnjvxzhgNBHvBIUEQkmHQDicg4tjoTWDhg=="

    const client = new InfluxDB({ url: influxdb_url, token });

    let withGps = [];
    let allMeasurements = [];
    const queryApi = client.getQueryApi(org);
    
    try {
        // Time range in UTC
        // const start = '2024-12-10T10:50:33Z';
        // const stop = '2024-12-10T11:09:16Z';

        const start = '2025-02-04T10:36:22.000Z';
        const stop = '2025-02-04T12:24:34.000Z';

        // Flux query
       
        const query = `
            from(bucket: "${bucket}")
                |> range(start: ${start}, stop: ${stop})
                |> filter(fn: (r) => r._measurement == "4G_rssi")
                |> filter(fn: (r) => r._field == "rssi" or r._field == "latitude" or r._field == "longitude" or r._field == "speed" or r._field == "altitude")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> keep(columns: ["rssi", "latitude", "longitude","speed","altitude"])
                |> group(columns: ["rssi", "latitude", "longitude","speed","altitude"])
                |> distinct()
        `;
        let localwithGps = [];
        let all=[];
        // Execute query and process results
        await new Promise((resolve, reject) => {
            queryApi.queryRows(query, {
            next: (row, tableMeta) => {
                const record = tableMeta.toObject(row);
                if (record.latitude !== 0.0 && record.longitude !== 0.0) {
                localwithGps.push(record);
                }
                all.push(record);
            },
            error: (error) => {
                console.error('Error querying data:', error);
                reject(error);
            },
            complete: () => {
                withGps = localwithGps;
                allMeasurements = all;
                resolve();
            },
            });
        });
        // client.close();
        return withGps;
    } catch (error) {
        console.error(`Error retrieving data: ${error.message}`);
    }
}