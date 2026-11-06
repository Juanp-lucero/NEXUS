import pytest

from backend.nexus.lexer import Lexer
from backend.nexus.parser import Parser
from backend.nexus.semantic import SemanticAnalyzer
from backend.nexus.ir import TACGenerator
from backend.nexus.runtime import VirtualMachine, ExecutionError


def generate_instructions(source):
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    SemanticAnalyzer().analyze(program)

    generator = TACGenerator()
    return generator.generate(program)


def execute_source(source):
    instructions = generate_instructions(source)

    vm = VirtualMachine()

    return vm.execute(instructions)


def test_executes_complete_program():

    source = """
    int numero1 = 10;
    int numero2 = 5;
    int resultado;

    resultado = numero1 + numero2 * 2;

    print(resultado);
    """

    result = execute_source(source)

    assert result.output == ["20"]
    assert result.variables["resultado"] == 20


def test_executes_string_print():

    result = execute_source(
        'print("Hola desde NEXUS");'
    )

    assert result.output == ["Hola desde NEXUS"]


def test_executes_float_division():

    source = """
    float resultado = 5 / 2;
    print(resultado);
    """

    result = execute_source(source)

    assert result.output == ["2.5"]
    assert result.variables["resultado"] == 2.5


def test_executes_negative_numbers():

    source = """
    int numero = -10;
    print(numero);
    """

    result = execute_source(source)

    assert result.output == ["-10"]


def test_executes_comparisons():

    source = """
    bool resultado = 10 > 5;
    print(resultado);
    """

    result = execute_source(source)

    assert result.output == ["true"]
    assert result.variables["resultado"] is True


def test_detects_division_by_zero():

    source = """
    float resultado = 10 / 0;
    print(resultado);
    """

    with pytest.raises(
        ExecutionError,
        match="Instrucción 2"
    ):
        execute_source(source)


def test_resets_machine_state_between_executions():

    vm = VirtualMachine()

    instructions1 = generate_instructions(
        "int numero = 10; print(numero);"
    )

    result1 = vm.execute(instructions1)

    instructions2 = generate_instructions(
        "int otro = 20; print(otro);"
    )

    result2 = vm.execute(instructions2)

    assert result1.output == ["10"]
    assert result2.output == ["20"]

    assert "numero" not in result2.variables
    assert "otro" in result2.variables


def test_counts_executed_instructions():

    source = """
    int numero = 10;
    print(numero);
    """

    result = execute_source(source)

    assert result.instructions_executed == 3