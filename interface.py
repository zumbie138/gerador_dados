from abc import ABC, abstractmethod
from datetime import datetime
from tkinter import ttk, scrolledtext
import tkinter as tk
from typing import Optional, List, Callable
import pandas as pd
import sys
from contextlib import contextmanager
from header_data import HeaderData
import logging
import re

class LogManager:
    '''Gerenciador e centralizador de logs e redirecionamento'''
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._original_stdout = sys.stdout
        self._redirector: Optional['PrintRedirector'] = None
        self._log_widget: Optional[tk.Text] = None
        self.logger = logger
    
    def setup_widget(self, parent: tk.Widget) -> tk.Text:
        '''cria e configura widget de log'''
        if self._log_widget:
            return self._log_widget
        
        log_frame = tk.LabelFrame(
            parent,
            text='Console de Logs',
            font=('Arial', 10, 'bold')
        )
        log_frame.grid(row=1, column=0, sticky='nsew', pady=10, padx=10)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        self._log_widget = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=70,
            height=15,
            font=('Consolas', 9),
            bg='#1E1E1E',
            fg='#00FF00'
        )
        self._log_widget.grid(row=0, column=0, sticky='nsew', pady=5, padx=5)
        return self._log_widget

    def start_redirection(self):
        if self._log_widget:
            self._redirector = PrintRedirector(self._log_widget, self)
            sys.stdout = self._redirector
    
    def stop_redirection(self):
        sys.stdout = self._original_stdout
        self._redirector = None
    
    def log(self, message: str, level: str = 'INFO'):
        '''Log manual com níveis'''
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted = f'[{timestamp}] [{level}] {message}\n'
        
        if self._log_widget and self._log_widget.winfo_exists():
            self._log_widget.insert(tk.END, formatted)
            self._log_widget.see(tk.END)
        
        if self.logger:
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(message)
        
        self._original_stdout.write(formatted)

class PrintRedirector:
    """Classe para redirecionar prints para o widget de texto"""
    def __init__(self, text_widget: tk.Text, log_manager: LogManager):
        self.text_widget = text_widget
        self.log_manager = log_manager
        self._is_writing = False
    
    def write(self, string: str):
        if self._is_writing or not string:
            return
            
        self._is_writing = True
        try:
            string = string.rstrip()
            if not string:
                return
                
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted = f"[{timestamp}] {string}\n"
            
            # Log no widget da interface
            if self.text_widget.winfo_exists():
                self.text_widget.insert(tk.END, formatted)
                self.text_widget.see(tk.END)
                self.text_widget.update_idletasks()
            
            # Log usando o logger externo (se disponível)
            if self.log_manager.logger:
                # Determina o nível baseado no conteúdo
                if "erro" in string.lower() or "error" in string.lower():
                    self.log_manager.logger.error(string)
                elif "aviso" in string.lower() or "warning" in string.lower():
                    self.log_manager.logger.warning(string)
                else:
                    self.log_manager.logger.info(string)
                    
        except Exception:
            pass
        finally:
            self._is_writing = False
    
    def flush(self):
        pass

class BasePage(tk.Frame, ABC):
    '''CLasse base abastrata para todas as paginas'''
    
    def __init__(self, master, controller: 'MainController'):
        super().__init__(master)
        self.controller = controller
        self.log_manager = controller.log_manager
    
    @abstractmethod
    def apply_widgets(self):
        '''Configura interface da página'''
        pass
    
    def show_error(self, message:str):
        '''exibe mensagem de erro'''
        self.log_manager.log(message, 'ERROR')
    
    def show_info(self, message:str):
        '''exibe mensagem'''
        self.log_manager.log(message, 'INFO')

class MainController(tk.Tk):
    '''controlador principal da aplicação'''
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__()
        self.title('Gerador de relatórios')
        
        self.logger = logger
        
        self.log_manager = LogManager(logger)
        self._setup_ui()
        self._setup_pages()
        
        self.log_manager.start_redirection()
        
        self.protocol("WM_DELETE_WINDOW", self._safe_close)
        
        self.report_callback: Optional[Callable] = None
        self.query_callback: Optional[Callable] = None
        self.export_callback: Optional[Callable] = None
        
        
        self.show_page('generate')

    def _setup_ui(self):
        '''configura UI principal'''
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.page_container = tk.Frame(self)
        self.page_container.grid(row=0, column=0, sticky='nsew')
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)
        
        self.log_manager.setup_widget(self)
        
    
    def _setup_pages(self):
        self.pages = {}
        
        for PageClass, page_name in [
            (ReportGenerationPage, 'generate'),
            (ReportQueryPage, 'query')
        ]:
            page = PageClass(self.page_container, self)
            page.grid(row=0, column=0, sticky='nsew')
            self.pages[page_name] = page
    
    def show_page(self, page_name:str):
        page = self.pages.get(page_name)
        if page:
            page.tkraise()
            # self.log_manager.log(f'Navegando para: {page_name}')
        
    def register_callbacks(self, report_cb=None, query_cb=None, export_cb=None):
        self.report_callback = report_cb
        self.query_callback = query_cb
        self.export_callback = export_cb
    
    @contextmanager
    def safe_operation(self):
        """Context manager para operações seguras"""
        try:
            yield
        except Exception as e:
            self.log_manager.log(f"Erro: {str(e)}", "ERROR")
    
    def _safe_close(self):
        """Fecha a aplicação de forma segura"""
        with self.safe_operation():
            self.log_manager.log("Encerrando aplicação...")
            self.log_manager.stop_redirection()
            self.destroy()
    
class ReportGenerationPage(BasePage):
    def __init__(self, master, controller: 'MainController'):
        super().__init__(master, controller)
        self.config = HeaderData()
        self.camara_var = tk.StringVar()
        self.receita_var = tk.StringVar()
        self.data_var = tk.StringVar()
        self.hora_var = tk.StringVar()
        
        self.apply_widgets()

    def apply_widgets(self):
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        #monitoramente da aspersão :grid 0, 0
        tk.Label(self, text='MONITORAMENTE DA ASPERSÃO').grid(row=0, column=0, columnspan=2, pady=(0, 10))
        #selecionar a câmara :grid 1, 0
        tk.Label(self, text='Selecionar Câmara:').grid(row=1, column=0, pady=2)
        #combobox, da camara 1 a camara 12: grid 1, 1
        ttk.Combobox(
            self,
            textvariable= self.camara_var,
            values=['CAM01','CAM02','CAM03','CAM04','CAM05','CAM06',
                    'CAM07','CAM08','CAM09','CAM10','CAM11','CAM12']
           ).grid(row=1, column=1, padx=(10, 0))
        #selecionar receita : grid 2, 0
        tk.Label(self, text='Selecionar Receita').grid(row=2, column=0,pady=2)
        #combobox da receita 1, 2 ou 3 : grid 2, 1
        ttk.Combobox(
            self,
            textvariable= self.receita_var,
            values=['RECEITA 01','RECEITA 02','RECEITA 03']
        ).grid(row= 2,column= 1, padx=(10, 0))
        #data de inicio : grid 3, 0
        tk.Label(self, text='Data de início: ').grid(row=3, column=0, pady=2)
        #entry da data de inicio : grid 3, 1
        tk.Entry(
            self,
            textvariable=self.data_var,
            state='normal'
        ).grid(row=3, column=1, padx=(10, 0))
        #hora de inicio : grid 4, 0
        tk.Label(self, text='Hora de Início: ').grid(row=4, column=0)
        #entry da hora de inicio : grid 4, 1
        tk.Entry(
            self,
            textvariable=self.hora_var,
            state='normal'
        ).grid(row=4, column=1, padx=(10, 0))
        #botao de gerar relatorio 5, 0
        tk.Button(
            self,
            text='GERAR RELATÓRIO',
            command=self._generate_report
        ).grid(row=5, column=0, columnspan=2, pady=15)
        
        #botao para mudar de frame
        tk.Button(
            self,
            text='Consultar relátorios',
            command=lambda: self.controller.show_page('query')
        ).grid(row=6, column=2)
    

    
    def _generate_report(self):
        self.config.camara = self.camara_var.get()
        self.config.receita = self.receita_var.get()
        self.config.data = self.data_var.get()
        self.config.hora = self.hora_var.get()

        is_valid, error_msg = self.config.validate()
        if not is_valid:
            self.show_error(error_msg)
            return
        
        self.show_info(f'Gerando relatório para {self.config.camara} - {self.config.receita}')
        
        if self.controller.report_callback:
            self.controller.report_callback(self.config)
        
class ReportQueryPage(BasePage):
    def __init__(self, master, controller: 'MainController'):
        super().__init__(master, controller)
        
        self.data_inicio = tk.StringVar()
        self.data_fim = tk.StringVar()
        self.checkboxes_frame : Optional[tk.Frame] = None
        self.check_vars : List[tk.BooleanVar] = []
        self.df_list : List[pd.DataFrame] = []
        self.apply_widgets()
    
    def apply_widgets(self):
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(1, weight=1)
        tk.Label(
            self, 
            text='CONSULTA DE RELATORIOS'
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        tk.Label(self, text='Data inicial').grid(row=1, column=0, pady=(0, 10))
        tk.Entry(self, textvariable=self.data_inicio, state='normal').grid(row=1, column=1)
        tk.Label(self, text='Data final').grid(row=2, column=0, pady=(0, 10))
        tk.Entry(self, textvariable=self.data_fim, state='normal').grid(row=2, column=1)
        tk.Button(
            self,
            text='CONSULTAR',
            command=self._on_query
        ).grid(row=3, column=0, columnspan=2)
        
        self.checkboxes_frame = tk.Frame(self)
        self.checkboxes_frame.grid(row=4, column=0, columnspan=2, sticky='nsew', pady=10)
        button_frame = tk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        tk.Button(
            button_frame,
            text='Voltar',
            command=lambda: self.controller.show_page('generate')
        ).pack(side=tk.LEFT, padx=5)
        
        self.export_button = tk.Button(
            button_frame,
            text='EXPORTAR PDF',
            command=self._on_export,
            bg='#FF9800',
            fg='white',
            state='disabled'
        )
        self.export_button.pack(side=tk.LEFT, padx=5)
    
    def _on_query(self):
        data_inicio = self.data_inicio.get()
        data_fim = self.data_fim.get()
        
        for date_str, name in [(data_inicio, "inicial"), (data_fim, "final")]:
            try:
                datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                self.show_error(f"Data {name} inválida")
                return
        
        self.show_info(f'Consultando relatórios de {data_inicio} a {data_fim}')
        
        self._clear_checkboxes()
        
        if self.controller.query_callback:
            self.df_list = self.controller.query_callback(data_inicio, data_fim)
            self._apply_checkbox()
    
    def _clear_checkboxes(self):
        for widget in self.checkboxes_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()
        
    def _get_row_text(self, row_text:str):
        padrao_receita = r'(RECEITA \d{2})'
        padrao_cam = r'(CAM\d{1,2})'
        receita_match = re.search(padrao_receita, row_text)
        cam_match = re.search(padrao_cam, row_text)
        
        receita = receita_match.group(1) if receita_match else None
        cam = cam_match.group(1) if cam_match else None
    
        return receita, cam
        
    def _apply_checkbox(self):
        if not self.df_list:
            tk.Label(
                self.checkboxes_frame,
                text='Nenhum relatório encontrado no período',
                fg='grey'
            ).pack()
            self.export_button.config(state='disabled')
            return
        
        for i, df in enumerate(self.df_list):
            var = tk.BooleanVar()
            self.check_vars.append(var)
            first_row = df.iloc[0]
            data = first_row['data']
            hora = first_row['hora']
            evento = first_row['evento']
            receita, cam = self._get_row_text(evento)
            tk.Checkbutton(
                self.checkboxes_frame,
                text=f'RELATÓRIO {i+1}: {cam} - {receita} - {data} - {hora}',
                variable=var
            ).pack(anchor='w', pady=2)
            
        self.export_button.config(state='normal') 
        
    def _on_export(self):
        
        selecionados = [self.df_list[i] for i, var in enumerate(self.check_vars) if var.get()]
        
        if not selecionados:
            self.show_error('Selecione pelo menos um relatório')
            return


        combined_df = pd.concat(selecionados, ignore_index=True)
        self.show_info(f"Exportando {len(combined_df)} registros para PDF")
        
        if self.controller.export_callback:
            self.controller.export_callback(combined_df)
        
        