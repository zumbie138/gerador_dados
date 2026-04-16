from header_data import HeaderData
from datetime import datetime
from tkinter import ttk, scrolledtext
import tkinter as tk
import sys
import os

class PrintRedirector:
    """Classe para redirecionar prints para o widget de texto"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        try:
            self.stdout = sys.stdout
            if self.stdout is None:
                self.stdout = sys.stderr
        except:
            self.stdout = None

        self._is_writing = False
    
    def write(self, string):
        # Evita recursão infinita
        if self._is_writing:
            return
            
        self._is_writing = True
        
        try:
            # Verifica se o widget ainda existe e está válido
            if self.text_widget and self.text_widget.winfo_exists():
                # Adiciona timestamp para melhor visualização
                if string.strip():  # Só adiciona timestamp se não for linha vazia
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    formatted_string = f"[{timestamp}] {string}"
                else:
                    formatted_string = string
                    
                # Insere o texto no widget
                self.text_widget.insert(tk.END, formatted_string)
                self.text_widget.see(tk.END)  # Auto-scroll
                self.text_widget.update_idletasks()
            
            # Tenta escrever no stdout original de forma segura
            if self.stdout and hasattr(self.stdout, 'write'):
                try:
                    self.stdout.write(string)
                    if hasattr(self.stdout, 'flush'):
                        self.stdout.flush()
                except:
                    # Se falhar, silenciosamente ignora
                    pass
                    
        except Exception as e:
            # Em caso de erro, tenta apenas escrever no stdout original
            if self.stdout and hasattr(self.stdout, 'write'):
                try:
                    self.stdout.write(string)
                except:
                    pass
        finally:
            self._is_writing = False
    
    def flush(self):
        if self.stdout and hasattr(self.stdout, 'flush'):
            try:
                self.stdout.flush()
            except:
                pass

class MenuInterface(tk.Tk):
    def __init__(self, callback=None, logger=None):
        super().__init__()
        self.title('Gerador de relatórios')
        self.config = HeaderData()
        self.callback = callback
        self.logger = logger
        
        self.camara_var = tk.StringVar()
        self.receita_var = tk.StringVar()
        self.data_var = tk.StringVar()
        self.hora_var = tk.StringVar()
        
        self._apply_widgets()
        self._setup_log_console()
        
        self.print_redirector = PrintRedirector(self.log_text)
        self._original_stdout = sys.stdout
        sys.stdout = self.print_redirector
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _on_closing(self):
        """Restaura stdout original ao fechar a janela"""
        if hasattr(self, '_original_stdout'):
            sys.stdout = self._original_stdout
        self.destroy()
    
    def _apply_widgets(self):
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10, padx=10, fill=tk.X)
        
        #monitoramente da aspersão :grid 0, 0
        tk.Label(control_frame, text='MONITORAMENTE DA ASPERSÃO').grid(row=0, column=0, columnspan=2, pady=(0, 10))
        #selecionar a câmara :grid 1, 0
        tk.Label(control_frame, text='Selecionar Câmara:').grid(row=1, column=0, pady=2)
        #combobox, da camara 1 a camara 12: grid 1, 1
        ttk.Combobox(
            control_frame,
            textvariable= self.camara_var,
            values=['CAM01','CAM02','CAM03','CAM04','CAM05','CAM06',
                    'CAM07','CAM08','CAM09','CAM10','CAM11','CAM12']
           ).grid(row=1, column=1, padx=(10, 0))
        #selecionar receita : grid 2, 0
        tk.Label(control_frame, text='Selecionar Receita').grid(row=2, column=0,pady=2)
        #combobox da receita 1, 2 ou 3 : grid 2, 1
        ttk.Combobox(
            control_frame,
            textvariable= self.receita_var,
            values=['RECEITA 01','RECEITA 02','RECEITA 03']
        ).grid(row= 2,column= 1, padx=(10, 0))
        #data de inicio : grid 3, 0
        tk.Label(control_frame, text='Data de início: ').grid(row=3, column=0, pady=2)
        #entry da data de inicio : grid 3, 1
        tk.Entry(
            control_frame,
            textvariable=self.data_var,
            state='normal'
        ).grid(row=3, column=1, padx=(10, 0))
        #hora de inicio : grid 4, 0
        tk.Label(control_frame, text='Hora de Início: ').grid(row=4, column=0)
        #entry da hora de inicio : grid 4, 1
        tk.Entry(
            control_frame,
            textvariable=self.hora_var,
            state='normal'
        ).grid(row=4, column=1, padx=(10, 0))
        #botao de gerar relatorio 5, 0
        tk.Button(
            control_frame,
            text='GERAR RELATÓRIO',
            command=self._generate_report
        ).grid(row=5, column=0, columnspan=2, pady=15)
    
    def _setup_log_console(self):
        log_frame = tk.LabelFrame(
            self,
            text='Console de Logs',
            font=('Arial', 10, 'bold')
        )
        log_frame.pack(
            pady=10,
            padx=10,
            fill=tk.BOTH,
            expand=True
        )
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=70,
            height=15,
            font=('Consolas', 9),
            bg='#1E1E1E',
            fg='#00FF00'
        )
        self.log_text.pack(
            pady=5,
            padx=5,
            fill=tk.BOTH,
            expand=True
        )
    
    def datetime_valido(self, valor, formato):
        try:
            datetime.strptime(valor, formato)
            return True
        except ValueError:
            return False
    
    def _generate_report(self):
        self.config.camara = self.camara_var.get()
        self.config.receita = self.receita_var.get()
        self.config.data = self.data_var.get()
        self.config.hora = self.hora_var.get()

        if not self.datetime_valido(self.config.data, "%d/%m/%Y"):
            print('Data não está no formato certo')
            self.logger.warning('Data não está no formato certo')
            
        elif not self.datetime_valido(self.config.hora, "%H:%M:%S"):
            print('Hora não está no formato certo')
            self.logger.warning('Hora não está no formato certo')
        else:
            if self.callback:
                self.callback(self.config)
        
