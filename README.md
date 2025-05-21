# 🌱 Sistema de Irrigação Automatizado com ESP32

Este projeto simula um sistema de irrigação automatizado utilizando o microcontrolador **ESP32**, sensores ambientais e lógica de controle. O circuito foi montado no simulador **Wokwi**, e o código foi escrito em **C++** utilizando a plataforma **PlatformIO**.

## 📦 Componentes Utilizados

- 🧠 **ESP32 DevKit v4**
- 🌡️ **Sensor DHT22** (temperatura e umidade)
- 🌞 **Sensor LDR** (simula leitura para cálculo de pH)
- 🔘 **2 botões** (simulam presença de nutrientes: Fósforo e Potássio)
- 🔌 **Módulo Relé** (simula acionamento da bomba de irrigação)
- 💡 **LED branco** (representa a bomba ligada)
- 💾 **Módulo MicroSD** (simula gravação de dados em CSV)
- 🔧 **Protoboard e fios de conexão**

## 🔌 Descrição do Circuito

- **DHT22** conectado ao pino **21** (dados de temperatura e umidade)
- **BUTTON_P (Fósforo)** no pino **22**
- **BUTTON_K (Potássio)** no pino **17**
- **LDR** (simula pH) conectado ao pino **34**
- **Relé** no pino **4**
- **LED branco** ligado à saída do relé
- **Módulo MicroSD** com as conexões SPI:
  - CS: pino **5**
  - DI: pino **23**
  - DO: pino **19**
  - SCK: pino **18**
  - GND e VCC ligados à alimentação da protoboard

## 🧠 Lógica de Controle

O sistema coleta leituras a cada **2 segundos** e toma decisões com base nas seguintes condições:

1. **Umidade** < **40%**
2. **Fósforo presente** (botão pressionado = LOW)
3. **Potássio presente** (botão pressionado = LOW)
4. **pH** entre **6.0 e 7.5** (calculado via leitura analógica do LDR)

### 💡 Acionamento da bomba:

Se todas as condições forem satisfeitas, a **bomba é acionada** (LED acende). Caso contrário, ela permanece desligada.

## 💾 Gravação de Dados

O sistema está programado para **gravar os dados em um arquivo CSV no cartão SD** com as leituras dos sensores e o estado da bomba.

> ⚠️ **Observação importante:**  
> Como o projeto é executado em um **ambiente virtual (Wokwi)**, a gravação real em cartão SD **não é suportada**.  
> Para simular o funcionamento completo, foi criado manualmente um arquivo `data.csv` de exemplo. Esse arquivo é utilizado no **dashboard em Python (Streamlit)** para visualizar os dados simulados.

## 📊 Dashboard Python (Streamlit)

Um painel interativo foi criado com **Python + Streamlit** para analisar os dados do sistema. Ele exibe:

- Temperatura, Umidade, pH
- Presença de Fósforo e Potássio
- Estado da bomba
- Gráficos de correlação, dispersão e séries temporais

> O dashboard carrega o `data.csv` e **não depende da execução direta do ESP32**.

## 💬 Exemplo de Saída Serial

```
===== LEITURA DE SENSORES =====
Umidade: 37.2%
Temperatura: 25.1%
pH (simulado): 6.80
Fósforo presente: SIM
Potássio presente: SIM
>> Bomba LIGADA <<
```