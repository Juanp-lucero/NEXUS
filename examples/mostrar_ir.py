from pathlib import Path

from backend.nexus.lexer import Lexer
from backend.nexus.parser import Parser
from backend.nexus.semantic import SemanticAnalyzer

from backend.nexus.ir import (
    TACGenerator,
    convert_to_quadruples,
    format_quadruples,
)


# Leer nuestro programa de ejemplo
file_path = Path(__file__).with_name("primer_programa.nx")
source = file_path.read_text(encoding="utf-8")

# Fase 1: análisis léxico
tokens = Lexer(source).tokenize()

# Fase 2: análisis sintáctico
program = Parser(tokens).parse()

# Fase 3: análisis semántico
SemanticAnalyzer().analyze(program)

# Fase 4: generación de código intermedio
generator = TACGenerator()
instructions = generator.generate(program)

print("\n========== CÓDIGO TAC ==========\n")
print(generator.format_tac())

# Convertir a cuádruplos
quadruples = convert_to_quadruples(instructions)

print("\n========== CUÁDRUPLOS ==========\n")
print(format_quadruples(quadruples))