/*
  Replace NWKSKEY, APPSKEY, DEVADDR

  Reference: https://github.com/goodcheney/ttn_mapper/blob/master/gps_shield
*/

#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <SoftwareSerial.h>
#include <TinyGPS.h>

TinyGPS gps;
SoftwareSerial ss(3, 4); // Arduino RX (D3) <-> GPS_TX, Arduino TX (D4) <-> GPS_RX

static void smartdelay(unsigned long ms);

unsigned int count = 1; // Times counter

String datastring1 = "";
String datastring2 = "";
String datastring3 = "";
uint8_t datasend[20]; // Used to store GPS data for uploading

char gps_lat[20] = {"\0"}; // Latitude
char gps_lon[20] = {"\0"}; // Longitude
char gps_alt[20] = {"\0"}; // Altitude
float flat, flon, falt;

static uint8_t mydata[] = "Hello, world!"; // For testing purposes

/*
  LoRaWAN NwkSKey, network session key
*/
static const PROGMEM u1_t NWKSKEY[16] = { 0xac, 0x98, 0x60, 0xd5, 0xb8, 0x96, 0x43, 0x0f, 0x7a, 0x07, 0xbe, 0x76, 0x9b, 0x2a, 0x40, 0xe5 };

/*
  LoRaWAN AppSKey, application session key
*/
static const u1_t PROGMEM APPSKEY[16] = { 0xc1, 0x17, 0x33, 0xc5, 0x2d, 0x51, 0x3c, 0x35, 0x40, 0xde, 0xd2, 0xf0, 0x5f, 0x49, 0xc6, 0xe6 };

/*
  LoRaWAN end-device address (DevAddr)
*/
static const u4_t DEVADDR = 0x260111D1;

void os_getArtEui (u1_t* buf) { }
void os_getDevEui (u1_t* buf) { }
void os_getDevKey (u1_t* buf) { }

static osjob_t initjob, sendjob, blinkjob;

/*
  Schedule TX every this many seconds.
*/
const unsigned TX_INTERVAL = 10;

// Pin mapping
const lmic_pinmap lmic_pins = {
  .nss = 10,
  .rxtx = LMIC_UNUSED_PIN,
  .rst = 9,
  .dio = {2, 6, 7}
};

void do_send(osjob_t* j){
  // Check if there is not a current TX/RX job running
  if (LMIC.opmode & OP_TXRXPEND) {
    Serial.println("OP_TXRXPEND, not sending");
  } else {
    GPSRead();
    GPSWrite();

    // Prepare upstream data transmission at the next possible time.
    LMIC_setTxData2(1, datasend, sizeof(datasend) - 1, 0);
    Serial.println("Packet queued");
  } 
}

void onEvent(ev_t ev) {
  Serial.print(os_getTime());
  Serial.print(": ");
  Serial.println(ev);
  switch (ev) {
    case EV_SCAN_TIMEOUT:
      Serial.println("EV_SCAN_TIMEOUT");
      break;
    case EV_BEACON_FOUND:
      Serial.println("EV_BEACON_FOUND");
      break;
    case EV_BEACON_MISSED:
      Serial.println("EV_BEACON_MISSED");
      break;
    case EV_BEACON_TRACKED:
      Serial.println("EV_BEACON_TRACKED");
      break;
    case EV_JOINING:
      Serial.println("EV_JOINING");
      break;
    case EV_JOINED:
      Serial.println("EV_JOINED");
      break;
    case EV_RFU1:
      Serial.println("EV_RFU1");
      break;
    case EV_JOIN_FAILED:
      Serial.println("EV_JOIN_FAILED");
      break;
    case EV_REJOIN_FAILED:
      Serial.println("EV_REJOIN_FAILED");
      break;
    case EV_TXCOMPLETE:
      Serial.println("EV_TXCOMPLETE (includes waiting for RX windows)");
      if (LMIC.dataLen) {
        // Data received in RX slot after TX
        Serial.print("Data Received: ");
        Serial.write(LMIC.frame + LMIC.dataBeg, LMIC.dataLen);
        Serial.println();
        printRSSIandSNR(); // Print RSSI and SNR
      }
      os_setTimedCallback(&sendjob, os_getTime() + sec2osticks(TX_INTERVAL), do_send);
      break;
    case EV_LOST_TSYNC:
      Serial.println("EV_LOST_TSYNC");
      break;
    case EV_RESET:
      Serial.println("EV_RESET");
      break;
    case EV_RXCOMPLETE:
      Serial.println("EV_RXCOMPLETE");
      printRSSIandSNR(); // Print RSSI and SNR
      break;
    case EV_LINK_DEAD:
      Serial.println("EV_LINK_DEAD");
      break;
    case EV_LINK_ALIVE:
      Serial.println("EV_LINK_ALIVE");
      break;
    default:
      Serial.println("Unknown event");
      break;
  }
}

// Function to print RSSI and SNR of the received signal
void printRSSIandSNR() {
  int rssi = LMIC.rssi;  // Get RSSI value
  int snr = LMIC.snr;    // Get SNR value
  Serial.print("RSSI: ");
  Serial.print(rssi);
  Serial.println(" dBm");
  Serial.print("SNR: ");
  Serial.print(snr);
  Serial.println(" dB");
}

void setup() {
  Serial.begin(9600);
  ss.begin(9600);
  while (!Serial) {};
  Serial.println("LoRa GPS Example ---- ");
  Serial.println("Connecting to TTN");

  os_init();
  LMIC_reset();

  #ifdef PROGMEM
    uint8_t appskey[sizeof(APPSKEY)];
    uint8_t nwkskey[sizeof(NWKSKEY)];
    memcpy_P(appskey, APPSKEY, sizeof(APPSKEY));
    memcpy_P(nwkskey, NWKSKEY, sizeof(NWKSKEY));
    LMIC_setSession (0x1, DEVADDR, nwkskey, appskey);
  #else
    LMIC_setSession (0x1, DEVADDR, NWKSKEY, APPSKEY);
  #endif

  LMIC_setLinkCheckMode(0);
  LMIC.dn2Dr = DR_SF9;
  LMIC_setDrTxpow(DR_SF7, 14);

  do_send(&sendjob);
}

void GPSRead() {
  unsigned long age;
  gps.f_get_position(&flat, &flon, &age);
  falt = gps.f_altitude(); 
  flat = flat == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flat;
  flon = flon == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flon;
  falt = falt == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : falt;
}

void GPSWrite() {
  datastring1 = dtostrf(flat, 0, 4, gps_lat);
  datastring2 = dtostrf(flon, 0, 4, gps_lon);
  strcat(gps_lat, ",");
  strcat(gps_lat, gps_lon);

  strcpy((char*)datasend, gps_lat);
  int32_t lat = flat * 10000;
  int32_t lon = flon * 10000;

  datasend[0] = lat;
  datasend[1] = lat >> 8;
  datasend[2] = lat >> 16;

  datasend[3] = lon;
  datasend[4] = lon >> 8;
  datasend[5] = lon >> 16;

  smartdelay(1000);
}

static void smartdelay(unsigned long ms) {
  unsigned long start = millis();
  do {
    while (ss.available()) {
      gps.encode(ss.read());
    }
  } while (millis() - start < ms);
}

void loop() {
  os_runloop_once();
}
