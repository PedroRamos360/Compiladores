from typing import Dict, Optional


class Simbolo:
    def __init__(self, nome: str, tipo: str) -> None:
        self.nome = nome
        self.tipo = tipo


class TabelaDeSimbolos:
    def __init__(self) -> None:
        self._simbolos: Dict[str, Simbolo] = {}

    def definir(self, simbolo: Simbolo) -> None:
        self._simbolos[simbolo.nome] = simbolo

    def buscar(self, nome: str) -> Optional[Simbolo]:
        return self._simbolos.get(nome)
