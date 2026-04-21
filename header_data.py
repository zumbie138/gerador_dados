from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class HeaderData:
    camara: str = ''
    receita: str = ''
    data: str = ''
    hora: str = ''

    def validate(self) -> tuple[bool, Optional[str]]:
        if not self.camara:
            return False, 'Câmara não selecionada'
        if not self.receita:
            return False, 'Receita não selecionada'
        
        try:
            datetime.strptime(self.data, "%d/%m/%Y")
        except ValueError:
            return False, 'Data inválida (use DD/MM/AAAA)'
        
        try:
            datetime.strptime(self.hora, "%H:%M:%S")
        except ValueError:
            return False, 'Hora inválida (use HH:MM:SS)'
        
        return True, None