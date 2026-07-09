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
    
    def _verificar_data(self, hora, hora_anterior):
        if hora.time() < hora_anterior.time():
            self.data = (datetime.strptime(self.data, '%d/%m/%Y') + timedelta(days=1)).strftime('%d/%m/%Y')
    
    def _adicionar_dados(self, evento, camara, data, hora, usuario, trilho, valvula, temperatura, pressao):
        self.dados.append({
            'Evento': evento,
            'Data': f'{data}',
            'Hora': f'{hora}',
            'Câmara': camara, 
            'Usuário': usuario,
            'trilho': trilho,
            'Válvula': valvula,
            'Temperatura (°C)': temperatura,
            'Pressão (bar)': pressao
        })
        
    def ciclo_inicial(self):
        hora_ligamento = self._calcular_hora(self.hora, 0, 39)
        hora_anterior = hora_ligamento
        self._adicionar_dados(
           f'CARREGOU A {self.receita} NA {self.camara}',
           self.camara, self.data, hora_ligamento.time(),
            'gq', None, None, None, None
        )
        valvulas = self.camara_valvulas[self.camara]
        for i in range(valvulas[0]):
            valv = valvulas[1] + i
            segundo_acionameto = random.randint(11, 50)
            hora_ligamento = self._calcular_hora(hora_ligamento, 0, segundo_acionameto)
            self._verificar_data(hora_ligamento, hora_anterior)
            self._adicionar_dados(
                f'HABILITOU PROCESSO: {self.camara} - VALV{valv}, {self.receita}',
                self.camara, self.data, hora_ligamento.time(), 'gq',
                f'Trilho {i+1}', f'V{valv}', None, None
            )
            hora_anterior = hora_ligamento
        segundo_acionameto = random.randint(11, 50)
        self.hora_ciclo = self._calcular_hora(hora_ligamento, 0, segundo_acionameto)
    
    def ciclo_principal(self):
        ciclo = round(self.receita_minutos[self.receita] / 3)
        hora_anterior = self.hora_ciclo
        for i in range(int(ciclo)):
            trilho, valvula, segundo_acionamento, temperatura, pressao = self._gerar_dados_aleatorios()
            hora = self._calcular_hora(self.hora_ciclo, 0, segundo_acionamento)
            self.hora_ciclo = self._calcular_hora(self.hora_ciclo, 3, 0)
            self._verificar_data(hora, hora_anterior)
            self._adicionar_dados(
                f'TEMPERATURA = {temperatura:.1f}°C, PRESSÃO = {pressao:.1f} bar',
                self.camara, self.data, hora.time(), 'SISTEMA', f'Trilho {trilho}',
                f'V{valvula}', f'{temperatura:.2f}', f'{pressao:.2f}'
            )
            hora_anterior = hora
    
    def ciclo_encerramento(self):
        valvulas = self.camara_valvulas[self.camara]
        hora = self.hora_ciclo
        hora_anterior = hora
        for i in range(valvulas[0]):
            _, valvula, segundo_acionamento, *_ = self._gerar_dados_aleatorios()
            valv_num = valvulas[1] + i
            hora = self._calcular_hora(hora, 0, segundo_acionamento)
            self._verificar_data(hora, hora_anterior)
            self._adicionar_dados(
                f'DESABILITOU PROCESSO: {self.camara}- VALV{valv_num},  {self.receita}',
                self.camara, self.data, hora.time(), 'SISTEMA', f'Trilho {i+1}',
                f'V{valvula}', None, None
            )
            hora_anterior = hora
