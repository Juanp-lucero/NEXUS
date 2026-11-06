from dataclasses import fields, is_dataclass

from backend.nexus.lexer import Lexer
from backend.nexus.parser import Parser
from backend.nexus.semantic import SemanticAnalyzer
from backend.nexus.ir import (
    TACGenerator,
    convert_to_quadruples,
)
from backend.nexus.runtime import VirtualMachine


def serialize_ast(node):
    """
    Convertir los nodos del AST en estructuras
    compatibles con JSON.
    """

    if is_dataclass(node):
        return {
            "node": type(node).__name__,
            **{
                field.name: serialize_ast(
                    getattr(node, field.name)
                )
                for field in fields(node)
            }
        }

    if isinstance(node, list):
        return [serialize_ast(item) for item in node]

    if isinstance(node, tuple):
        return [serialize_ast(item) for item in node]

    if isinstance(node, dict):
        return {
            str(key): serialize_ast(value)
            for key, value in node.items()
        }

    return node


def compile_source(source: str) -> dict:
    """
    Ejecutar el proceso completo de compilación
    de un programa NexusLang.
    """

    # FASE 1: Análisis léxico
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    token_data = [
        {
            "type": token.type.name,
            "lexeme": token.lexeme,
            "line": token.line,
            "column": token.column
        }
        for token in tokens
    ]

    # FASE 2: Análisis sintáctico
    parser = Parser(tokens)
    program = parser.parse()

    ast_data = serialize_ast(program)

    # FASE 3: Análisis semántico
    analyzer = SemanticAnalyzer()
    symbol_table = analyzer.analyze(program)

    symbols_data = [
        {
            "name": symbol.name,
            "data_type": symbol.data_type,
            "scope_level": symbol.scope_level,
            "initialized": symbol.initialized
        }
        for symbol in symbol_table.get_all_symbols()
    ]

    # FASE 4: Generación de código intermedio
    generator = TACGenerator()
    instructions = generator.generate(program)

    tac_data = [
        {
            "index": index,
            "instruction": instruction.to_tac()
        }
        for index, instruction in enumerate(
            instructions,
            start=1
        )
    ]

    # Conversión a cuádruplos
    quadruples = convert_to_quadruples(instructions)

    quadruples_data = [
        {
            "index": quad.index,
            "operator": quad.operator,
            "arg1": quad.arg1,
            "arg2": quad.arg2,
            "result": quad.result
        }
        for quad in quadruples
    ]

    # FASE 5: Ejecución en la máquina virtual
    vm = VirtualMachine()
    execution = vm.execute(instructions)

    execution_data = {
        "output": execution.output,
        "variables": execution.variables,
        "temporaries": execution.temporaries,
        "instructions_executed": execution.instructions_executed,
        "stack": execution.stack_snapshot,
        "heap": execution.heap_snapshot
    }

    # RESPUESTA COMPLETA
    return {
        "success": True,
        "message": "Programa compilado y ejecutado correctamente.",

        "tokens": token_data,

        "ast": ast_data,

        "symbol_table": symbols_data,

        "tac": tac_data,

        "quadruples": quadruples_data,

        "execution": execution_data
    }