#include <Arduino.h>
#include <DHT.h>
#include <SPI.h>
#include <Wire.h>
#include <RTClib.h>
#include <LiquidCrystal_I2C.h>

// Botões de fósforo e potássio
#define PIN_BUTTON_P 34
#define PIN_BUTTON_K 35

// Sensor simulado de pH
#define PIN_LDR 32

// Sensor de umidade
#define PIN_DHT 33
#define DHT_TYPE DHT22
DHT dht(PIN_DHT, DHT_TYPE);

// Definindo pino do relé
#define PIN_RELAY 15

// Definindo Real Time Clock
RTC_DS1307 rtc;
const int sqwPin = 27;
const int I2C_SDA_PIN = 21;
const int I2C_SCL_PIN = 22;
char diasDaSemana[7][12] = {"Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"};

// Definindo o display LCD
const int LCD_I2C_ADDRESS = 0X27;
const int LCD_COLUMNS = 20;
const int LCD_ROWS = 4;
LiquidCrystal_I2C lcd(LCD_I2C_ADDRESS, LCD_COLUMNS, LCD_ROWS);

String bomba;





void setup(){
    Serial.begin(115200);

    dht.begin();    // inicializa o sensor DHT

    pinMode(PIN_BUTTON_P, INPUT_PULLUP);
    pinMode(PIN_BUTTON_K, INPUT_PULLUP);

    pinMode(PIN_RELAY, OUTPUT);
    digitalWrite(PIN_RELAY, LOW);

    Wire.begin(21,22);   // inicializa a comunicação I2C no ESP32
    lcd.init();     // inicializa o display
    lcd.backlight();
    lcd.clear();
    
    if (!rtc.begin()) {
        Serial.println("Modulo RTC DS1307 nao encontrado!");
        Serial.println("Verifique as conexoes do RTC (SDA no GPIO 21, SCL no GPIO 22).");
        lcd.setCursor(0,0); lcd.print("RTC ERROR!"); // Exibe erro no LCD
        lcd.setCursor(0,1); lcd.print("Check Wiring/Power");
        while (true); // Trava o programa se o RTC não for encontrado
    }
    if (rtc.now().year() < 2000) {
        Serial.println("Hora do RTC parece ser muito antiga, ajustando para a hora de compilacao...");
        lcd.setCursor(0,2); lcd.print("RTC Time Invalid!");
        lcd.setCursor(0,3); lcd.print("Adjusting Time...");
        delay(2000);
        rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    }


}

void loop(){

    byte error, address;
    int nDevices = 0;

    Serial.println("Scanning...");

    for (address = 1; address < 127; address++) {
        Wire.beginTransmission(address);
        error = Wire.endTransmission();

        if (error == 0) {
        Serial.print("I2C device found at address 0x");
        if (address < 16) Serial.print("0");
        Serial.print(address, HEX);
        Serial.println("  !");
        nDevices++;
        } else if (error == 4) {
        Serial.print("Unknown error at address 0x");
        if (address < 16) Serial.print("0");
        Serial.println(address, HEX);
        }
    }
    if (nDevices == 0) {
        Serial.println("No I2C devices found\n");
    } else {
        Serial.println("done\n");
    }


    delay(3000);

    DateTime now = rtc.now();

    float UMIDADE = dht.readHumidity();
    float TEMPERATURA = dht.readTemperature();

    int LDR_VALUE = analogRead(PIN_LDR);
    float PH = (14 * (LDR_VALUE - 32) / 4031); // converte a leitura do LDR para uma escala entre 0 e 7

    bool PRESENCA_FOSFORO = digitalRead(PIN_BUTTON_P) == LOW;
    bool PRESENCA_POTASSIO = digitalRead(PIN_BUTTON_K) == LOW;

    if(
        UMIDADE < 40.0 &&
        PRESENCA_FOSFORO &&
        PRESENCA_POTASSIO &&
        (PH >= 6.0 && PH <= 7.5)
    ){
        digitalWrite(PIN_RELAY, HIGH);
        bomba = "LIGADA";
    } else{
        digitalWrite(PIN_RELAY, LOW);
        bomba = "DESLIGADA";
    }



    //////////////////// IMPRIMINDO DADOS NO DISPLAY LCD ////////////////////

    //Data, Hora, Umidade do solo, Temperatura
    lcd.clear();

    lcd.setCursor(0,0);
    lcd.print("Data: ");
    lcd.print(now.day(), DEC);
    lcd.print('/');
    lcd.print(now.month(), DEC);
    lcd.print('/');
    lcd.print(now.year(), DEC);

    lcd.setCursor(0,1);
    lcd.print(diasDaSemana[now.dayOfTheWeek()]);
    lcd.print(" ");
        // Garante dois dígitos para hora, minuto, segundo
    if (now.hour() < 10) lcd.print('0');
    lcd.print(now.hour(), DEC);
    lcd.print(':');
    if (now.minute() < 10) lcd.print('0');
    lcd.print(now.minute(), DEC);
    lcd.print(':');
    if (now.second() < 10) lcd.print('0');
    lcd.print(now.second(), DEC);

    lcd.setCursor(0,2);
    lcd.printf("%-5s %.1f%%", "Umidade:", UMIDADE);

    lcd.setCursor(0,3);
    lcd.printf("%-5s  %.1fC", "Temperatura:", TEMPERATURA);

    // pH, presença de fósforo, presença de potássio
    delay(2000);
    lcd.clear();

    lcd.setCursor(0,0);
    lcd.printf("%-5s  %.1f", "pH: ", PH);

    lcd.setCursor(0,1);
    if(PRESENCA_FOSFORO){
        lcd.printf("Fosforo presente");
    } else{
        lcd.printf("Fosforo ausente");
    }
    lcd.setCursor(0,2);
        if(PRESENCA_POTASSIO){
        lcd.printf("Potassio presente");
    } else{
        lcd.printf("Potassio ausente");
    }
    

    // Status da bomba
    delay(2000);
    lcd.clear();

    lcd.setCursor(0,0);
    lcd.print("====================");
    lcd.setCursor(0,1);
    lcd.print("STATUS DA BOMBA:");
    lcd.setCursor(0,2);
    lcd.print(bomba);
    lcd.setCursor(0,3);
    lcd.print("====================");

}