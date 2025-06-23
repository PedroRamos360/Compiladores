class Simbolo:
    def __init__(self, nome, tipo):
        self.nome = nome
        self.tipo = tipo


class TabelaDeSimbolos:
    def __init__(self):
        self._simbolos = {}

    def definir(self, simbolo):
        self._simbolos[simbolo.nome] = simbolo

    def buscar(self, nome):
        return self._simbolos.get(nome)
