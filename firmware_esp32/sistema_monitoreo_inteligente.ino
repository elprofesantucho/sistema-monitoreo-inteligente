// ==============================================
// SISTEMA DE MONITOREO INTELIGENTE - EEST N14
// Control automático de riego y ventilación
// ==============================================

#include <TFT_eSPI.h>
#include <SPI.h>
#include <DHT.h>

// Configuración
#define DHT_TYPE DHT22
#define DHT_PIN 16
#define SOIL_SENSOR_1 34
#define SOIL_SENSOR_2 35
#define SOIL_SENSOR_3 32
#define SOIL_SENSOR_4 33
#define MOTOR_A_IN1 12
#define MOTOR_A_IN2 13
#define MOTOR_A_ENA 14
#define MOTOR_B_IN1 25
#define MOTOR_B_IN2 26
#define MOTOR_B_ENB 27

const int UMBRAL_HUMEDAD_SUELO = 1500;
const int UMBRAL_TEMPERATURA_ALTA = 30;

TFT_eSPI tft = TFT_eSPI();
DHT dht(DHT_PIN, DHT_TYPE);

float temperatura = 0;
float humedadAire = 0;
int suelo1 = 0, suelo2 = 0, suelo3 = 0, suelo4 = 0;

void setup() {
  Serial.begin(115200);
  tft.init();
  tft.setRotation(1);
  dht.begin();
  
  pinMode(SOIL_SENSOR_1, INPUT);
  pinMode(SOIL_SENSOR_2, INPUT);
  pinMode(SOIL_SENSOR_3, INPUT);
  pinMode(SOIL_SENSOR_4, INPUT);
  pinMode(MOTOR_A_IN1, OUTPUT);
  pinMode(MOTOR_A_IN2, OUTPUT);
  pinMode(MOTOR_A_ENA, OUTPUT);
  pinMode(MOTOR_B_IN1, OUTPUT);
  pinMode(MOTOR_B_IN2, OUTPUT);
  pinMode(MOTOR_B_ENB, OUTPUT);
  
  apagarMotores();
  pantallaBienvenida();
  delay(2000);
}

void loop() {
  leerSensores();
  pantallaPrincipal();
  delay(4000);
  pantallaBienvenida();
  delay(4000);
  controlAutomatico();
  imprimirSerial();
  delay(2000);
}

void leerSensores() {
  temperatura = dht.readTemperature();
  humedadAire = dht.readHumidity();
  suelo1 = analogRead(SOIL_SENSOR_1);
  suelo2 = analogRead(SOIL_SENSOR_2);
  suelo3 = analogRead(SOIL_SENSOR_3);
  suelo4 = analogRead(SOIL_SENSOR_4);
  
  if (isnan(temperatura) || isnan(humedadAire)) {
    Serial.println("Error DHT22!");
    temperatura = 0;
    humedadAire = 0;
  }
}

void pantallaBienvenida() {
  tft.fillScreen(TFT_BLACK);
  tft.setTextFont(4);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  int x_center = tft.width() / 2;
  tft.setCursor(x_center - 70, 30);
  tft.print("Sistema de");
  tft.setCursor(x_center - 100, 60);
  tft.print("Monitoreo");
  tft.setCursor(x_center - 70, 90);
  tft.print("Inteligente");
  tft.setTextFont(2);
  tft.setCursor(10, 130);
  tft.print("DHT22 + 4 Sensores Suelo");
  tft.setCursor(10, 150);
  tft.print("Control Puente H Doble");
  tft.setCursor(10, 170);
  tft.print("EEST N14");
}

void pantallaPrincipal() {
  tft.fillScreen(TFT_BLACK);
  tft.setTextFont(4);
  tft.setTextColor(TFT_CYAN, TFT_BLACK);
  tft.setCursor(10, 10);
  tft.print("Monitoreo Activo");
  tft.setTextFont(2);
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.setCursor(10, 40);
  tft.printf("Temp: %.1fC  Hum Aire: %.1f%%", temperatura, humedadAire);
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  tft.setCursor(10, 60);
  tft.printf("Suelo 1: %d", suelo1);
  tft.setCursor(120, 60);
  tft.printf("Suelo 2: %d", suelo2);
  tft.setCursor(10, 80);
  tft.printf("Suelo 3: %d", suelo3);
  tft.setCursor(120, 80);
  tft.printf("Suelo 4: %d", suelo4);
  tft.setTextColor(TFT_ORANGE, TFT_BLACK);
  tft.setCursor(10, 110);
  tft.printf("Motor A: %s", obtenerEstadoMotorA().c_str());
  tft.setCursor(10, 130);
  tft.printf("Motor B: %s", obtenerEstadoMotorB().c_str());
}

void controlAutomatico() {
  if (suelo1 > UMBRAL_HUMEDAD_SUELO || suelo2 > UMBRAL_HUMEDAD_SUELO) {
    activarMotorA();
  } else {
    desactivarMotorA();
  }
  if (suelo3 > UMBRAL_HUMEDAD_SUELO || suelo4 > UMBRAL_HUMEDAD_SUELO) {
    activarMotorB();
  } else {
    desactivarMotorB();
  }
  if (temperatura > UMBRAL_TEMPERATURA_ALTA) {
    activarVentilacion();
  }
}

void apagarMotores() {
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, LOW);
  analogWrite(MOTOR_A_ENA, 0);
  digitalWrite(MOTOR_B_IN1, LOW);
  digitalWrite(MOTOR_B_IN2, LOW);
  analogWrite(MOTOR_B_ENB, 0);
}

void activarMotorA() {
  digitalWrite(MOTOR_A_IN1, HIGH);
  digitalWrite(MOTOR_A_IN2, LOW);
  analogWrite(MOTOR_A_ENA, 200);
}

void desactivarMotorA() {
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, LOW);
  analogWrite(MOTOR_A_ENA, 0);
}

void activarMotorB() {
  digitalWrite(MOTOR_B_IN1, HIGH);
  digitalWrite(MOTOR_B_IN2, LOW);
  analogWrite(MOTOR_B_ENB, 200);
}

void desactivarMotorB() {
  digitalWrite(MOTOR_B_IN1, LOW);
  digitalWrite(MOTOR_B_IN2, LOW);
  analogWrite(MOTOR_B_ENB, 0);
}

void activarVentilacion() {
  digitalWrite(MOTOR_B_IN1, HIGH);
  digitalWrite(MOTOR_B_IN2, LOW);
  analogWrite(MOTOR_B_ENB, 150);
}

String obtenerEstadoMotorA() {
  return digitalRead(MOTOR_A_IN1) ? "ACTIVO" : "APAGADO";
}

String obtenerEstadoMotorB() {
  return digitalRead(MOTOR_B_IN1) ? "ACTIVO" : "APAGADO";
}

void imprimirSerial() {
  Serial.println("=== DATOS SENSORES ===");
  Serial.print("Temperatura: "); Serial.println(temperatura);
  Serial.print("Humedad: "); Serial.println(humedadAire);
  Serial.print("Suelo 1: "); Serial.println(suelo1);
  Serial.print("Suelo 2: "); Serial.println(suelo2);
  Serial.print("Suelo 3: "); Serial.println(suelo3);
  Serial.print("Suelo 4: "); Serial.println(suelo4);
  Serial.print("Motor A: "); Serial.println(obtenerEstadoMotorA());
  Serial.print("Motor B: "); Serial.println(obtenerEstadoMotorB());
  Serial.println("====================");
}
