from ..lexer import Token, TokenType
from ..ast.nodes import (
    Program,
    VarDeclaration,
    Assignment,
    PrintStatement,
    BinaryExpression,
    UnaryExpression,
    Literal,
    Variable,
)


class ParseError(Exception):
    """Error producido durante el análisis sintáctico."""


class Parser:

    TYPES = {"int", "float", "string", "bool"}

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    def current(self) -> Token:
        return self.tokens[self.position]

    def previous(self) -> Token:
        return self.tokens[self.position - 1]

    def advance(self) -> Token:
        token = self.current()

        if token.type != TokenType.EOF:
            self.position += 1

        return token

    def check(self, token_type: TokenType) -> bool:
        return self.current().type == token_type

    def match(self, *token_types: TokenType) -> bool:
        if self.current().type in token_types:
            self.advance()
            return True

        return False

    def match_keyword(self, keyword: str) -> bool:
        token = self.current()

        if (
            token.type == TokenType.KEYWORD
            and token.lexeme == keyword
        ):
            self.advance()
            return True

        return False

    def consume(
        self,
        token_type: TokenType,
        message: str
    ) -> Token:

        if self.check(token_type):
            return self.advance()

        token = self.current()

        raise ParseError(
            f"{message} Línea {token.line}, "
            f"columna {token.column}. "
            f"Se encontró {token.lexeme!r}."
        )

    # PROGRAMA Y SENTENCIAS

    def parse(self) -> Program:
        statements = []

        while not self.check(TokenType.EOF):
            statements.append(self.parse_statement())

        return Program(statements)

    def parse_statement(self):

        token = self.current()

        if token.type == TokenType.KEYWORD:

            if token.lexeme in self.TYPES:
                return self.parse_declaration()

            if token.lexeme == "print":
                return self.parse_print()

            raise ParseError(
                f"Sentencia no implementada: {token.lexeme}. "
                f"Línea {token.line}, columna {token.column}."
            )

        if token.type == TokenType.IDENTIFIER:
            return self.parse_assignment()

        raise ParseError(
            f"Sentencia no válida en línea {token.line}, "
            f"columna {token.column}: {token.lexeme!r}."
        )

    # DECLARACIONES

    def parse_declaration(self) -> VarDeclaration:

        var_type = self.advance().lexeme

        name = self.consume(
            TokenType.IDENTIFIER,
            "Se esperaba el nombre de la variable."
        )

        initializer = None

        if self.match(TokenType.ASSIGN):
            initializer = self.parse_expression()

        self.consume(
            TokenType.SEMICOLON,
            "Se esperaba ';' al finalizar la declaración."
        )

        return VarDeclaration(
            var_type=var_type,
            name=name.lexeme,
            initializer=initializer
        )

    # ASIGNACIONES

    def parse_assignment(self) -> Assignment:

        name = self.consume(
            TokenType.IDENTIFIER,
            "Se esperaba una variable."
        )

        self.consume(
            TokenType.ASSIGN,
            "Se esperaba '=' en la asignación."
        )

        value = self.parse_expression()

        self.consume(
            TokenType.SEMICOLON,
            "Se esperaba ';' al finalizar la asignación."
        )

        return Assignment(
            name=name.lexeme,
            value=value
        )

    # IMPRESIÓN

    def parse_print(self) -> PrintStatement:

        self.advance()  # Consumir print

        self.consume(
            TokenType.LPAREN,
            "Se esperaba '(' después de print."
        )

        expression = self.parse_expression()

        self.consume(
            TokenType.RPAREN,
            "Se esperaba ')' después de la expresión."
        )

        self.consume(
            TokenType.SEMICOLON,
            "Se esperaba ';' después de print."
        )

        return PrintStatement(expression)

    # EXPRESIONES

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):

        expression = self.parse_comparison()

        while self.match(
            TokenType.EQUAL,
            TokenType.NOT_EQUAL
        ):
            operator = self.previous().lexeme
            right = self.parse_comparison()

            expression = BinaryExpression(
                expression,
                operator,
                right
            )

        return expression

    def parse_comparison(self):

        expression = self.parse_term()

        while self.match(
            TokenType.LESS_THAN,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_THAN,
            TokenType.GREATER_EQUAL
        ):
            operator = self.previous().lexeme
            right = self.parse_term()

            expression = BinaryExpression(
                expression,
                operator,
                right
            )

        return expression

    def parse_term(self):

        expression = self.parse_factor()

        while self.match(
            TokenType.PLUS,
            TokenType.MINUS
        ):
            operator = self.previous().lexeme
            right = self.parse_factor()

            expression = BinaryExpression(
                expression,
                operator,
                right
            )

        return expression

    def parse_factor(self):

        expression = self.parse_unary()

        while self.match(
            TokenType.MULTIPLY,
            TokenType.DIVIDE
        ):
            operator = self.previous().lexeme
            right = self.parse_unary()

            expression = BinaryExpression(
                expression,
                operator,
                right
            )

        return expression

    def parse_unary(self):

        if self.match(TokenType.MINUS):
            operator = self.previous().lexeme
            operand = self.parse_unary()

            return UnaryExpression(
                operator,
                operand
            )

        return self.parse_primary()

    # VALORES PRIMARIOS

    def parse_primary(self):

        if self.match(TokenType.INTEGER):
            token = self.previous()

            return Literal(
                int(token.lexeme),
                "int"
            )

        if self.match(TokenType.FLOAT):
            token = self.previous()

            return Literal(
                float(token.lexeme),
                "float"
            )

        if self.match(TokenType.STRING):
            token = self.previous()

            return Literal(
                token.lexeme[1:-1],
                "string"
            )

        if self.match_keyword("true"):
            return Literal(True, "bool")

        if self.match_keyword("false"):
            return Literal(False, "bool")

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous().lexeme)

        if self.match(TokenType.LPAREN):

            expression = self.parse_expression()

            self.consume(
                TokenType.RPAREN,
                "Se esperaba ')' para cerrar la expresión."
            )

            return expression

        token = self.current()

        raise ParseError(
            f"Expresión no válida en línea {token.line}, "
            f"columna {token.column}."
        )