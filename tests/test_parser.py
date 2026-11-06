import pytest

from backend.nexus.lexer import Lexer
from backend.nexus.parser import Parser, ParseError

from backend.nexus.ast.nodes import (
    Program,
    VarDeclaration,
    Assignment,
    PrintStatement,
    BinaryExpression,
    Literal,
    Variable,
)


def parse_source(source):
    tokens = Lexer(source).tokenize()
    parser = Parser(tokens)
    return parser.parse()


def test_parses_variable_declaration():

    program = parse_source("int edad = 20;")

    assert isinstance(program, Program)
    assert len(program.statements) == 1

    declaration = program.statements[0]

    assert isinstance(declaration, VarDeclaration)
    assert declaration.var_type == "int"
    assert declaration.name == "edad"
    assert declaration.initializer.value == 20


def test_parses_assignment():

    program = parse_source("resultado = 15;")

    assignment = program.statements[0]

    assert isinstance(assignment, Assignment)
    assert assignment.name == "resultado"
    assert assignment.value.value == 15


def test_respects_operator_precedence():

    program = parse_source(
        "int resultado = 10 + 5 * 2;"
    )

    expression = program.statements[0].initializer

    assert isinstance(expression, BinaryExpression)
    assert expression.operator == "+"

    assert isinstance(expression.right, BinaryExpression)
    assert expression.right.operator == "*"


def test_parses_print_statement():

    program = parse_source('print("Hola mundo");')

    statement = program.statements[0]

    assert isinstance(statement, PrintStatement)
    assert isinstance(statement.expression, Literal)
    assert statement.expression.value == "Hola mundo"


def test_parses_variable_expression():

    program = parse_source("resultado = numero1 + 5;")

    expression = program.statements[0].value

    assert isinstance(expression, BinaryExpression)
    assert isinstance(expression.left, Variable)
    assert expression.left.name == "numero1"


def test_detects_missing_semicolon():

    with pytest.raises(ParseError):
        parse_source("int edad = 20")


def test_parses_complete_program():

    source = """
    int numero1 = 10;
    int numero2 = 5;
    int resultado;
    resultado = numero1 + numero2 * 2;
    print(resultado);
    """

    program = parse_source(source)

    assert len(program.statements) == 5
    assert isinstance(program.statements[0], VarDeclaration)
    assert isinstance(program.statements[3], Assignment)
    assert isinstance(program.statements[4], PrintStatement)