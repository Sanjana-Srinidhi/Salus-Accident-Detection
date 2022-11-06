#include <Wire.h>

int ADXL345 = 0x53;
int X_out, Y_out, Z_out;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  Wire.beginTransmission(ADXL345);
  Wire.write(0x2D); //talk to POWER_CTL Register - 0x2D
  
  Wire.write(8); // Bit D3 High for measuring enable (8dec -> 0000 1000 binary)
  Wire.endTransmission();
  delay(10);
}

void loop() {
  Wire.beginTransmission(ADXL345);
  Wire.write(0x32);
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL345, 6, true);

  X_out = ( Wire.read() | Wire.read() << 8);
  Y_out = ( Wire.read() | Wire.read() << 8);
  Z_out = ( Wire.read() | Wire.read() << 8);

  Serial.print(X_out);
  Serial.print(",");
  Serial.print(Y_out);
  Serial.print(",");
  Serial.println(Z_out);
  delay(500);
}
