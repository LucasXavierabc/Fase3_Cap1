# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# FarmTech Solutions: Sistema Inteligente de Irrigação

## Nome do grupo

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do integrante 1</a>
- <a href="https://www.linkedin.com/in/william--xavier/">William Xavier</a>
- <a href="https://www.linkedin.com/in/lucas-xavier-a05199284/">Lucas Xavier</a>
- <a> Jeniane Joice Malosti de Oliveira</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/lucas-gomes-moreira-15a8452a/">Lucas Gomes Moreira</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi</a>


## 📜 Descrição

Nesta Fase 4 do projeto FarmTech Solutions, o objetivo principal é elevar a inteligência e a interatividade do sistema de irrigação automatizado, construído sobre a base da Fase 3. Incorporamos avançadas funcionalidades de Machine Learning e uma interface de usuário dinâmica para otimizar a gestão hídrica em ambientes agrícolas.

O sistema agora utiliza a biblioteca **Scikit-learn** para desenvolver um modelo preditivo capaz de analisar dados históricos de umidade, temperatura e nutrientes do solo, prevendo a necessidade de irrigação em horários específicos. Essa inteligência artificial permite uma tomada de decisão mais eficiente e proativa, minimizando o desperdício de água e maximizando a saúde das culturas.

Para aprimorar a visualização e o controle, foi implementado um dashboard interativo utilizando **Streamlit**. Esta interface permite aos usuários monitorar em tempo real as métricas coletadas pelos sensores, visualizar os insights gerados pelo modelo de Machine Learning e acompanhar o status da irrigação de forma intuitiva.

No hardware, o **ESP32** foi otimizado para maior eficiência de memória e agora integra um **display LCD** via barramento I2C, exibindo as principais métricas diretamente no dispositivo. Além disso, o monitoramento em tempo real de variáveis críticas é facilitado pelo uso do **Serial Plotter**, fornecendo uma análise visual contínua do comportamento do sistema.

Este projeto representa um avanço significativo na automação agrícola, combinando hardware robusto, software inteligente e uma interface amigável para uma gestão de irrigação mais sustentável e eficaz.

## 📁 Estrutura de pastas

A estrutura de pastas do projeto é organizada para facilitar o desenvolvimento, a manutenção e a compreensão dos diferentes componentes do sistema:

```
.
├── .github/                     # Configurações do GitHub (workflows, templates)
├── assets/                      # Imagens e outros recursos visuais do README e projeto
├── config/                      # Arquivos de configuração gerais (ex: credenciais de BD)
├── document/                    # Documentação do projeto (relatórios, especificações)
│   └── other/                   # Documentos complementares
├── scripts/                     # Scripts auxiliares (deploy, migrações de BD)
├── src/                         # Código fonte principal do projeto
│   ├── backend/                 # Código da API Flask para comunicação com o banco de dados
│   │   └── api.py               # Servidor Flask com endpoints para dados de irrigação
│   ├── data_generation/         # Scripts para geração de dados fictícios
│   │   └── data_generator.py    # Gerador de dados realísticos para a API
│   ├── esp32/                   # Código C/C++ para o ESP32 (firmware)
│   │   └── main.ino             # Código principal do ESP32 (com LCD e Serial Plotter)
│   ├── ml_model/                # Código para treinamento e uso do modelo de Machine Learning
│   │   ├── ml_irrigation_system.py # Sistema de ML para predição de irrigação
│   │   └── model_analyzer.py    # Ferramenta para análise e relatório do modelo de ML
│   │   └── modelo_irrigacao.pkl # Modelo de ML treinado (gerado após o treinamento)
│   └── frontend/                # Código da interface de usuário (Streamlit)
│       └── app.py               # Aplicação Streamlit para dashboard interativo
├── README.md                    # Este arquivo
└── .gitignore                   # Arquivo para ignorar arquivos e pastas no Git
```

## 🔧 Como executar o código

Para configurar e executar o projeto FarmTech Solutions, siga os passos abaixo. Certifique-se de ter os pré-requisitos instalados em seu ambiente.

### Pré-requisitos

*   **Python 3.8+**: Para os scripts de backend, ML e Streamlit.
*   **pip**: Gerenciador de pacotes Python.
*   **Oracle Database**: Um servidor Oracle acessível para o banco de dados.
*   **Oracle Instant Client**: Necessário para a conexão Python com o Oracle.
*   **Arduino IDE** ou **VS Code com PlatformIO**: Para compilar e carregar o código no ESP32 (ou simular no Wokwi).
*   **Wokwi**: Para simulação do ESP32 e visualização do LCD/Serial Plotter.

### Configuração do Ambiente

1.  **Clonar o Repositório:**
    ```bash
    git clone https://github.com/LucasXavierabc/Fase3_Cap1/tree/fase4
    cd Fase4_Cap1
    ```

2.  **Configurar o Ambiente Python:**
    Crie um ambiente virtual e instale as dependências:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    pip install -r requirements.txt # Crie este arquivo com as dependências
    ```
    **Conteúdo para `requirements.txt`:**
    ```
    Flask
    oracledb
    pandas
    scikit-learn
    requests
    joblib
    matplotlib
    seaborn
    streamlit
    ```

3.  **Configurar o Banco de Dados Oracle:**
    *   Certifique-se de que seu banco de dados Oracle esteja acessível.
    *   No arquivo `src/backend/api.py`, atualize as configurações de conexão `ORACLE_CONFIG` com seu `dsn`, `user` e `password`.
    *   A tabela `irrigacao_dados` será criada automaticamente na primeira execução da API se não existir.

### Execução dos Componentes

Siga a ordem recomendada para garantir o funcionamento correto do sistema.

1.  **Iniciar a API (Backend):**
    Abra um terminal e execute:
    ```bash
    python src/backend/api.py
    ```
    A API estará disponível em `http://localhost:5000`.

2.  **Gerar Dados (Opcional, para popular o BD):**
    Abra outro terminal e execute o gerador de dados. Você pode escolher entre inserção em lote ou contínua através do menu interativo.
    ```bash
    python src/data_generation/data_generator.py
    ```
    Para um teste rápido com 50 registros iniciais e 10 em tempo real:
    ```bash
    python src/data_generation/data_generator.py rapido
    ```

3.  **Treinar e Analisar o Modelo de Machine Learning:**
    Após ter dados no banco (gerados ou reais), treine o modelo.
    ```bash
    python src/ml_model/ml_irrigation_system.py
    ```
    Para uma análise mais detalhada do modelo treinado:
    ```bash
    python src/ml_model/model_analyzer.py
    ```
    O modelo treinado será salvo como `src/ml_model/modelo_irrigacao.pkl`.

4.  **Executar o Dashboard Streamlit (Frontend):**
    Abra um novo terminal e inicie a aplicação Streamlit:
    ```bash
    streamlit run src/frontend/app.py
    ```
    O dashboard será aberto em seu navegador padrão.

5.  **Compilar e Simular o Código ESP32 (Wokwi):**
    *   Abra o projeto ESP32 (`src/esp32/main.ino`) no Wokwi.
    *   Configure o display LCD (barramento I2C, pinos SDA e SCL) conforme o circuito.
    *   Inicie a simulação. O display LCD mostrará as métricas, e você poderá monitorar variáveis no Serial Plotter.

### Integração do Serial Plotter

Para demonstrar o uso do Serial Plotter, inclua capturas de tela do Wokwi aqui, mostrando o gráfico de uma ou mais variáveis (ex: umidade) em tempo real. Explique o que cada gráfico representa e como ele ajuda na análise do comportamento do sistema.

**Exemplo de Print do Serial Plotter:**
![Exemplo Serial Plotter](assets/serial_plotter_example.png)
*Descrição: Este gráfico do Serial Plotter exibe a variação da umidade do solo ao longo do tempo. Observa-se que a umidade diminui gradualmente e sobe abruptamente quando a bomba de irrigação é ativada, demonstrando a resposta do sistema à necessidade hídrica.*

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>


