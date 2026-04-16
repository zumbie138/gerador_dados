import os
import sys
from pathlib import Path

class PathManager:
    @staticmethod
    def get_base_path():
        '''Retorna o caminho base da aplicação(funciona tanto para .exe quanto em dev)'''
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(__file__).parent
        
    @classmethod
    def get_resource_path(cls, relative_path):
        '''Retorna caminho absoluto para recursos empacotados'''
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        
        else:
            base_path = cls.get_base_path()
            
        return base_path / relative_path
    
    @classmethod
    def get_data_path(cls, relative_path):
        '''Retorna caminho para daods que podem ser modificados'''
        base_path = cls.get_base_path()
        
        if os.name == 'nt' and getattr(sys, 'frozen', False):
            app_data = Path(os.getenv('APPDATA')) / 'GeradorDadosFreezer'
            app_data.mkdir(parents=True, exist_ok=True)
            return app_data / relative_path
        else:
            return base_path / relative_path
    
    @classmethod
    def ensure_data_directory(cls):
        '''Garante que os diretórios de dados existem'''
        data_path = cls.get_data_path('')
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path