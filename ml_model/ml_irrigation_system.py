import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import requests
import joblib
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SistemaIrrigacaoML:
    def __init__(self, api_url='http://localhost:5000'):
        self.api_url = api_url
        self.modelo = None
        self.scaler = None
        self.historico_acuracia = []
        
    def obter_dados_api(self, limite=5000):
        # Obtém dados da API p treinamento
        try:
            response = requests.get(f'{self.api_url}/dados/consulta', 
                                  params={'limite': limite})
            
            if response.status_code == 200:
                dados = response.json()['dados']
                if dados:
                    df = pd.DataFrame(dados)
                    # Converte status da bomba para binARIO 
                    df['bomba_ligada'] = (df['BOMBA_STATUS'] == 'LIGADA').astype(int)
                    return df
                else:
                    print("Nenhum dado retornado da API")
                    return None
            else:
                print(f"Erro ao obter dados: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Erro na conexão com API: {e}")
            return None
    
    def preparar_dados(self, df):
        # Prepara os dados para treinamento do modelo
        features = ['HUMIDITY', 'TEMPERATURE', 'PH', 'FOSFORO_PRESENTE', 'POTASSIO_PRESENTE']
        
        # Cria features adicionais baseadas no tempo
        if 'DATA_COLETA' in df.columns:
            df['DATA_COLETA'] = pd.to_datetime(df['DATA_COLETA'])
            df['hora'] = df['DATA_COLETA'].dt.hour
            df['dia_semana'] = df['DATA_COLETA'].dt.dayofweek
            features.extend(['hora', 'dia_semana'])
        
        # Features de interação
        df['humidity_temp_ratio'] = df['HUMIDITY'] / (df['TEMPERATURE'] + 1)
        df['ph_nutrients'] = df['PH'] * (df['FOSFORO_PRESENTE'] + df['POTASSIO_PRESENTE'])
        features.extend(['humidity_temp_ratio', 'ph_nutrients'])
        
        X = df[features].fillna(0)
        y = df['bomba_ligada']
        
        return X, y, features
    
    def treinar_modelo(self):
        # TREina o ML
        print("Obtendo dados da API...")
        df = self.obter_dados_api()
        
        if df is None or len(df) < 50:
            print("Dados insuficientes para treinamento (mínimo 50 registros)")
            return False
        
        print(f"Preparando {len(df)} registros para treinamento...")
        X, y, self.features = self.preparar_dados(df)
        distribuicao = y.value_counts()
        print(f"Distribuição das classes: {distribuicao.to_dict()}")
        if len(distribuicao) < 2:
            print("Precisa de exemplos de bomba ligada E desligada para treinamento")
            return False
        
        # Divisão treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normalização
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Treinamento do modelo
        print("Treinando modelo Random Forest...")
        self.modelo = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.modelo.fit(X_train_scaled, y_train)
        
        # Avaliação
        y_pred = self.modelo.predict(X_test_scaled)
        acuracia = accuracy_score(y_test, y_pred)
        self.historico_acuracia.append(acuracia)
        
        print(f"Acurácia do modelo: {acuracia:.3f}")
        print("\nRelatório de classificação:")
        print(classification_report(y_test, y_pred))
        
        # Importância das features
        importancias = pd.DataFrame({
            'feature': self.features,
            'importancia': self.modelo.feature_importances_
        }).sort_values('importancia', ascending=False)
        
        print("\nImportância das features:")
        print(importancias.head(8))
        
        # Salva o modelo
        self.salvar_modelo()
        
        return True
    
    def prever_irrigacao(self, humidity, temperature, ph, fosforo, potassio, hora_atual=None):
        """Faz predição de necessidade de irrigação"""
        if self.modelo is None:
            if not self.carregar_modelo():
                return None, "Modelo não treinado"
        
        # Prepara dados de entrada
        if hora_atual is None:
            hora_atual = datetime.now().hour
        
        dados = {
            'HUMIDITY': humidity,
            'TEMPERATURE': temperature,
            'PH': ph,
            'FOSFORO_PRESENTE': fosforo,
            'POTASSIO_PRESENTE': potassio,
            'hora': hora_atual,
            'dia_semana': datetime.now().weekday(),
            'humidity_temp_ratio': humidity / (temperature + 1),
            'ph_nutrients': ph * (fosforo + potassio)
        }
        
        # Converte para array
        X = np.array([list(dados.values())])
        X_scaled = self.scaler.transform(X)
        
        # Predição
        predicao = self.modelo.predict(X_scaled)[0]
        probabilidade = self.modelo.predict_proba(X_scaled)[0]
        
        resultado = {
            'deve_irrigar': bool(predicao),
            'probabilidade_irrigar': float(probabilidade[1]),
            'confianca': max(probabilidade),
            'dados_entrada': dados
        }
        
        return resultado, None
    
    def otimizar_horarios_irrigacao(self, previsoes_24h=None):
        # Otimiza horários de irrigação com base em previsões horárias
        if previsoes_24h is None:
            # Gera previsões típicas para cada hora do dia
            previsoes_24h = []
            for hora in range(24):
                if 6 <= hora <= 10:  # Manhã
                    humidity, temp, ph = 70, 22, 6.5
                elif 11 <= hora <= 16:  # Tarde
                    humidity, temp, ph = 45, 32, 6.8
                elif 17 <= hora <= 21:  # Noite
                    humidity, temp, ph = 60, 25, 6.6
                else:  # Madrugada
                    humidity, temp, ph = 80, 18, 6.4
                previsoes_24h.append((humidity, temp, ph))
        
        horarios_otimos = []
        
        for i, previsao in enumerate(previsoes_24h):
            hora = i
            humidity, temperature, ph = previsao
            
            resultado, erro = self.prever_irrigacao(
                humidity, temperature, ph, 1, 1, hora
            )
            
            if resultado:
                horarios_otimos.append({
                    'hora': hora,
                    'deve_irrigar': resultado['deve_irrigar'],
                    'probabilidade': resultado['probabilidade_irrigar'],
                    'confianca': resultado['confianca'],
                    'condicoes': f"H:{humidity}% T:{temperature}°C pH:{ph}"
                })
        
        # Ordena por probabilidade de irrigação
        horarios_otimos.sort(key=lambda x: x['probabilidade'], reverse=True)
        
        return horarios_otimos
    
    def analisar_tendencias(self, dias=7):
        # Análise de tendências dos dados históricos
        data_inicio = (datetime.now() - timedelta(days=dias)).isoformat()
        
        try:
            response = requests.get(f'{self.api_url}/dados/consulta', 
                                  params={'data_inicio': data_inicio, 'limite': 1000})
            
            if response.status_code == 200:
                dados = response.json()['dados']
                if dados:
                    df = pd.DataFrame(dados)
                    df['DATA_COLETA'] = pd.to_datetime(df['DATA_COLETA'])
                    
                    # Análises
                    tendencias = {
                        'media_humidity': df['HUMIDITY'].mean(),
                        'media_temperature': df['TEMPERATURE'].mean(),
                        'media_ph': df['PH'].mean(),
                        'irrigacoes_periodo': (df['BOMBA_STATUS'] == 'LIGADA').sum(),
                        'horario_mais_irrigado': df[df['BOMBA_STATUS'] == 'LIGADA']['DATA_COLETA'].dt.hour.mode().iloc[0] if any(df['BOMBA_STATUS'] == 'LIGADA') else None
                    }
                    
                    return tendencias
            
        except Exception as e:
            print(f"Erro ao analisar tendências: {e}")
        
        return None
    
    def salvar_modelo(self):
        # Salva o modelo treinado em um arquivo
        try:
            joblib.dump({
                'modelo': self.modelo,
                'scaler': self.scaler,
                'features': self.features,
                'historico_acuracia': self.historico_acuracia
            }, 'modelo_irrigacao.pkl')
            print("Modelo salvo com sucesso")
        except Exception as e:
            print(f"Erro ao salvar modelo: {e}")
    
    def carregar_modelo(self):
        # Carrega o modelo treinado de um arquivo
        try:
            dados = joblib.load('modelo_irrigacao.pkl')
            self.modelo = dados['modelo']
            self.scaler = dados['scaler']
            self.features = dados['features']
            self.historico_acuracia = dados.get('historico_acuracia', [])
            print("Modelo carregado com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            return False

def exemplo_uso():
    sistema = SistemaIrrigacaoML()
    
    # Treina o modelo
    print("=== TREINAMENTO DO MODELO ===")
    if sistema.treinar_modelo():
        print("\n=== FAZENDO PREDIÇÕES ===")
        
        # Exemplo de predição
        resultado, erro = sistema.prever_irrigacao(
            humidity=45.5,
            temperature=25.3,
            ph=6.8,
            fosforo=1,
            potassio=0
        )
        
        if resultado:
            print(f"Deve irrigar: {resultado['deve_irrigar']}")
            print(f"Probabilidade: {resultado['probabilidade_irrigar']:.3f}")
            print(f"Confiança: {resultado['confianca']:.3f}")
        
        print("\n=== ANÁLISE DE TENDÊNCIAS ===")
        tendencias = sistema.analisar_tendencias()
        if tendencias:
            print(f"Humidade média: {tendencias['media_humidity']:.2f}%")
            print(f"Temperatura média: {tendencias['media_temperature']:.2f}°C")
            print(f"pH médio: {tendencias['media_ph']:.2f}")
            print(f"Irrigações no período: {tendencias['irrigacoes_periodo']}")
        
        print("\n=== HORÁRIOS OTIMIZADOS ===")
        # Otimização de horários com condições realísticas
        horarios = sistema.otimizar_horarios_irrigacao()
        
        if horarios:
            print("Melhores horários para irrigação (top 5):")
            for i, horario in enumerate(horarios[:5]):
                status = "IRRIGAR" if horario['deve_irrigar'] else "OK"
                print(f"- {horario['hora']:02d}:00 - {status} - "
                      f"Prob: {horario['probabilidade']:.3f} - "
                      f"Conf: {horario['confianca']:.3f} - "
                      f"{horario['condicoes']}")
        else:
            print("Nenhum horário de irrigação identificado")

def teste_completo():
    """Teste mais detalhado do sistema"""
    sistema = SistemaIrrigacaoML()
    
    print("=== TESTE COMPLETO DO SISTEMA ML ===")
    
    # Verifica se modelo existe
    if sistema.carregar_modelo():
        print("Modelo existente carregado")
    else:
        print("Treinando novo modelo...")
        if not sistema.treinar_modelo():
            print("Falha no treinamento")
            return
    
    print("\n=== PREDIÇÕES DE TESTE ===")
    
    # Testa diferentes cenários
    cenarios = [
        {"nome": "Solo seco + calor", "humidity": 30, "temperature": 35, "ph": 6.5, "fosforo": 1, "potassio": 1},
        {"nome": "Solo úmido + frio", "humidity": 80, "temperature": 15, "ph": 6.8, "fosforo": 1, "potassio": 1},
        {"nome": "Condições médias", "humidity": 55, "temperature": 25, "ph": 6.7, "fosforo": 0, "potassio": 1},
        {"nome": "Muito seco", "humidity": 20, "temperature": 40, "ph": 6.0, "fosforo": 0, "potassio": 0}
    ]
    
    for cenario in cenarios:
        resultado, _ = sistema.prever_irrigacao(
            cenario['humidity'], cenario['temperature'], cenario['ph'],
            cenario['fosforo'], cenario['potassio']
        )
        
        if resultado:
            irrigar = "SIM" if resultado['deve_irrigar'] else "NÃO"
            print(f"{cenario['nome']:20} - Irrigar: {irrigar} - "
                  f"Prob: {resultado['probabilidade_irrigar']:.3f}")
    
    print("\n=== ANÁLISE DETALHADA DE HORÁRIOS ===")
    horarios = sistema.otimizar_horarios_irrigacao()
    
    print("Análise completa das 24 horas:")
    for horario in horarios:
        status = "🔴" if horario['deve_irrigar'] else "🟢"
        print(f"{horario['hora']:02d}:00 {status} - "
              f"Prob: {horario['probabilidade']:.3f} - "
              f"{horario['condicoes']}")
    
    print(f"\nResumo: {sum(1 for h in horarios if h['deve_irrigar'])} horários requerem irrigação")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'completo':
        teste_completo()
    else:
        exemplo_uso()