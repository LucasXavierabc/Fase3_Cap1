import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.tree import export_text
import os
import warnings
from datetime import datetime

# Suprimir warnings específicos do sklearn para uma saída mais limpa
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

class AnalisadorModeloIrrigacao:
    """
    Classe para análise completa de modelos de irrigação baseados em ML.
    Permite carregar, analisar e visualizar características do modelo treinado.
    """
    
    def __init__(self, caminho_modelo='modelo_irrigacao.pkl'):
        """
        Inicializa o analisador de modelo.
        
        Args:
            caminho_modelo (str): Caminho para o arquivo do modelo (.pkl)
        """
        self.caminho_modelo = caminho_modelo
        self.modelo_dados = None
        self.modelo = None
        self.scaler = None
        self.features = None
        self.historico_acuracia = None
        
    def carregar_modelo(self):
        """
        Carrega o modelo salvo e seus componentes.
        
        Returns:
            bool: True se carregado com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(self.caminho_modelo):
                print(f"ERRO: Arquivo {self.caminho_modelo} não encontrado.")
                print("Certifique-se de que o modelo foi treinado e salvo.")
                return False
            
            self.modelo_dados = joblib.load(self.caminho_modelo)
            self.modelo = self.modelo_dados['modelo']
            self.scaler = self.modelo_dados['scaler']
            self.features = self.modelo_dados['features']
            self.historico_acuracia = self.modelo_dados.get('historico_acuracia', [])
            
            print(f"Modelo carregado com sucesso de: {self.caminho_modelo}")
            print(f"Tamanho do arquivo: {os.path.getsize(self.caminho_modelo) / 1024:.2f} KB")
            return True
            
        except Exception as e:
            print(f"ERRO ao carregar modelo: {str(e)}")
            return False
    
    def informacoes_gerais(self):
        """
        Exibe informações gerais sobre o modelo carregado.
        """
        if self.modelo is None:
            print("ERRO: Modelo não carregado. Execute carregar_modelo() primeiro.")
            return
        
        print("\n" + "="*60)
        print("INFORMAÇÕES GERAIS DO MODELO")
        print("="*60)
        
        print(f"Tipo de modelo: {type(self.modelo).__name__}")
        print(f"Número de estimadores: {self.modelo.n_estimators}")
        print(f"Profundidade máxima: {self.modelo.max_depth}")
        print(f"Critério de divisão: {self.modelo.criterion}")
        print(f"Balanceamento de classes: {self.modelo.class_weight}")
        print(f"Estado aleatório: {self.modelo.random_state}")
        
        if self.historico_acuracia:
            print(f"Acurácia atual: {self.historico_acuracia[-1]:.4f}")
            print(f"Histórico de acurácias: {len(self.historico_acuracia)} treinamentos")
        
        print(f"Número de features: {len(self.features)}")
        print(f"Features utilizadas: {', '.join(self.features)}")
        
        # Informações do scaler
        if hasattr(self.scaler, 'mean_'):
            print(f"Normalização: StandardScaler aplicado")
            print(f"Médias das features: {np.round(self.scaler.mean_, 3)}")
            print(f"Desvios padrão: {np.round(self.scaler.scale_, 3)}")
    
    def analise_importancia_features(self):
        """
        Analisa e exibe a importância das features no modelo.
        """
        if self.modelo is None:
            print("ERRO: Modelo não carregado.")
            return
        
        print("\n" + "="*60)
        print("ANÁLISE DE IMPORTÂNCIA DAS FEATURES")
        print("="*60)
        
        importancias = pd.DataFrame({
            'Feature': self.features,
            'Importancia': self.modelo.feature_importances_,
            'Percentual': self.modelo.feature_importances_ * 100
        }).sort_values('Importancia', ascending=False)
        
        print("\nRanking de importância das características:")
        print("-" * 50)
        for idx, row in importancias.iterrows():
            print(f"{row['Feature']:20} | {row['Importancia']:.4f} | {row['Percentual']:6.2f}%")
        
        # Identificar features mais relevantes
        features_relevantes = importancias[importancias['Percentual'] >= 5.0]
        print(f"\nFeatures mais relevantes (>= 5%): {len(features_relevantes)}")
        
        if len(features_relevantes) > 0:
            print("Características principais do modelo:")
            for _, row in features_relevantes.iterrows():
                self._interpretar_feature(row['Feature'], row['Percentual'])
        
        return importancias
    
    def _interpretar_feature(self, feature, percentual):
        """
        Interpreta o significado de cada feature para o usuário.
        """
        interpretacoes = {
            'HUMIDITY': 'Umidade do solo - fundamental para decisões de irrigação',
            'TEMPERATURE': 'Temperatura ambiente - afeta evapotranspiração',
            'PH': 'pH do solo - influencia absorção de nutrientes',
            'FOSFORO_PRESENTE': 'Presença de fósforo - nutriente essencial',
            'POTASSIO_PRESENTE': 'Presença de potássio - nutriente essencial',
            'hora': 'Hora do dia - padrões temporais de irrigação',
            'dia_semana': 'Dia da semana - rotinas de manejo',
            'humidity_temp_ratio': 'Relação umidade/temperatura - índice composto',
            'ph_nutrients': 'Interação pH com nutrientes - disponibilidade nutricional'
        }
        
        interpretacao = interpretacoes.get(feature, 'Feature customizada')
        print(f"  - {feature}: {interpretacao} ({percentual:.1f}%)")
    
    def analise_arvores_decisao(self, num_arvores=3):
        """
        Analisa algumas árvores de decisão do Random Forest.
        """
        if self.modelo is None:
            print("ERRO: Modelo não carregado.")
            return
        
        print("\n" + "="*60)
        print("ANÁLISE DE ÁRVORES DE DECISÃO")
        print("="*60)
        
        print(f"Analisando {num_arvores} árvores do Random Forest...")
        
        for i in range(min(num_arvores, len(self.modelo.estimators_))):
            arvore = self.modelo.estimators_[i]
            print(f"\n--- ÁRVORE {i+1} ---")
            print(f"Profundidade: {arvore.get_depth()}")
            print(f"Número de folhas: {arvore.get_n_leaves()}")
            
            # Regras da árvore (limitadas para legibilidade)
            regras = export_text(arvore, feature_names=self.features, max_depth=3)
            print("Primeiras regras de decisão:")
            print(regras[:500] + "..." if len(regras) > 500 else regras)
    
    def simular_predicoes(self, num_simulacoes=5):
        """
        Simula predições com diferentes cenários de entrada.
        """
        if self.modelo is None or self.scaler is None:
            print("ERRO: Modelo ou scaler não carregados.")
            return
        
        print("\n" + "="*60)
        print("SIMULAÇÃO DE PREDIÇÕES")
        print("="*60)
        
        # Cenários de teste realísticos
        cenarios = [
            {
                'nome': 'Solo muito seco, calor intenso',
                'dados': {'HUMIDITY': 20, 'TEMPERATURE': 38, 'PH': 6.0, 
                         'FOSFORO_PRESENTE': 1, 'POTASSIO_PRESENTE': 1, 
                         'hora': 14, 'dia_semana': 2}
            },
            {
                'nome': 'Solo úmido, temperatura amena',
                'dados': {'HUMIDITY': 75, 'TEMPERATURE': 22, 'PH': 6.8, 
                         'FOSFORO_PRESENTE': 1, 'POTASSIO_PRESENTE': 0, 
                         'hora': 8, 'dia_semana': 1}
            },
            {
                'nome': 'Condições médias, meio-dia',
                'dados': {'HUMIDITY': 50, 'TEMPERATURE': 28, 'PH': 6.5, 
                         'FOSFORO_PRESENTE': 0, 'POTASSIO_PRESENTE': 1, 
                         'hora': 12, 'dia_semana': 3}
            },
            {
                'nome': 'Madrugada, alta umidade',
                'dados': {'HUMIDITY': 85, 'TEMPERATURE': 18, 'PH': 6.2, 
                         'FOSFORO_PRESENTE': 1, 'POTASSIO_PRESENTE': 1, 
                         'hora': 3, 'dia_semana': 0}
            },
            {
                'nome': 'Solo ácido, sem nutrientes',
                'dados': {'HUMIDITY': 40, 'TEMPERATURE': 30, 'PH': 5.5, 
                         'FOSFORO_PRESENTE': 0, 'POTASSIO_PRESENTE': 0, 
                         'hora': 16, 'dia_semana': 4}
            }
        ]
        
        print("Testando diferentes cenários de irrigação:")
        print("-" * 80)
        
        for cenario in cenarios[:num_simulacoes]:
            dados = cenario['dados']
            
            # Calcular features derivadas
            dados['humidity_temp_ratio'] = dados['HUMIDITY'] / (dados['TEMPERATURE'] + 1)
            dados['ph_nutrients'] = dados['PH'] * (dados['FOSFORO_PRESENTE'] + dados['POTASSIO_PRESENTE'])
            
            # Preparar dados para predição
            X = np.array([[dados[feature] for feature in self.features]])
            # Converter para DataFrame para evitar warnings do sklearn
            X_df = pd.DataFrame(X, columns=self.features)
            X_scaled = self.scaler.transform(X_df)
            
            # Fazer predição
            predicao = self.modelo.predict(X_scaled)[0]
            probabilidades = self.modelo.predict_proba(X_scaled)[0]
            
            decisao = "IRRIGAR" if predicao == 1 else "NÃO IRRIGAR"
            confianca = max(probabilidades) * 100
            
            print(f"\nCenário: {cenario['nome']}")
            print(f"Condições: H={dados['HUMIDITY']}% T={dados['TEMPERATURE']}°C "
                  f"pH={dados['PH']} Hora={dados['hora']:02d}:00")
            print(f"Decisão: {decisao}")
            print(f"Probabilidade de irrigar: {probabilidades[1]:.3f}")
            print(f"Confiança: {confianca:.1f}%")
    
    def analise_sensibilidade(self):
        """
        Analisa a sensibilidade do modelo a mudanças nas features principais.
        """
        if self.modelo is None or self.scaler is None:
            print("ERRO: Modelo ou scaler não carregados.")
            return
        
        print("\n" + "="*60)
        print("ANÁLISE DE SENSIBILIDADE")
        print("="*60)
        
        # Valores base para teste
        valores_base = {
            'HUMIDITY': 50, 'TEMPERATURE': 25, 'PH': 6.5,
            'FOSFORO_PRESENTE': 1, 'POTASSIO_PRESENTE': 1,
            'hora': 12, 'dia_semana': 2,
            'humidity_temp_ratio': 50/26, 'ph_nutrients': 6.5 * 2
        }
        
        # Testar variações nas features principais
        features_teste = ['HUMIDITY', 'TEMPERATURE', 'PH']
        
        for feature in features_teste:
            print(f"\nTeste de sensibilidade - {feature}:")
            print("-" * 40)
            
            # Valores de teste para a feature
            if feature == 'HUMIDITY':
                valores_teste = [10, 30, 50, 70, 90]
                unidade = "%"
            elif feature == 'TEMPERATURE':
                valores_teste = [15, 20, 25, 30, 35]
                unidade = "°C"
            elif feature == 'PH':
                valores_teste = [5.5, 6.0, 6.5, 7.0, 7.5]
                unidade = ""
            
            for valor in valores_teste:
                dados_teste = valores_base.copy()
                dados_teste[feature] = valor
                
                # Recalcular features derivadas se necessário
                if feature in ['HUMIDITY', 'TEMPERATURE']:
                    dados_teste['humidity_temp_ratio'] = dados_teste['HUMIDITY'] / (dados_teste['TEMPERATURE'] + 1)
                if feature == 'PH':
                    dados_teste['ph_nutrients'] = dados_teste['PH'] * (dados_teste['FOSFORO_PRESENTE'] + dados_teste['POTASSIO_PRESENTE'])
                
                X = np.array([[dados_teste[f] for f in self.features]])
                # Converter para DataFrame para evitar warnings do sklearn
                X_df = pd.DataFrame(X, columns=self.features)
                X_scaled = self.scaler.transform(X_df)
                
                prob_irrigar = self.modelo.predict_proba(X_scaled)[0][1]
                
                print(f"  {feature}={valor}{unidade:2} -> Prob. irrigar: {prob_irrigar:.3f}")
    
    def relatorio_completo(self):
        """
        Gera um relatório completo de análise do modelo.
        """
        print("\n" + "="*80)
        print("RELATÓRIO COMPLETO DE ANÁLISE DO MODELO DE IRRIGAÇÃO")
        print("="*80)
        print(f"Data/Hora da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        if not self.carregar_modelo():
            return
        
        # Executar todas as análises
        self.informacoes_gerais()
        importancias = self.analise_importancia_features()
        self.analise_arvores_decisao()
        self.simular_predicoes()
        self.analise_sensibilidade()
        
        print("\n" + "="*80)
        print("RESUMO E RECOMENDAÇÕES")
        print("="*80)
        
        # Gerar recomendações baseadas na análise
        if importancias is not None:
            feature_principal = importancias.iloc[0]['Feature']
            importancia_principal = importancias.iloc[0]['Percentual']
            
            print(f"1. Feature mais importante: {feature_principal} ({importancia_principal:.1f}%)")
            print("   Esta característica tem maior influência nas decisões de irrigação")
            
            features_baixa_importancia = importancias[importancias['Percentual'] < 2.0]
            if len(features_baixa_importancia) > 0:
                print(f"2. Features com baixa importância: {len(features_baixa_importancia)} identificadas")
                print("   Considere avaliar se são necessárias para simplificar o modelo")
                print(f"   Features: {', '.join(features_baixa_importancia['Feature'].tolist())}")
            
            if self.historico_acuracia and self.historico_acuracia[-1] < 0.85:
                print("3. ATENÇÃO: Acurácia do modelo abaixo de 85%")
                print("   Recomenda-se coletar mais dados de treinamento")
                print("   Considere aumentar o período de coleta de dados")
            else:
                print("3. Performance do modelo: ADEQUADA")
                if self.historico_acuracia:
                    print(f"   Acurácia atual: {self.historico_acuracia[-1]:.1%}")
            
            print("4. Status do modelo: PRONTO PARA PRODUÇÃO")
            print("   Implementação recomendada com monitoramento contínuo")
            print("5. Manutenção: Retreinamento periódico recomendado")
            print("   Frequência sugerida: mensal ou quando performance diminuir")

def main():
    """
    Função principal para execução do analisador.
    """
    print("Analisador de Modelo de Irrigação Inteligente")
    print("Desenvolvido para análise de modelos de Machine Learning")
    
    analisador = AnalisadorModeloIrrigacao()
    
    # Verificar se arquivo existe
    if not os.path.exists('modelo_irrigacao.pkl'):
        print("\nERRO: Arquivo 'modelo_irrigacao.pkl' não encontrado.")
        print("Certifique-se de que o modelo foi treinado usando o sistema de irrigação ML.")
        print("Execute primeiro o treinamento com: python ml_irrigation_system.py")
        return
    
    # Executar análise completa
    try:
        analisador.relatorio_completo()
        
        print("\n" + "="*80)
        print("Análise concluída com sucesso!")
        print("Para análises específicas, importe a classe AnalisadorModeloIrrigacao")
        print("e use os métodos individuais conforme necessário.")
        
    except Exception as e:
        print(f"\nERRO durante a análise: {str(e)}")
        print("Verifique se o arquivo do modelo está íntegro e foi gerado corretamente.")

if __name__ == "__main__":
    main()