// Building from the max31856_oneshot sketch
// A 6-shot thermocouple revolver
// The call to readThermocoupleTemperature() is blocking for O(100ms)

#include <Adafruit_MAX31856.h>

// Use software SPI: CS, DI, DO, CL
// Each maxthermo_<n> uses CS #<n>
// Shared rails:
// SDI 11
// SDO 12
// SCK 13

Adafruit_MAX31856 maxthermo_revolver[] ={
  Adafruit_MAX31856(0, 11, 12, 13),
  Adafruit_MAX31856(1, 11, 12, 13),
  Adafruit_MAX31856(2, 11, 12, 13),
  Adafruit_MAX31856(3, 11, 12, 13),
  Adafruit_MAX31856(4, 11, 12, 13),
  Adafruit_MAX31856(5, 11, 12, 13)
};
/*
Adafruit_MAX31856 maxthermo_0 = Adafruit_MAX31856(0, 11, 12, 13);
Adafruit_MAX31856 maxthermo_1 = Adafruit_MAX31856(1, 11, 12, 13);
Adafruit_MAX31856 maxthermo_2 = Adafruit_MAX31856(2, 11, 12, 13);
Adafruit_MAX31856 maxthermo_3 = Adafruit_MAX31856(3, 11, 12, 13);
Adafruit_MAX31856 maxthermo_4 = Adafruit_MAX31856(4, 11, 12, 13);
Adafruit_MAX31856 maxthermo_5 = Adafruit_MAX31856(5, 11, 12, 13);
*/
// if you want to use hardware SPI, just pass in the CS pin
//Adafruit_MAX31856 maxthermo = Adafruit_MAX31856(10);

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("MAX31856 thermocouple test");

  for(int n = 0; n <= 5; n++){
    maxthermo_revolver[n].setThermocoupleType(MAX31856_TCTYPE_N);

    Serial.print("Thermocouple #");
    Serial.print(n);
    Serial.print(", type: ");
    switch (maxthermo_revolver[n].getThermocoupleType() ) {
      case MAX31856_TCTYPE_B: Serial.println("B Type"); break;
      case MAX31856_TCTYPE_E: Serial.println("E Type"); break;
      case MAX31856_TCTYPE_J: Serial.println("J Type"); break;
      case MAX31856_TCTYPE_K: Serial.println("K Type"); break;
      case MAX31856_TCTYPE_N: Serial.println("N Type"); break;
      case MAX31856_TCTYPE_R: Serial.println("R Type"); break;
      case MAX31856_TCTYPE_S: Serial.println("S Type"); break;
      case MAX31856_TCTYPE_T: Serial.println("T Type"); break;
      case MAX31856_VMODE_G8: Serial.println("Voltage x8 Gain mode"); break;
      case MAX31856_VMODE_G32: Serial.println("Voltage x8 Gain mode"); break;
      default: Serial.println("Unknown"); break;
    }
  }

}

void loop() {
  for(int n = 0; n <= 5; n++){
    Serial.print("tc_id:");
    Serial.print(n);

    Serial.print(", Cold_Junction_Temp:");
    Serial.print(maxthermo_revolver[n].readCJTemperature());

    Serial.print(", Thermocouple_Temp:");
    Serial.println(maxthermo_revolver[n].readThermocoupleTemperature());

    // Check and print any faults
    uint8_t fault = maxthermo_revolver[n].readFault();
    if (fault) {
      if (fault & MAX31856_FAULT_CJRANGE) Serial.println("Cold Junction Range Fault");
      if (fault & MAX31856_FAULT_TCRANGE) Serial.println("Thermocouple Range Fault");
      if (fault & MAX31856_FAULT_CJHIGH)  Serial.println("Cold Junction High Fault");
      if (fault & MAX31856_FAULT_CJLOW)   Serial.println("Cold Junction Low Fault");
      if (fault & MAX31856_FAULT_TCHIGH)  Serial.println("Thermocouple High Fault");
      if (fault & MAX31856_FAULT_TCLOW)   Serial.println("Thermocouple Low Fault");
      if (fault & MAX31856_FAULT_OVUV)    Serial.println("Over/Under Voltage Fault");
      if (fault & MAX31856_FAULT_OPEN)    Serial.println("Thermocouple Open Fault");
    }
    delay(200);
  }
  delay(10000);
}
