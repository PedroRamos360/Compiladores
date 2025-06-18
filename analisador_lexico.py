import re


class Token:
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return (
            f"Token({self.tipo}, '{self.valor}', Linha {self.linha}, Col {self.coluna})"
        )


class AnalisadorLexico:
    def __init__(self, codigo_fonte):
        self.codigo_fonte = codigo_fonte
        self.posicao = 0
        self.linha = 1
        self.coluna = 1

        self.palavras_reservadas = {
            "programa": "PROGRAMA",
            "var": "VAR",
            "início": "INÍCIO",
            "fim": "FIM",
            "inteiro": "INTEIRO",
            "lógico": "LÓGICO",
            "ler": "LER",
            "escrever": "ESCREVER",
            "se": "SE",
            "então": "ENTÃO",
            "senão": "SENÃO",
            "enquanto": "ENQUANTO",
            "faça": "FAÇA",
        }

        self.especificacoes_tokens = [
            ("COMENTÁRIO", r"/\*.*?\*/"),
            ("ESPAÇO", r"[ \t]+"),
            ("NOVA_LINHA", r"\n"),
            ("STRING", r'"(?:\\.|[^"\\])*"'),
            ("ATRIBUIÇÃO", r":="),
            ("MENOR_IGUAL", r"<="),
            ("MAIOR_IGUAL", r">="),
            ("DIFERENTE", r"<>"),
            ("NÚMERO", r"\d+"),
            ("ID", r"[a-zA-Z_À-ú][a-zA-Z0-9_À-ú]*"),
            ("MAIS", r"\+"),
            ("MENOS", r"-"),
            ("MULT", r"\*"),
            ("DIV", r"/"),
            ("IGUAL", r"="),
            ("MENOR", r"<"),
            ("MAIOR", r">"),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("LCOLCH", r"\["),
            ("RCOLCH", r"\]"),
            ("PONTO_VÍRGULA", r";"),
            ("DOIS_PONTOS", r":"),
            ("PONTO", r"\."),
            ("VÍRGULA", r","),
            ("ERRO", r"."),
        ]

        regex_unidas = "|".join(
            f"(?P<{par[0]}>{par[1]})" for par in self.especificacoes_tokens
        )
        self.token_regex = re.compile(regex_unidas, re.DOTALL)

    def analisar(self) -> list[Token]:
        tokens = []
        while self.posicao < len(self.codigo_fonte):
            token = self._proximo_token()
            if token and token.tipo != "ESPAÇO" and token.tipo != "COMENTÁRIO":
                tokens.append(token)
        tokens.append(Token("EOF", "EOF", self.linha, self.coluna))
        return tokens

    def _proximo_token(self):
        match = self.token_regex.match(self.codigo_fonte, self.posicao)
        if not match:
            return None

        tipo = match.lastgroup
        valor = match.group()
        coluna_inicial = self.coluna

        if tipo in ["ESPACO", "COMENTARIO"]:
            self.posicao = match.end()
            self.coluna += len(valor)
            return self._proximo_token()

        if tipo == "NOVA_LINHA":
            self.posicao = match.end()
            self.linha += 1
            self.coluna = 1
            return self._proximo_token()

        if tipo == "ID" and valor.lower() in self.palavras_reservadas:
            tipo = self.palavras_reservadas[valor.lower()]

        if tipo == "ERRO":
            raise ValueError(
                f"Caractere não reconhecido '{valor}' na linha {self.linha}, coluna {coluna_inicial}"
            )

        token = Token(tipo, valor, self.linha, coluna_inicial)
        self.posicao = match.end()
        self.coluna += len(valor)
        return token
