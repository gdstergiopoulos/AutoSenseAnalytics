SELECT R1.recvTimeTs, R1.recvTime,R1.attrName, R1.attrValue,R2.attrName, R2.attrValue,R3.attrName,R3.attrValue,R4.attrName,R4.attrValue
FROM `default`.AutoSenseAnalytics_Wifi_elenishome_rssi_bssid as R1 JOIN `default`.AutoSenseAnalytics_Wifi_elenishome_rssi_bssid as R2 JOIN `default`.AutoSenseAnalytics_Wifi_elenishome_rssi_bssid as R3 JOIN `default`.AutoSenseAnalytics_Wifi_elenishome_rssi_bssid as R4
WHERE R1.attrName="rssi" AND R2.attrName="macAddress" AND R3.attrName="location" AND R4.attrName="timestamp" AND R1.recvTimeTs=R2.recvTimeTs AND R1.recvTimeTs=R3.recvTimeTs AND R1.recvTimeTs=R4.recvTimeTs AND R2.recvTimeTs=R3.recvTimeTs AND R2.recvTimeTs=R4.recvTimeTs AND R3.recvTimeTs=R4.recvTimeTs ;

SELECT R1.recvTimeTs, R1.recvTime,R1.attrName, R1.attrValue,R2.attrName, R2.attrValue,R3.attrName,R3.attrValue,R4.attrName,R4.attrValue
FROM `default`.AutoSenseAnalytics_Wifi_elenishome_rssi_bssid as R1 JOIN `default`.AutoSenseAnalytics_Wifi_elenishome_rssi_bssid as R2 JOIN `default`.AutoSenseAnalytics_Wifi_elenishome_rssi_bssid as R3 JOIN `default`.AutoSenseAnalytics_Wifi_elenishome_rssi_bssid as R4
WHERE R1.attrName="rssi" AND R2.attrName="macAddress" AND R3.attrName="location" AND R4.attrName="timestamp" AND R1.recvTimeTs=R2.recvTimeTs AND R1.recvTimeTs=R3.recvTimeTs AND R1.recvTimeTs=R4.recvTimeTs AND R2.recvTimeTs=R3.recvTimeTs AND R2.recvTimeTs=R4.recvTimeTs AND R3.recvTimeTs=R4.recvTimeTs AND R4.attrValue>="2024-11-27T16:05:50.238Z" AND R4.attrValue<="2024-11-28T10:50:19.638Z" ;

AND R4.attrValue>="2024-11-27T10:50:19.638Z" AND R4.attrValue<="2024-11-28T10:50:19.638Z";