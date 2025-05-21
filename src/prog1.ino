#include <Arduino.h>
#include <DHT.h> 
#include <SPI.h>
#include <SD.h>

#define DHTPIN 21      
#define DHTTYPE DHT22   
#define BUTTON_P 22
#define BUTTON_K 17
#define LDR_PIN 34
#define RELAY_PIN 4

#define SD_CS    5  // Pino Chip Select
#define SD_SCK   18 // Pino Clock
#define SD_MOSI  23 // Pino MOSI
#define SD_MISO  19 // Pino MISO

DHT dht(DHTPIN, DHTTYPE);


void setup() {
  Serial.begin(115200);

  dht.begin();

  pinMode(BUTTON_P, INPUT_PULLUP);
  pinMode(BUTTON_K, INPUT_PULLUP);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);



  Serial.println("Inicializando o cartão microSD...");
  if (!SD.begin(SD_CS)) {
    Serial.println("Erro ao inicializar o microSD!");
    while (1);
  }
  Serial.println("Cartão microSD inicializado com sucesso!");

  File dataFile = SD.open("/data.csv", FILE_WRITE);
  if (dataFile) {
    // Escrever o cabeçalho no arquivo
    dataFile.println("Humidity,Temperature,pH,FosforoPresente,PotassioPresente");
    dataFile.close();
    Serial.println("Arquivo criado com cabeçalho.");
  } else {
    Serial.println("Erro ao criar o arquivo.");
  }
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



  File dataFile = SD.open("/data.csv", FILE_WRITE);
  if (dataFile) {
    // Escrever os dados no arquivo
    dataFile.print(humidity);
    dataFile.print(",");
    dataFile.print(temperature);
    dataFile.print(",");
    dataFile.print(pH);
    dataFile.print(",");
    dataFile.print(fosforoPresente);
    dataFile.print(",");
    dataFile.println(potassioPresente);
    dataFile.close();
    Serial.println("Dados registrados no arquivo.");
  } else {
    Serial.println("Erro ao abrir o arquivo.");
  }
}