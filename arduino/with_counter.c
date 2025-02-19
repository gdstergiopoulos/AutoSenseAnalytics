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
uint8_t send_counter = 0;

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
  This is the default Semtech key, which is used by the prototype TTN
  network initially.
*/

/*ac9860d5b896430f7a07be769b2a40e5*/
static const PROGMEM u1_t NWKSKEY[16] = { 0xac, 0x98, 0x60, 0xd5, 0xb8, 0x96, 0x43, 0x0f, 0x7a, 0x07, 0xbe, 0x76, 0x9b, 0x2a, 0x40, 0xe5 };

/*
  LoRaWAN AppSKey, application session key
  This is the default Semtech key, which is used by the prototype TTN
  network initially.
*/
/*c11733c52d513c3540ded2f05f49c6e6*/
static const u1_t PROGMEM APPSKEY[16] = { 0xc1, 0x17, 0x33, 0xc5, 0x2d, 0x51, 0x3c, 0x35, 0x40, 0xde, 0xd2, 0xf0, 0x5f, 0x49, 0xc6, 0xe6 };

/*
  LoRaWAN end-device address (DevAddr)
  See http://thethingsnetwork.org/wiki/AddressSpace
*/
static const u4_t DEVADDR = 0x260111D1;

/*
  These callbacks are only used in over-the-air activation, so they are
  left empty here (we cannot leave them out completely unless
  DISABLE_JOIN is set in config.h, otherwise the linker will complain).
*/
void os_getArtEui (u1_t* buf) { }
void os_getDevEui (u1_t* buf) { }
void os_getDevKey (u1_t* buf) { }

static osjob_t initjob, sendjob, blinkjob;

/*
  Schedule TX every this many seconds (might become longer due to duty
  cycle limitations).
*/
const unsigned TX_INTERVAL = 0.1;

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
    
    Serial.print("Counter value: ");
    Serial.println(send_counter);

    // Prepare upstream data transmission at the next possible time.
    LMIC_setTxData2(1, datasend, sizeof(datasend) - 1, 0);
    // LMIC_setTxData2(1, mydata, sizeof(mydata) - 1, 0);
    Serial.println("Packet queued");
    Serial.print("LMIC.freq:");
    Serial.println(LMIC.freq);
    Serial.println("");
    Serial.println("");
    Serial.println("Receive data:");

    send_counter = (send_counter + 1) % 256;
  } 
  // Next TX is scheduled after TX_COMPLETE event.
}

void onEvent (ev_t ev) {
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
      }
      // Schedule next transmission
      os_setTimedCallback(&sendjob, os_getTime() + sec2osticks(TX_INTERVAL), do_send);
      break;
    case EV_LOST_TSYNC:
      Serial.println("EV_LOST_TSYNC");
      break;
    case EV_RESET:
      Serial.println("EV_RESET");
      break;
    case EV_RXCOMPLETE:
      // Data received in ping slot
      Serial.println("EV_RXCOMPLETE");
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

void setup() {
  // Initialize digital pin as an output
  Serial.begin(9600);
  ss.begin(9600);
  while (!Serial) {};
  Serial.println("LoRa GPS Example---- ");
  Serial.println("Connect to TTN");
  #ifdef VCC_ENABLE
    // For Pinoccio Scout boards
    pinMode(VCC_ENABLE, OUTPUT);
    digitalWrite(VCC_ENABLE, HIGH);
    delay(1000);
  #endif

  // LMIC init
  os_init();
  // Reset the MAC state. Session and pending data transfers will be discarded.
  LMIC_reset();
  /*
    LMIC_setClockError(MAX_CLOCK_ERROR * 1/100);
    Set static session parameters. Instead of dynamically establishing a session
    by joining the network, precomputed session parameters are be provided.
  */
  #ifdef PROGMEM
    /*
      On AVR, these values are stored in flash and only copied to RAM
      once. Copy them to a temporary buffer here, LMIC_setSession will
      copy them into a buffer of its own again.
    */
    uint8_t appskey[sizeof(APPSKEY)];
    uint8_t nwkskey[sizeof(NWKSKEY)];
    memcpy_P(appskey, APPSKEY, sizeof(APPSKEY));
    memcpy_P(nwkskey, NWKSKEY, sizeof(NWKSKEY));
    LMIC_setSession (0x1, DEVADDR, nwkskey, appskey);
  #else
    // If not running an AVR with PROGMEM, just use the arrays directly 
    LMIC_setSession (0x1, DEVADDR, NWKSKEY, APPSKEY);
  #endif

  // Disable link check validation
  LMIC_setLinkCheckMode(0);

  // TTN uses SF9 for its RX2 window
  LMIC.dn2Dr = DR_SF9;

  // Set data rate and transmit power (note: txpow seems to be ignored by the library)
  LMIC_setDrTxpow(DR_SF7, 14);

  // Start job
  do_send(&sendjob);
}

void GPSRead() {
  unsigned long age;
  gps.f_get_position(&flat, &flon, &age);
  falt = gps.f_altitude(); // Get altitude
  //Serial.println(falt);
  //Serial.println(flon);
  flat == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flat, 6;
  flon == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flon, 6; // Save six decimal places
  falt == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : falt, 2; // Save two decimal places
}

void GPSWrite() {
  // Convert GPS data to format
  datastring1 += dtostrf(flat, 0, 4, gps_lat);
  datastring2 += dtostrf(flon, 0, 4, gps_lon);
  // datastring3 += dtostrf(falt, 0, 2, gps_alt);
  Serial.print("Latitude: ");
  Serial.println(flat, 6); // Print latitude with 6 decimal places
  Serial.print("Longitude: ");
  Serial.println(flon, 6); // Print longitude with 6 decimal places


  if (flat != 1000.000000) {
    strcat(gps_lat, ",");
    strcat(gps_lat, gps_lon);
    // strcat(gps_lat, ",");
    // strcat(gps_lat, gps_alt);
    int i = 0;
    for (i = 0; i < 2; i++) {
      // datasend.toFloat();
      atof(gps_lat);
      // Serial.println((char*)datasend);
      Serial.println("Testing converted data:");
      Serial.println(gps_lat);
      // atof(gps_alt);
      // Serial.print(gps_alt);
    }

    strcpy((char*)datasend, gps_lat); // The format of datasend is latitude, longtitude, altitude
    Serial.print("###########    ");
    Serial.print("NO.");
    Serial.print(count);
    Serial.println("    ###########");
    Serial.println("The latitude and longtitude are:");
    Serial.print("[");
    Serial.print((char*)datasend);
    Serial.print("]");
    Serial.println("");
    /*
      for (int k = 0; k < 20; k++) {
        Serial.print("[");
        Serial.print(datasend[k], HEX);
        Serial.print("]");
      }
      Serial.println("");
      Serial.println("");
    */
    count++;
  }

  int32_t lat = flat * 10000;
  int32_t lon = flon * 10000;

  datasend[0] = lat;
  datasend[1] = lat >> 8;
  datasend[2] = lat >> 16;

  datasend[3] = lon;
  datasend[4] = lon >> 8;
  datasend[5] = lon >> 16;
  datasend[6]=send_counter; 
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