import requests
import random
import time
import json
from datetime import datetime, timedelta
import threading
import numpy as np

class GeradorDadosIrrigacao:
    def __init__(self, api_url='http://localhost:5000'):
        self.api_url = api_url
        self.rodando = False
        self.contador_registros = 0
        
    def gerar_dados_realisticos(self):
        # gerar dados de irrigação realista p treinamento de ML
        hora_atual = datetime.now().hour
        
        # Padrões baseados na hora do dia
        if 6 <= hora_atual <= 10:  # Manhã
            base_humidity = random.uniform(60, 85)
            base_temp = random.uniform(18, 25)
            chance_irrigacao = 0.7
        elif 11 <= hora_atual <= 16:  # Tarde
            base_humidity = random.uniform(35, 65)
            base_temp = random.uniform(25, 35)
            chance_irrigacao = 0.8
        elif 17 <= hora_atual <= 21:  # Noite
            base_humidity = random.uniform(50, 75)
            base_temp = random.uniform(20, 28)
            chance_irrigacao = 0.6
        else:  # Madrugada
            base_humidity = random.uniform(70, 90)
            base_temp = random.uniform(15, 22)
            chance_irrigacao = 0.3
        
        # Adiciona variação natural
        humidity = max(10, min(100, base_humidity + random.uniform(-15, 15)))
        temperature = max(5, min(45, base_temp + random.uniform(-5, 5)))
        
        # pH varia entre 5.5 e 8.0
        ph = round(random.uniform(5.5, 8.0), 2)
        
        # Nutrientes aleatórios
        fosforo = random.choice([0, 1])
        potassio = random.choice([0, 1])
        
        # Lógica de irrigação baseada em condições
        deve_irrigar = False
        
        # Condições para irrigação
        if humidity < 40:  # Humidade muito baixa
            deve_irrigar = True
        elif humidity < 55 and temperature > 30:  # Calor e humidade baixa
            deve_irrigar = True
        elif (fosforo == 0 or potassio == 0) and humidity < 60:  # Falta nutrientes
            deve_irrigar = True
        elif random.random() < (chance_irrigacao * 0.3):  # Chance aleatória
            deve_irrigar = True
        
        # Pequena chance de não irrigar mesmo em condições ideais
        if random.random() < 0.1:
            deve_irrigar = False
        
        bomba_status = "LIGADA" if deve_irrigar else "DESLIGADA"
        
        return {
            'humidity': round(humidity, 2),
            'temperature': round(temperature, 2),
            'ph': ph,
            'fosforo_presente': fosforo,
            'potassio_presente': potassio,
            'bomba_status': bomba_status
        }
    
    def inserir_dados_batch_inicial(self, quantidade=200):
        # Insere um lote inicial de dados fictícios
        print(f"Gerando {quantidade} registros históricos...")
        
        dados_batch = []
        for i in range(quantidade):
            # Simula dados de diferentes dias/horários
            dados = self.gerar_dados_realisticos()
            dados_batch.append(dados)
            
            if len(dados_batch) >= 50:  # Insere em lotes de 50
                self.enviar_batch(dados_batch)
                dados_batch = []
                print(f"Inseridos {i+1}/{quantidade} registros...")
        
        # Insere registros restantes
        if dados_batch:
            self.enviar_batch(dados_batch)
        
        print(f"✓ {quantidade} registros históricos inseridos!")
    
    def enviar_batch(self, dados):
        # Envia um lote de dados para a API
        try:
            response = requests.post(
                f'{self.api_url}/dados/batch',
                json=dados,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                resultado = response.json()
                self.contador_registros += resultado.get('sucessos', 0)
                return True
            else:
                print(f"Erro no batch: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Erro ao enviar batch: {e}")
            return False
    
    def inserir_dados_continuos(self, intervalo=30):
        # Insere dados continuamente em intervalos definidos
        print(f"Iniciando inserção contínua (intervalo: {intervalo}s)")
        self.rodando = True
        
        while self.rodando:
            try:
                dados = self.gerar_dados_realisticos()
                
                response = requests.post(
                    f'{self.api_url}/dados',
                    json=dados,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 201:
                    self.contador_registros += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Registro #{self.contador_registros} - "
                          f"H:{dados['humidity']:.1f}% T:{dados['temperature']:.1f}°C "
                          f"pH:{dados['ph']} Bomba:{dados['bomba_status']}")
                else:
                    print(f"Erro: {response.status_code}")
                
                time.sleep(intervalo)
                
            except KeyboardInterrupt:
                print("\nParando inserção contínua...")
                break
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(5)
        
        self.rodando = False
    
    def parar_insercao(self):
        self.rodando = False
    
    def verificar_api(self):
        # Verifica se a API está rodando
        try:
            response = requests.get(f'{self.api_url}/health')
            if response.status_code == 200:
                return True
        except:
            pass
        return False

def menu_interativo():
    # Menu o gerador
    gerador = GeradorDadosIrrigacao()
    
    if not gerador.verificar_api():
        print("API não está rodando em http://localhost:5000")
        return
    
    print("API conectada com sucesso!")
    print("=== GERADOR DE DADOS FICTÍCIOS ===")
    
    while True:
        print("\nOpções:")
        print("1. Inserir lote inicial (200 registros)")
        print("2. Inserir lote maior (500 registros)")
        print("3. Inserção contínua (30s)")
        print("4. Inserção contínua rápida (5s)")
        print("5. Ver estatísticas atuais")
        print("6. Sair")
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        if escolha == '1':
            gerador.inserir_dados_batch_inicial(200)
            
        elif escolha == '2':
            gerador.inserir_dados_batch_inicial(500)
            
        elif escolha == '3':
            print("Pressione Ctrl+C para parar")
            gerador.inserir_dados_continuos(30)
            
        elif escolha == '4':
            print("Pressione Ctrl+C para parar")
            gerador.inserir_dados_continuos(5)
            
        elif escolha == '5':
            try:
                response = requests.get(f'{gerador.api_url}/dados/estatisticas')
                if response.status_code == 200:
                    stats = response.json()
                    print("\n=== ESTATÍSTICAS ATUAIS ===")
                    print(f"Total de registros: {stats.get('total_registros', 0):,}")
                    print(f"Humidade média: {stats.get('media_humidity', 0):.1f}%")
                    print(f"Temperatura média: {stats.get('media_temperature', 0):.1f}°C")
                    print(f"pH médio: {stats.get('media_ph', 0):.2f}")
                    print(f"Bombas ligadas: {stats.get('bombas_ligadas', 0)}")
                    print(f"Última coleta: {stats.get('ultima_coleta', 'N/A')}")
                else:
                    print("Erro ao obter estatísticas")
            except Exception as e:
                print(f"Erro: {e}")
                
        elif escolha == '6':
            print("Saindo...")
            break
            
        else:
            print("Opção inválida")

def exemplo_rapido():
    """Exemplo rápido para testar"""
    print("=== TESTE RÁPIDO ===")
    gerador = GeradorDadosIrrigacao()
    
    if not gerador.verificar_api():
        print("API não está rodando!")
        return
    
    print("Inserindo 50 registros de teste...")
    gerador.inserir_dados_batch_inicial(50)
    
    print("\nInserindo 10 registros em tempo real...")
    for i in range(10):
        dados = gerador.gerar_dados_realisticos()
        try:
            response = requests.post(
                f'{gerador.api_url}/dados',
                json=dados
            )
            if response.status_code == 201:
                print(f"✓ Registro {i+1}: H:{dados['humidity']:.1f}% "
                      f"T:{dados['temperature']:.1f}°C Bomba:{dados['bomba_status']}")
        except Exception as e:
            print(f"Erro: {e}")
        
        time.sleep(1)
    
    print("\n Teste concluído! Dados prontos para ML.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rapido':
        exemplo_rapido()
    else:
        menu_interativo()