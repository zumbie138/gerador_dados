import logging
from logging.handlers import RotatingFileHandler

class ErrorLogging():
    def __init__(self):
        self.logger = logging.getLogger('GeradorRelatorios')
        self.logger.setLevel(logging.INFO)
        
    def setup_logging(self):
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            

            file_handler = RotatingFileHandler(
                'log_gerador_relatorios.log', 
                maxBytes=10*1024*1024, 
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            return self.logger