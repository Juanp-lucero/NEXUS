import pytest

from backend.nexus.lexer import Lexer
from backend.nexus.parser import Parser
from backend.nexus.semantic import (
    SemanticAnalyzer,
    SemanticError,
    SymbolTable,
    SymbolError,
)


def analyze_source(source):
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


def test_valid_program():
    source = """
    int numero = 10;
    float precio = 2.5;
    float total = numero + precio;
    print(total);
    """

    table = analyze_source(source)

    assert table.lookup("numero").data_type == "int"
    assert table.lookup("precio").data_type == "float"
    assert table.lookup("total").data_type == "float"


def test_detects_undeclared_variable():
    source = "resultado = 100;"

    with pytest.raises(
        SemanticError,
        match="no ha sido declarada"
    ):
        analyze_source(source)


def test_detects_duplicate_declaration():
    source = """
    int edad = 20;
    int edad = 30;
    """

    with pytest.raises(
        SemanticError,
        match="ya fue declarada"
    ):
        analyze_source(source)


def test_detects_incompatible_declaration():
    source = 'int numero = "hola";'

    with pytest.raises(
        SemanticError,
        match="Asignación incompatible"
    ):
        analyze_source(source)


def test_detects_incompatible_assignment():
    source = """
    int numero = 10;
    numero = 3.5;
    """

    with pytest.raises(
        SemanticError,
        match="Asignación incompatible"
    ):
        analyze_source(source)


def test_detects_uninitialized_variable():
    source = """
    int resultado;
    print(resultado);
    """

    with pytest.raises(
        SemanticError,
        match="sin haber sido inicializada"
    ):
        analyze_source(source)


def test_allows_integer_to_float_conversion():
    source = """
    int numero = 10;
    float resultado = numero;
    """

    table = analyze_source(source)

    assert table.lookup("resultado").data_type == "float"
    assert table.lookup("resultado").initialized is True


def test_comparison_returns_boolean_type():
    source = """
    bool resultado = 10 > 5;
    """

    table = analyze_source(source)

    assert table.lookup("resultado").data_type == "bool"


def test_symbol_table_supports_nested_scopes():
    table = SymbolTable()

    table.define("valor", "int")

    table.enter_scope()
    table.define("valor", "float")

    assert table.lookup("valor").data_type == "float"

    table.exit_scope()

    assert table.lookup("valor").data_type == "int"


def test_cannot_remove_global_scope():
    table = SymbolTable()

    with pytest.raises(SymbolError):
        table.exit_scope()