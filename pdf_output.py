from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from path_manager import PathManager
import os
import sys
from pathlib import Path
import pandas as pd

class RelatorioPDF:
    def __init__(self, logger = None):
        self.logger = logger
        self.path_manager = PathManager()
        
        self._pdf_path = self.path_manager.get_data_path('relatorio_camaras.pdf')
        self._icon_path = self.path_manager.get_resource_path('icone.png')
        
        self.path_manager.ensure_data_directory()
        
        if not self._icon_path.exists():
            self.logger.warning(f'Aviso: Ícone não encontrado em {self._icon_path}')
            print(f'Aviso: Ícone não encontrado em {self._icon_path}')
            if getattr(sys, 'frozen', False):
                temp_dir = Path(sys._MEIPASS)
                print(f'Conteúdo do diretório temporário({temp_dir})')
                self.logger.info(f'Conteúdo do diretório temporário({temp_dir})')
                for file in temp_dir.iterdir():
                    self.logger.info(f' - {file.name}')
                    print(f' - {file.name}')
        
        self.nome_arquivo = str(self._pdf_path)
        self.icon_path = str(self._icon_path) if self._icon_path.exists() else None
        
        self.doc = SimpleDocTemplate(
            self.nome_arquivo, 
            pagesize=A4, 
            topMargin=1*cm,
            bottomMargin=1.5*cm,
            leftMargin=1*cm,
            rightMargin=1*cm
        )
        self.elements = []
        self.total_pages = 1
        
        self.styles = getSampleStyleSheet()
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.red,
            alignment=TA_CENTER,
            spaceAfter=2,
            leading=18
        )
        
        self.subheader_style = ParagraphStyle(
            'CustomSubHeader',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.red,
            alignment=TA_CENTER,
            spaceAfter=8,
            leading=18
        )
        
        self.footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=7,
            textColor=colors.red,
            alignment=TA_RIGHT
        )
    
    def cabecalho_principal(self):
        """Adiciona o cabeçalho principal com logo no canto superior esquerdo"""
        
        if self.icon_path and Path(self.icon_path).exists():
            from reportlab.platypus import Frame, KeepTogether
            
            # Criar um container para manter imagem e texto juntos
            from reportlab.platypus import Paragraph, Spacer, Image, Table
            
            # Carregar imagem
            img = Image(self.icon_path)
            img.drawHeight = 0.40 * inch  # Altura ajustada
            img.drawWidth = img.drawHeight * (img.imageWidth / img.imageHeight) * 2.4
            
            # Criar uma tabela 2x2 para melhor controle vertical
            header1 = Paragraph("RELATÓRIO DE ASPERSÃO DE CARCAÇAS", self.header_style)
            header2 = Paragraph("UNIDADE CAMPO GRANDE I - CPG", self.subheader_style)
            
            # Estrutura: [Imagem] [Título    ]
            #           [       ] [Subtítulo ]
            dados_tabela = [
                [img, header1],
                ['', header2]
            ]
            
            cabecalho_table = Table(
                dados_tabela,
                colWidths=[img.drawWidth + 10, self.doc.width - img.drawWidth - 20],
                rowHeights=[0.25 * inch, 0.25 * inch]  # Alturas específicas para cada linha
            )
            
            cabecalho_table.setStyle(TableStyle([
                # Alinhamentos
                ('VALIGN', (0, 0), (0, 0), 'BOTTON'),
                ('VALIGN', (1, 0), (1, 1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 1), 'CENTER'),
                # Remover paddings
                ('LEFTPADDING', (0, 0), (0, -1), 0),
                ('RIGHTPADDING', (1, 0), (1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            self.elements.append(cabecalho_table)
            self.elements.append(Spacer(1, 0.15*inch))
        else:
            header1 = Paragraph("RELATÓRIO DE ASPERSÃO DE CARCAÇAS", self.header_style)
            header2 = Paragraph("UNIDADE CAMPO GRANDE I - CPG", self.subheader_style)
            self.elements.append(header1)
            self.elements.append(header2)
            self.elements.append(Spacer(1, 0.15*inch))
    
    def calcular_larguras_colunas(self, df):
        """Calcula larguras proporcionais para as 4 colunas"""
        
        largura_total = self.doc.width - 10  # Margem pequena
        
        # Define as proporções
        proporcao_data_hora = 1      # Menor tamanho
        proporcao_usuario = 1.5      # Um pouco maior
        proporcao_evento = 6         # 60% seria 60, mas ajustado para proporção
        
        # Calcula total das proporções
        total_proporcao = (proporcao_data_hora * 2) + proporcao_usuario + proporcao_evento
        
        # Calcula larguras em pontos
        largura_data_hora = (proporcao_data_hora / total_proporcao) * largura_total
        largura_usuario = (proporcao_usuario / total_proporcao) * largura_total
        largura_evento = (proporcao_evento / total_proporcao) * largura_total
        
        # Garante larguras mínimas
        largura_data_hora = max(50, largura_data_hora)
        largura_usuario = max(55, largura_usuario)
        largura_evento = max(200, largura_evento)
        
        # Retorna lista de larguras na ordem das colunas
        col_widths = [largura_data_hora, largura_data_hora, largura_usuario, largura_evento]
        
        return col_widths
    
    def calcular_larguras_percentuais(self, df):
        """Calcula larguras baseadas em porcentagens"""
        largura_total = self.doc.width
        
        # Define porcentagens para cada coluna
        # Data e Hora: 12% cada
        # Usuario: 16%
        # Evento: 60%
        porcentagens = [0.12, 0.12, 0.16, 0.60]  # data, hora, usuario, evento
        
        # Calcula larguras baseadas nas porcentagens
        col_widths = [largura_total * pct for pct in porcentagens]
        
        # Garante larguras mínimas
        col_widths = [max(45, width) for width in col_widths]
        
        return col_widths
    
    def criar_tabela(self, dados):
        """Cria a tabela com 4 colunas: data, hora, usuario, evento"""
        df = pd.DataFrame(dados)
        
        # Garantir que as colunas estão na ordem correta
        colunas_ordenadas = ['data', 'hora', 'usuario', 'evento']
        
        # Verificar se as colunas existem no DataFrame
        for col in colunas_ordenadas:
            if col not in df.columns:
                df[col] = '-'  # Adiciona coluna vazia se não existir
        
        # Reordenar as colunas
        df = df[colunas_ordenadas]
        
        # Coloca os títulos em CAIXA ALTA
        headers = ['DATA', 'HORA', 'USUÁRIO', 'EVENTO']
        
        # Calcular larguras das colunas
        # Opção 1: Usar método de proporções
        col_widths = self.calcular_larguras_colunas(df)
        
        # Opção 2: Usar método de porcentagens (descomente se preferir)
        # col_widths = self.calcular_larguras_percentuais(df)
        
        # Criar cabeçalhos com fundo cinza
        header_cells = []
        for header in headers:
            header_style = ParagraphStyle(
                'HeaderCell',
                parent=self.styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=9,
                textColor=colors.whitesmoke,
                alignment=TA_CENTER
            )
            p = Paragraph(header, header_style)
            header_cells.append(p)
        
        # Preparar dados
        table_data = [header_cells]
        
        for _, row in df.iterrows():
            row_cells = []
            for col, value in zip(colunas_ordenadas, row):
                if value is None or pd.isna(value):
                    text = '-'
                else:
                    text = str(value)
                
                # Definir alinhamento baseado na coluna
                if col in ['data', 'hora']:
                    alignment = TA_CENTER
                elif col == 'usuario':
                    alignment = TA_CENTER
                else:  # evento
                    alignment = TA_LEFT
                
                data_style = ParagraphStyle(
                    'DataCell',
                    parent=self.styles['Normal'],
                    fontName='Helvetica',
                    fontSize=8,  # Fonte um pouco maior para legibilidade
                    alignment=alignment,
                    leading=8
                )
                
                # Para a coluna evento, permitir quebra de linha
                if col == 'evento':
                    # Dividir texto longo em múltiplas linhas
                    if len(text) > 80:
                        # Insere quebras de linha a cada 80 caracteres
                        text = '\n'.join([text[i:i+80] for i in range(0, len(text), 80)])
                
                p = Paragraph(text, data_style)
                row_cells.append(p)
            table_data.append(row_cells)
        
        # Criar tabela com larguras calculadas
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo da tabela
        style_commands = [
            # Cabeçalhos - fundo cinza
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
        ]
        
        # Bordas individuais para cada célula do cabeçalho
        for col in range(len(headers)):
            style_commands.append(('BOX', (col, 0), (col, 0), 0.3, colors.black))
        
        # Estilos dos dados
        style_commands.extend([
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),  # Top para eventos longos
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING', (0, 1), (-1, -1), 4),
            ('RIGHTPADDING', (0, 1), (-1, -1), 4),
            
            # Linha pontilhada entre linhas
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.black, None, (2, 2)),
            ('LINEBELOW', (0, -1), (-1, -1), 0.3, colors.black),
            
            # Bordas laterais externas
            ('LINELEFT', (0, 1), (0, -1), 0.2, colors.black),
            ('LINERIGHT', (-1, 1), (-1, -1), 0.2, colors.black),
        ])
        
        # Alinhamento específico por coluna
        # Data e Hora: centralizado
        style_commands.append(('ALIGN', (0, 1), (0, -1), 'CENTER'))  # Data
        style_commands.append(('ALIGN', (1, 1), (1, -1), 'CENTER'))  # Hora
        style_commands.append(('ALIGN', (2, 1), (2, -1), 'CENTER'))  # Usuário
        style_commands.append(('ALIGN', (3, 1), (3, -1), 'LEFT'))    # Evento
        
        table.setStyle(TableStyle(style_commands))
        return table
    
    def numero_paginas(self, canvas, doc):
        """Adiciona numeração de páginas"""
        page_num = canvas.getPageNumber()
        
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.red)
        
        x = doc.width + doc.leftMargin - 10
        y = doc.bottomMargin - 15
        
        canvas.drawRightString(x, y, f"Página {page_num} de {self.total_pages}")
        
        canvas.restoreState()
    
    def gerar_pdf(self, df):
        """Gera o PDF completo"""
        self.cabecalho_principal()
        

        rows_per_page = 35  # Menos linhas porque evento pode ser longo
        
        # Calcular total de páginas
        total_pages = (len(df) + rows_per_page - 1) // rows_per_page
        if total_pages == 0:
            total_pages = 1
        self.total_pages = total_pages
        
        for i in range(0, len(df), rows_per_page):
            if i > 0:
                self.elements.append(PageBreak())
                self.cabecalho_principal()
            
            page_data = df.iloc[i:i+rows_per_page].to_dict('records')
            
            if page_data:
                tabela = self.criar_tabela(page_data)
                self.elements.append(tabela)
                self.elements.append(Spacer(1, 0.05*inch))
        
        self.doc.build(
            self.elements,
            onFirstPage=self.numero_paginas,
            onLaterPages=self.numero_paginas
        )
        
        print(f"PDF gerado no path: {self.nome_arquivo}")


