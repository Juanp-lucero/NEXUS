import re

from .tokens import Token, TokenType


class LexicalError(Exception):
    """Error producido durante el análisis léxico."""


class Lexer:
    KEYWORDS = {
        "int",
        "float",
        "string",
        "bool",
        "if",
        "else",
        "while",
        "print",
        "true",
        "false",
    }

    TOKEN_PATTERN = re.compile(
        r"(?P<WHITESPACE>[ \t\r]+)|"
        r"(?P<NEWLINE>\n)|"
        r"(?P<COMMENT>//[^\n]*)|"
        r'(?P<FLOAT>\d+\.\d+)|'
        r"(?P<INTEGER>\d+)|"
        r'(?P<STRING>"(?:\\.|[^"\\])*")|'
        r"(?P<IDENTIFIER>[A-Za-z_][A-Za-z0-9_]*)|"
        r"(?P<EQUAL>==)|"
        r"(?P<NOT_EQUAL>!=)|"
        r"(?P<LESS_EQUAL><=)|"
        r"(?P<GREATER_EQUAL>>=)|"
        r"(?P<PLUS>\+)|"
        r"(?P<MINUS>-)|"
        r"(?P<MULTIPLY>\*)|"
        r"(?P<DIVIDE>/)|"
        r"(?P<ASSIGN>=)|"
        r"(?P<LESS_THAN><)|"
        r"(?P<GREATER_THAN>>)|"
        r"(?P<LPAREN>\()|"
        r"(?P<RPAREN>\))|"
        r"(?P<LBRACE>\{)|"
        r"(?P<RBRACE>\})|"
        r"(?P<SEMICOLON>;)|"
        r"(?P<COMMA>,)"
    )

    def __init__(self, source: str):
        self.source = source

    def tokenize(self) -> list[Token]:
        tokens = []

        position = 0
        line = 1
        column = 1

        while position < len(self.source):

            match = self.TOKEN_PATTERN.match(self.source, position)

            # Detectar caracteres que no reconoce el lenguaje
            if match is None:
                character = self.source[position]

                if character == '"':
                    raise LexicalError(
                        f"Cadena sin cerrar en línea {line}, "
                        f"columna {column}."
                    )

                raise LexicalError(
                    f"Carácter no reconocido {character!r} "
                    f"en línea {line}, columna {column}."
                )

            token_name = match.lastgroup
            lexeme = match.group()

            # Ignorar espacios
            if token_name == "WHITESPACE":
                column += len(lexeme)

            # Actualizar posición al encontrar un salto de línea
            elif token_name == "NEWLINE":
                line += 1
                column = 1

            # Ignorar comentarios
            elif token_name == "COMMENT":
                column += len(lexeme)

            else:
                # Identificar palabras reservadas
                if (
                    token_name == "IDENTIFIER"
                    and lexeme in self.KEYWORDS
                ):
                    token_type = TokenType.KEYWORD
                else:
                    token_type = TokenType[token_name]

                token = Token(
                    type=token_type,
                    lexeme=lexeme,
                    line=line,
                    column=column,
                )

                tokens.append(token)
                column += len(lexeme)

            position = match.end()

        # Agregar el token de fin de archivo
        tokens.append(
            Token(
                type=TokenType.EOF,
                lexeme="",
                line=line,
                column=column,
            )
        )

        return tokens