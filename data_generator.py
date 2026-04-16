import random
from datetime import datetime, timedelta
import pandas as pd

class DataGenerator:
    def __init__(self, receita, data, hora, camara):
        self.receita = receita
        self.data = data
        self.hora = hora
        self.camara = camara
        self.dados = []
        
        self.hora_ciclo = None
        
        self.receita_minutos = {
            'RECEITA 01': 480,
            'RECEITA 02': 360,
            'RECEITA 03': 180
        }

        self.camara_valvulas = {
            'CAM01': [8, 1],
            'CAM02': [8, 9],
            'CAM03': [7, 17],
            'CAM04': [7, 24],
            'CAM05': [7, 31],
            'CAM06': [7, 38],
            'CAM07': [7, 45],
            'CAM08': [7, 52],
            'CAM09': [7, 59],
            'CAM10': [7, 66],
            'CAM11': [7, 73],
            'CAM12': [7, 80]
        }
    
    def _gerar_dados_aleatorios(self) -> tuple:
        valvula_trilho = self.camara_valvulas[self.camara]
        trilho = random.randint(1, valvula_trilho[0])
        valvula = random.randint(valvula_trilho[1], (valvula_trilho[1] + valvula_trilho[0] - 1))
        segundo_acionameto = random.randint(0, 59)
        pressao = random.uniform(3.0, 3.8)
        temperatura = random.uniform(2.0, 3.8)
        return (trilho, valvula, segundo_acionameto, temperatura, pressao)
    
    def _calcular_hora(self, hora_calculada, minutos, segundos):
        if isinstance(hora_calculada, str):
            return (datetime.strptime(hora_calculada, '%H:%M:%S') - timedelta(minutes=minutos, seconds=segundos))
        elif isinstance(hora_calculada, datetime):
            return (hora_calculada + timedelta(minutes=minutos, seconds=segundos))
        
    def ciclo_inicial(self):
        hora_ligamento = self._calcular_hora(self.hora, 0, 39)
        self.dados.append({
            'Evento': f'CARREGOU A {self.receita} NA {self.camara}',
            'Data': f'{self.data}',
            'Hora': f'{hora_ligamento.time()}',
            'Câmara': self.camara, 
            'Usuário': 'gq',
            'trilho': None,
            'Válvula': None,
            'Temperatura (°C)': None,
            'Pressão (bar)': None
        })
        valvulas = self.camara_valvulas[self.camara]
        for i in range(valvulas[0]):
            valv = valvulas[1] + i
            segundo_acionameto = random.randint(11, 50)
            hora_ligamento = self._calcular_hora(hora_ligamento, 0, segundo_acionameto)
            self.dados.append({
                'Evento': f'HABILITOU PROCESSO: {self.camara} - VALV{valv}, {self.receita}',
                'Data': f'{self.data}',
                'Hora': f'{hora_ligamento.time()}',
                'Câmara': self.camara, 
                'Usuário': 'gq',
                'trilho': f'Trilho {i+1}',
                'Válvula': f'V{valv}',
                'Temperatura (°C)': None,
                'Pressão (bar)':None
            })
        segundo_acionameto = random.randint(11, 50)
        self.hora_ciclo = self._calcular_hora(hora_ligamento, 0, segundo_acionameto)
    
    def ciclo_principal(self):
        ciclo = round(self.receita_minutos[self.receita] / 3)
        for i in range(int(ciclo)):
            trilho, valvula, segundo_acionamento, temperatura, pressao = self._gerar_dados_aleatorios()
            hora = self._calcular_hora(self.hora_ciclo, 0, segundo_acionamento)
            self.hora_ciclo = self._calcular_hora(self.hora_ciclo, 3, 0)
            self.dados.append({
                'Evento': f'TEMPERATURA = {temperatura:.1f}°C, PRESSÃO = {pressao:.1f} bar',
                'Data': f'{self.data}',
                'Hora': f'{hora.time()}',
                'Câmara': self.camara,
                'Usuário': 'SISTEMA',
                'trilho': f'Trilho {trilho}',
                'Válvula': f'V{valvula}',
                'Temperatura (°C)': f'{temperatura:.2f}',
                'Pressão (bar)': f'{pressao:.2f}'
            })
    
    def ciclo_encerramento(self):
        valvulas = self.camara_valvulas[self.camara]
        hora = self.hora_ciclo
        for i in range(valvulas[0]):
            _, valvula, segundo_acionamento, *_ = self._gerar_dados_aleatorios()
            valv_num = valvulas[1] + i
            hora = self._calcular_hora(hora, 0, segundo_acionamento) 
            self.dados.append({
                'Evento': f'DESABILITOU PROCESSO: {self.camara}- VALV{valv_num},  {self.receita}',
                'Data': f'{self.data}',
                'Hora': f'{hora.time()}',
                'Câmara': self.camara,
                'Usuário': 'SISTEMA',
                'trilho': f'Trilho {i+1}',
                'Válvula': f'V{valvula}',
                'Temperatura (°C)': None,
                'Pressão (bar)': None
            })
            
