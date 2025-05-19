#include <Arduino.h>
#include <DHT.h> 

#define DHTPIN 21      
#define DHTTYPE DHT22   
#define BUTTON_P 22
#define BUTTON_K 23
#define LDR_PIN 34
#define RELAY_PIN 18   

DHT dht(DHTPIN, DHTTYPE);


void setup() {
  Serial.begin(115200);

  dht.begin();

  pinMode(BUTTON_P, INPUT_PULLUP);
  pinMode(BUTTON_K, INPUT_PULLUP);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
}


void loop() {
  delay(2000);

  float humidity = dht.readHumidity();

  float temperature = dht.readTemperature();

  int ldrValue = analogRead(LDR_PIN);

  float pH = (14 * (ldrValue - 32) / 4031);

  bool fosforoPresente = digitalRead(BUTTON_P) == LOW;
  bool potassioPresente = digitalRead(BUTTON_K) == LOW;

  Serial.println("===== LEITURA DE SENSORES =====");
  Serial.printf("Umidade: %.1f%%\n", humidity);
  Serial.printf("Temperatura: %.1f%%\n", temperature);
  Serial.printf("pH (simulado): %.2f\n", pH);
  Serial.printf("Fósforo presente: %s\n", fosforoPresente ? "SIM" : "NÃO");
  Serial.printf("Potássio presente: %s\n", potassioPresente ? "SIM" : "NÃO");

  if (
    humidity < 40.0 &&
    fosforoPresente &&
    potassioPresente &&
    (pH >= 6.0 && pH <= 7.5)
  ) {
    digitalWrite(RELAY_PIN, HIGH);
    Serial.println(">> Bomba LIGADA <<");
  } else {
    digitalWrite(RELAY_PIN, LOW);
    Serial.println(">> Bomba DESLIGADA <<");
  }

  Serial.println();
}