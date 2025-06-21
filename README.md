# 🌱 Sistema de Irrigação Automatizado com ESP32 + IA

Este projeto simula e monitora um **sistema inteligente de irrigação** utilizando **ESP32**, sensores, componentes simulados no **Wokwi**, **interface web interativa** com **Streamlit**, e um **modelo de Machine Learning com Scikit-learn** para prever a necessidade de irrigação.

---

## 🧩 Componentes Físicos (Wokwi)

- 🧠 **ESP32 DevKit v4**
- 🌡️ **DHT22** – Temperatura e umidade do solo
- 🔆 **Sensor LDR** – Simula leitura analógica para pH
- 🔘 **2 Botões** – Indicam presença de Fósforo e Potássio
- 📟 **Display LCD 20x4 (I2C)** – Exibe métricas em tempo real
- 🔁 **Módulo Relé + LED** – Controlam bomba de irrigação
- 🕒 **RTC DS1307** – Fornece horário para decisões e logs

---

## 🧠 Lógica no ESP32 (C++)

O arquivo `code.INO` controla a lógica embarcada:
- Coleta sensores a cada 2s
- Calcula pH simulado
- Ativa bomba com base em:
  - Umidade < 40%
  - pH entre 6.0 e 7.5
  - Presença de nutrientes
- Mostra dados no **Serial Monitor** e **Display LCD I2C**
- Usa tipos otimizados (`float`, `int8_t`) para economia de memória
- Serial Plotter exibe a **umidade em tempo real**

---

## 💾 Gravação e Visualização de Dados

### 📁 Arquivo CSV (`data.csv`)
Simula os dados lidos pelo sistema, usado para visualização no dashboard e treinamento do modelo de IA.

### 📊 Dashboard Interativo (`dashboard.py`)
Utiliza **Streamlit** e **Plotly** para:
- Mostrar métricas médias (umidade, temperatura, pH, nutrientes)
- Gráficos interativos:
  - Correlação entre variáveis
  - Distribuição de pH e umidade
  - Dispersão multivariada
  - Série temporal simulada
- Tabela de dados brutos

> ⚠️ O caminho para o `data.csv` deve ser ajustado conforme seu ambiente local.

---

## 🧪 Geração e Coleta de Dados

### `data_generator.py`
Simula dados realistas com base na hora do dia e envia para a API Flask:
- Geração por lote (histórico)
- Inserção contínua (em tempo real)
- Menu interativo via terminal
- Simula logicamente quando a bomba deve ser ligada

---

## 🔗 API Flask para Integração com Banco Oracle

### `irrigation_api.py`
API RESTful com endpoints:
- `/health` – Verifica status
- `/dados` – Insere dado individual
- `/dados/batch` – Insere lote
- `/dados/consulta` – Consulta registros
- `/dados/estatisticas` – Estatísticas em tempo real

Conecta-se a um banco Oracle e gerencia automaticamente a tabela `irrigacao_dados`.

---

## 🤖 Machine Learning com Scikit-learn

### `ml_irrigation_system.py`
Módulo inteligente de decisão com:
- Treinamento de modelo `RandomForestClassifier`
- Previsão da necessidade de irrigação com base em:
  - Umidade, temperatura, pH, nutrientes
  - Hora do dia e dia da semana
- Otimização de horários para irrigação ao longo das 24h
- Salvamento e carregamento do modelo em `modelo_irrigacao.pkl`
- Análise de tendências nos últimos 7 dias

---

## 📊 Análise Avançada do Modelo

### `model_analyzer.py`
Permite inspeção completa do modelo salvo:
- Tipo, profundidade e acurácia
- Importância das features com interpretação
- Simulação de predições e sensibilidade
- Geração de relatório técnico de análise

---

## 📐 Diagrama do Circuito (Wokwi)

### `diagram.json`
Arquivo Wokwi que define o circuito completo, incluindo:
- Conexões entre ESP32, sensores, relé, RTC e LCD I2C
- Alimentação e uso de barramentos
- Pinos SDA/SCL compartilhados entre RTC e LCD

---

## 📎 Arquivos do Projeto

| Arquivo                  | Descrição |
|--------------------------|-----------|
| `code.INO`               | Código C++ para o ESP32 com lógica de irrigação e LCD |
| `data.csv`               | Simulação de dados para visualização e treino |
| `dashboard.py`           | Painel interativo com métricas e gráficos |
| `data_generator.py`      | Geração de dados realistas e envio para a API |
| `irrigation_api.py`      | API RESTful com integração Oracle |
| `ml_irrigation_system.py`| Treinamento e predição de irrigação com ML |
| `model_analyzer.py`      | Ferramentas de análise e interpretação do modelo |
| `modelo_irrigacao.pkl`   | Modelo de ML salvo com `joblib` |
| `diagram.json`           | Circuito virtual completo no Wokwi |
| `README.md`              | Documentação completa do projeto |
