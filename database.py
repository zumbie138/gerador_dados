import sqlite3
import pandas as pd
from typing import List
from path_manager import PathManager

class Database:
    def __init__(self, logger = None):
        self.logger = logger
        self.path_manager = PathManager()
        self.db_path = self.path_manager.get_data_path('dados_relatorio.db')
        self.create_database()
    
    def create_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dadosfreezer(
            id INTEGER PRIMARY KEY,
            evento TEXT,
            data TEXT,
            hora TEXT,
            camara TEXT,
            usuario TEXT,
            trilho TEXT,
            valvula TEXT,
            temperatura TEXT,
            pressao TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def update_database(self, data_list: list):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
        INSERT OR REPLACE INTO dadosfreezer(
            evento, data, hora, camara, usuario, trilho, valvula, temperatura, pressao
        )
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        try:
            for data in data_list:
                valores = (
                    data['Evento'],
                    data['Data'],
                    data['Hora'],
                    data['Câmara'],
                    data['Usuário'],
                    data['trilho'],
                    data['Válvula'],
                    data['Temperatura (°C)'],
                    data['Pressão (bar)']
                )
                cursor.execute(query, valores)
            conn.commit()
        
        except Exception as e:
            print(f'Erro ao salvar dados no banco de dados: {e}')
            self.logger.error(f'Erro ao salvar dados no banco de dados: {e}')
            conn.rollback()
            
        finally:
            conn.close()
    
    def get_database(self, date:str) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
        SELECT * FROM dadosfreezer
        '''
        
        df = pd.read_sql_query(query, con=conn)
        
        conn.close()
        df_filtered = df[df['data'] == date]
        return df_filtered

    def get_dataframes_list(self, start_date:str, end_date:str) -> List[pd.DataFrame]:

        query = f'''
        SELECT * 
        FROM dadosfreezer 
        WHERE 
            -- Converter data dd/mm/yyyy para YYYY-MM-DD para comparação
            substr(data, 7, 4) || '-' || substr(data, 4, 2) || '-' || substr(data, 1, 2)
            BETWEEN
            substr(?, 7, 4) || '-' || substr(?, 4, 2) || '-' || substr(?, 1, 2)
            AND
            substr(?, 7, 4) || '-' || substr(?, 4, 2) || '-' || substr(?, 1, 2)
        ORDER BY 
            substr(data, 7, 4) || '-' || substr(data, 4, 2) || '-' || substr(data, 1, 2)
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                query,
                conn,
                params=(start_date, start_date, start_date, end_date, end_date, end_date)
            )
        grupos = df.groupby('timestamp')
        
        lista_df = [grupo for _, grupo in grupos]
        
        return lista_df