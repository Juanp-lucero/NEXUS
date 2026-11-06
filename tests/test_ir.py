import pytest

from backend.nexus.lexer import Lexer
from backend.nexus.parser import Parser
from backend.nexus.semantic import SemanticAnalyzer
from backend.nexus.ir import (
    TACGenerator,
    IRGenerationError,
    convert_to_quadruples,
    format_quadruples,
)


def compile_to_ir(source):

    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    # Comprobar primero que el programa tenga sentido.
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)

    # Generar las instrucciones intermedias.
    generator = TACGenerator()
    instructions = generator.generate(program)

    return generator, instructions


def test_generates_arithmetic_instructions():

    source = """
    int numero1 = 10;
    int numero2 = 5;
    int resultado;
    resultado = numero1 + numero2 * 2;
    """

    generator, instructions = compile_to_ir(source)

    operators = [
        instruction.operator
        for instruction in instructions
    ]

    assert operators == [
        "DECLARE",
        "=",
        "DECLARE",
        "=",
        "DECLARE",
        "*",
        "+",
        "=",
    ]

    assert instructions[5].to_tac() == "t1 = numero2 * 2"
    assert instructions[6].to_tac() == "t2 = numero1 + t1"
    assert instructions[7].to_tac() == "resultado = t2"


def test_generates_print_instruction():

    generator, instructions = compile_to_ir(
        "int numero = 10; print(numero);"
    )

    assert instructions[-1].operator == "PRINT"
    assert instructions[-1].to_tac() == "PRINT(numero)"


def test_generates_negative_number():

    generator, instructions = compile_to_ir(
        "int numero = -5;"
    )

    assert any(
        instruction.operator == "NEG"
        for instruction in instructions
    )

    assert any(
        instruction.to_tac() == "t1 = -5"
        for instruction in instructions
    )


def test_generates_comparison_instruction():

    generator, instructions = compile_to_ir(
        "bool resultado = 10 > 5;"
    )

    comparison = next(
        instruction
        for instruction in instructions
        if instruction.operator == ">"
    )

    assert comparison.to_tac() == "t1 = 10 > 5"


def test_generates_declaration_without_initializer():

    generator, instructions = compile_to_ir(
        "int resultado;"
    )

    assert len(instructions) == 1
    assert instructions[0].to_tac() == "DECLARE int resultado"


def test_converts_instructions_to_quadruples():

    generator, instructions = compile_to_ir(
        "int resultado = 10 + 5;"
    )

    quadruples = convert_to_quadruples(instructions)

    addition = next(
        quadruple
        for quadruple in quadruples
        if quadruple.operator == "+"
    )

    assert addition.arg1 == "10"
    assert addition.arg2 == "5"
    assert addition.result == "t1"


def test_formats_quadruple_table():

    generator, instructions = compile_to_ir(
        "int resultado = 10 + 5;"
    )

    quadruples = convert_to_quadruples(instructions)
    output = format_quadruples(quadruples)

    assert "Operador" in output
    assert "Argumento 1" in output
    assert "Resultado" in output
    assert "+" in output


def test_temporary_counter_resets():

    generator, instructions = compile_to_ir(
        "int resultado = 10 + 5;"
    )

    assert any(
        instruction.result is not None
        and instruction.result.value == "t1"
        for instruction in instructions
    )

    # Generar otro programa con el mismo generador.
    tokens = Lexer("int otro = 20 + 3;").tokenize()
    program = Parser(tokens).parse()

    SemanticAnalyzer().analyze(program)

    new_instructions = generator.generate(program)

    assert any(
        instruction.result is not None
        and instruction.result.value == "t1"
        for instruction in new_instructions
    )