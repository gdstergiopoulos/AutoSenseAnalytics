#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <SoftwareSerial.h>
#include <TinyGPS.h>

TinyGPS gps;
SoftwareSerial ss(3, 4); // Arduino RX (D3) <-> GPS_TX, Arduino TX (D4) <-> GPS_RX

static void smartdelay(unsigned long ms);
uint8_t datasend[20]; // Payload array to store GPS data and RSSI

// LoRaWAN session keys and device address
static const PROGMEM u1_t NWKSKEY[16] = { 0xac, 0x98, 0x60, 0xd5, 0xb8, 0x96, 0x43, 0x0f, 0x7a, 0x07, 0xbe, 0x76, 0x9b, 0x2a, 0x40, 0xe5 };
static const PROGMEM u1_t APPSKEY[16] = { 0xc1, 0x17, 0x33, 0xc5, 0x2d, 0x51, 0x3c, 0x35, 0x40, 0xde, 0xd2, 0xf0, 0x5f, 0x49, 0xc6, 0xe6 };
static const u4_t DEVADDR = 0x260111D1;

void os_getArtEui (u1_t* buf) { }
void os_getDevEui (u1_t* buf) { }
void os_getDevKey (u1_t* buf) { }

static osjob_t sendjob;

// Schedule TX every this many seconds
const unsigned TX_INTERVAL = 10;

// Pin mapping
const lmic_pinmap lmic_pins = {
  .nss = 10,
  .rxtx = LMIC_UNUSED_PIN,
  .rst = 9,
  .dio = {2, 6, 7}
};

float flat, flon, falt; // GPS coordinates and altitude
int rssi_value = -255;  // RSSI default value

void do_send(osjob_t* j) {
  if (LMIC.opmode & OP_TXRXPEND) {
    Serial.println("OP_TXRXPEND, not sending");
  } else {
    // Read GPS data
    GPSRead();

    // Prepare payload
    int32_t lat = flat * 10000; // Convert latitude to int (preserve precision)
    int32_t lon = flon * 10000; // Convert longitude to int (preserve precision)

    datasend[0] = lat;
    datasend[1] = lat >> 8;
    datasend[2] = lat >> 16;

    datasend[3] = lon;
    datasend[4] = lon >> 8;
    datasend[5] = lon >> 16;

    // Add RSSI value to payload
    datasend[6] = rssi_value; // RSSI is added to the payload

    // Send payload
    LMIC_setTxData2(1, datasend, 7, 0); // Transmit only 7 bytes
    Serial.println("Packet queued");
  }
}

void onEvent(ev_t ev) {
  Serial.print(os_getTime());
  Serial.print(": ");
  Serial.println(ev);

  switch (ev) {
    case EV_TXCOMPLETE:
      Serial.println("EV_TXCOMPLETE (includes waiting for RX windows)");
      if (LMIC.dataLen > 0) {
        // Data received in RX window
        Serial.println("Data Received!");
        Serial.print("RSSI of Received Signal: ");
        rssi_value = LMIC.rssi; // Update the RSSI value
        Serial.print(rssi_value);
        Serial.println(" dBm");
      }
      os_setTimedCallback(&sendjob, os_getTime() + sec2osticks(TX_INTERVAL), do_send);
      break;

    case EV_JOINING:
      Serial.println("EV_JOINING");
      break;

    case EV_JOINED:
      Serial.println("EV_JOINED");
      break;

    case EV_RXCOMPLETE:
      Serial.println("EV_RXCOMPLETE");
      Serial.print("RSSI of Received Signal: ");
      rssi_value = LMIC.rssi; // Update the RSSI value
      Serial.print(rssi_value);
      Serial.println(" dBm");
      break;

    default:
      Serial.println("Unknown event");
      break;
  }
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
