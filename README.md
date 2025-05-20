
# 🌱 Sistema de Irrigação Automatizado com ESP32

Este projeto simula um sistema de irrigação automatizado utilizando o microcontrolador **ESP32**, sensores ambientais e lógica de controle. O circuito foi montado no simulador **Wokwi**, e o código foi escrito em **C++** utilizando a plataforma **PlatformIO**.

## 📦 Componentes Utilizados

- 🧠 **ESP32 DevKit v4**
- 🌡️ **Sensor DHT22** (temperatura e umidade)
- 🌞 **Sensor LDR** (simula leitura para cálculo de pH)
- 🔘 **2 botões** (simulam presença de nutrientes: Fósforo e Potássio)
- 🔌 **Módulo Relé** (simula acionamento da bomba de irrigação)
- 💡 **LED branco** (simula o funcionamento da bomba)
- 🔧 **Protoboard e fios de conexão**

## 🔌 Descrição do Circuito

- **DHT22** está conectado ao pino **21** do ESP32.
- **Botões**:
  - **BUTTON_P (Fósforo)** → pino **22**
  - **BUTTON_K (Potássio)** → pino **23**
- **LDR** (sensor analógico) → pino **34**
- **Relé** → pino **18**
- **LED branco** está ligado na saída do relé (representa a bomba ligada).

A alimentação dos sensores é feita pela linha de 5V da protoboard. Os botões estão ligados com pull-up interno ativado.

## 🧠 Lógica de Controle

O sistema lê os dados dos sensores a cada **2 segundos** e toma decisões com base nos seguintes critérios:

1. **Umidade do solo** (via DHT22) < **40%**
2. **Fósforo presente** (botão pressionado = nível lógico LOW)
3. **Potássio presente** (botão pressionado = nível lógico LOW)
4. **pH adequado** entre **6.0 e 7.5**  
   _(pH simulado com LDR, convertendo valor analógico)_

### 💡 Acionamento da bomba (relé):

Se **TODAS** as condições forem satisfeitas, o sistema **liga a bomba de irrigação** (acende o LED via relé). Caso contrário, a bomba permanece desligada.

### 💬 Exemplo de Saída Serial:

```
===== LEITURA DE SENSORES =====
Umidade: 37.2%
Temperatura: 25.1%
pH (simulado): 6.80
Fósforo presente: SIM
Potássio presente: SIM
>> Bomba LIGADA <<
```
