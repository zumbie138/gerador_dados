from data_generator import DataGenerator
from database import Database
from interface import MenuInterface
from pdf_output import RelatorioPDF
from log_message import ErrorLogging

class Application:
    def __init__(self):
        log = ErrorLogging()
        self.logger = log.setup_logging()
        self.interface = MenuInterface(self.on_generate_report, self.logger)
        self.db = Database(self.logger)
        self.pdf = RelatorioPDF(self.logger)
    
    def on_generate_report(self, config):
        try:
            generator = DataGenerator(
                config.receita, 
                config.data, 
                config.hora, 
                config.camara
            )
            generator.ciclo_inicial()
            generator.ciclo_principal()
            generator.ciclo_encerramento()
            self.logger.info('Dados do relatório gerado')
            print('Dados do relatório gerado')
            
        except Exception as e:
            self.logger.error(f'Erro ao gerar os dados do relatório: {e}.')
            print(f'Erro ao gerar os dados do relatório: {e}.')
        
        try:
            self.db.update_database(generator.dados)
            self.logger.info(f'Novo relatório salvo no banco de dados: Receita:{config.receita}; Data:{config.data} {config.hora}; Camara: {config.camara}')
            print(f'Novo relatório salvo no banco de dados: Receita:{config.receita}; Data:{config.data} {config.hora}; Camara: {config.camara}')
        
        except Exception as e:
            self.logger.error(f'Erro ao salvar os dados do relatório no banco de dados: {e}.')
            print(f'Erro ao salvar os dados do relatório no banco de dados: {e}.')
            
        
        df = self.db.get_database(config.data)
        df_pdf = df.drop(['trilho','valvula','temperatura','pressao', 'id', 'camara'], axis=1)
        df_pdf = df_pdf[['data', 'hora', 'usuario', 'evento']]
        try:
            self.pdf.gerar_pdf(df_pdf)
            self.logger.info(f'PDF exportado com sucesso.')
            print(f'PDF exportado com sucesso.')

        except Exception as e:
            self.logger.error(f'Erro ao exportar dados para PDF: {e}.')
            print(f'Erro ao exportar dados para PDF: {e}.')
            
        

if __name__ == '__main__':
    try:
        app = Application()
        app.interface.mainloop()
    
    except Exception as e:
        print(f'Erro ao rodar o app: {e}')
        app.logger.critical(f'Erro ao rodar o app: {e}')
