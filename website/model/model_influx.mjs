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

export async function getMeasurements4G(location) {
    console.log("getMeasurements4G", location)
    const influxdb_url = "http://150.140.186.118:8086"
    const bucket = "AutoSenseAnalytics_4G"
    const org = "students"
    const token = "FcqYDwZ0_KMXrbp8z-2KjcgNQKSUOX_W1hPEqdrxuQ-LwB2I_7Vnpn_AOahhY0BkoNhQBOmYYp3Y9bAxLyDl7A=="

    const client = new InfluxDB({ url: influxdb_url, token });

    let withGps = [];
    let allMeasurements = [];
    const queryApi = client.getQueryApi(org);
    
    try {
        // Time range in UTC
        // const start = '2024-12-10T10:50:33Z';
        // const stop = '2024-12-10T11:09:16Z';
        let start = '2025-02-04T10:36:22.000Z';
        let stop = '2025-02-04T12:24:34.000Z';
        if (location==="Center") {
            start = '2025-02-04T10:36:22.000Z';
            stop = '2025-02-04T12:24:34.000Z';
        }
        else if(location==="Uni"){
            start = '2025-02-05T10:50:00.000Z'; 
            stop=   '2025-02-05T11:56:42.000Z';
        }
        else if(location==="All"){
            start = '2025-02-04T10:36:22.000Z';
            stop = '2025-02-05T11:56:42.000Z';
        }
            

        // Flux query
       
        const query = `
            from(bucket: "${bucket}")
                |> range(start: ${start}, stop: ${stop})
                |> filter(fn: (r) => r._measurement == "4G_rssi")
                |> filter(fn: (r) => r._field == "rssi" or r._field == "latitude" or r._field == "longitude" or r._field == "speed" or r._field == "altitude")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> keep(columns: ["rssi", "latitude", "longitude","speed","altitude","_time"])
                |> group(columns: ["rssi", "latitude", "longitude","speed","altitude","_time"])
                |> filter(fn: (r) => r.longitude != 0.35)
                |> distinct()
        `;
        let localwithGps = [];
        let all=[];
        // Execute query and process results
        await new Promise((resolve, reject) => {
            queryApi.queryRows(query, {
            next: (row, tableMeta) => {
                const record = tableMeta.toObject(row);
                // console.log(record)
                const {table, _value,result, ...cleanRecord}=record;
                if (cleanRecord.latitude !== 0.0 && cleanRecord.longitude !== 0.0) {
                localwithGps.push(cleanRecord);
                }
                all.push(cleanRecord);
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

export async function getMeasurementsIMU() {
    const influxdb_url = "http://150.140.186.118:8086"
    // const bucket = "AutoSenseAnalytics_imu_avg"
    // const bucket = "AutoSenseAnalytics_imu_std"
    // const bucket = "AutoSenseAnalytics_imu_max"
    const bucket = "AutoSenseAnalytics_imu_fft_score"
    const org = "students"
    const token = "kmVB5CFkQCqOSHpLPYc8N0C46IG_mAu9LnT1LdKGYC8k6_DlpUPAs31n9fP4sJaXjLJkyZ_Y9bvceMy5B3wobQ=="

    const client = new InfluxDB({ url: influxdb_url, token });

    let withGps = [];
    let allMeasurements = [];
    const queryApi = client.getQueryApi(org);
    
    try {
        
        const start = '2025-02-09T15:55:22.000Z';
        const stop = '2025-02-09T16:31:02.000Z';

        // Flux query
        // const query = `
        //     from(bucket: "${bucket}")
        //         |> range(start: ${start}, stop: ${stop})
        //         |> filter(fn: (r) => r._measurement == "imu_avg")
        //         |> filter(fn: (r) => r._field == "acc_x_max" or r._field == "acc_y_max" or r._field == "acc_z_max" or r._field=="altitude" or r._field=="speed" or r._field=="latitude" or r._field=="longitude")
        //         |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        //         |> keep(columns: ["_time", "acc_x_max", "acc_y_max", "acc_z_max", "altitude", "speed", "latitude", "longitude"])
        // `;

        // Flux query
        const query = `
            from(bucket: "${bucket}")
                |> range(start: ${start}, stop: ${stop})
                |> filter(fn: (r) => r._measurement == "imu_fft_score")
                |> filter(fn: (r) => r._field == "roughness" or r._field=="altitude" or r._field=="speed" or r._field=="latitude" or r._field=="longitude")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> keep(columns: ["_time","roughness", "altitude", "speed", "latitude", "longitude"])
        `;

        let localwithGps = [];
        let all=[];
        // Execute query and process results
        await new Promise((resolve, reject) => {
            queryApi.queryRows(query, {
            next: (row, tableMeta) => {
                const record = tableMeta.toObject(row);
                // console.log(record)
                const {table, _value,result, ...cleanRecord}=record;
                if (cleanRecord.latitude !== 0.0 && cleanRecord.longitude !== 0.0) {
                localwithGps.push(cleanRecord);
                }
                all.push(cleanRecord);
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