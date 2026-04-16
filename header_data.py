from dataclasses import dataclass


@dataclass
class HeaderData:
    camara: str = ''
    receita: str = ''
    data: str = ''
    hora: str = ''
