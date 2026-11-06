import pytest

from backend.nexus.lexer import Lexer, LexicalError, TokenType


def test_recognizes_keywords_and_identifiers():
    lexer = Lexer("int edad = 20;")
    tokens = lexer.tokenize()

    assert tokens[0].type == TokenType.KEYWORD
    assert tokens[0].lexeme == "int"

    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].lexeme == "edad"

    assert tokens[2].type == TokenType.ASSIGN
    assert tokens[3].type == TokenType.INTEGER
    assert tokens[4].type == TokenType.SEMICOLON
    assert tokens[5].type == TokenType.EOF


def test_recognizes_decimal_numbers():
    lexer = Lexer("float precio = 15.5;")
    tokens = lexer.tokenize()

    assert tokens[3].type == TokenType.FLOAT
    assert tokens[3].lexeme == "15.5"


def test_recognizes_arithmetic_operators():
    lexer = Lexer("10 + 5 * 2")
    tokens = lexer.tokenize()

    assert tokens[1].type == TokenType.PLUS
    assert tokens[3].type == TokenType.MULTIPLY


def test_ignores_comments():
    lexer = Lexer("int x = 5; // comentario")
    tokens = lexer.tokenize()

    lexemes = [token.lexeme for token in tokens]

    assert "// comentario" not in lexemes
    assert "int" in lexemes
    assert "x" in lexemes


def test_detects_invalid_characters():
    lexer = Lexer("int x = 5;\n@")

    with pytest.raises(LexicalError, match="Carácter no reconocido"):
        lexer.tokenize()


def test_recognizes_strings():
    lexer = Lexer('print("Hola mundo");')
    tokens = lexer.tokenize()

    assert tokens[2].type == TokenType.STRING
    assert tokens[2].lexeme == '"Hola mundo"'