from pathlib import Path

from backend.nexus.lexer import Lexer
from backend.nexus.parser import Parser
from backend.nexus.semantic import SemanticAnalyzer

from backend.nexus.ir import TACGenerator
from backend.nexus.runtime import VirtualMachine


# Leer el programa NexusLang
file_path = Path(__file__).with_name("primer_programa.nx")
source = file_path.read_text(encoding="utf-8")


# FASE 1: Análisis léxico
tokens = Lexer(source).tokenize()


# FASE 2: Análisis sintáctico
program = Parser(tokens).parse()


# FASE 3: Análisis semántico
SemanticAnalyzer().analyze(program)


# FASE 4: Generación de código intermedio
generator = TACGenerator()
instructions = generator.generate(program)


# FASE 5: Ejecución en la máquina virtual
vm = VirtualMachine()
result = vm.execute(instructions)


# MOSTRAR RESULTADOS
print("\n========== NEXUS VIRTUAL MACHINE ==========\n")

print("INSTRUCCIONES TAC:")
print(generator.format_tac())


# RESULTADO DE EJECUCIÓN
print("\n========== RESULTADO DE EJECUCIÓN ==========\n")

for value in result.output:
    print(f"> {value}")


# VARIABLES
print("\n========== ESTADO DE VARIABLES ==========\n")

for name, value in result.variables.items():
    print(f"{name} = {value}")


# MEMORIA STACK
print("\n========== MEMORIA STACK ==========\n")

for frame in result.stack_snapshot:
    print(f"Marco: {frame['name']}")

    for name, value in frame["locals"].items():
        print(f"  {name} = {value}")


# MEMORIA HEAP
print("\n========== MEMORIA HEAP ==========\n")

if result.heap_snapshot:
    for address, value in result.heap_snapshot.items():
        print(f"Dirección {address} = {value}")
else:
    print("No hay memoria dinámica reservada.")


# FINALIZACIÓN
print("\n============================================")
print("Programa ejecutado correctamente.")
print(
    f"Instrucciones ejecutadas: "
    f"{result.instructions_executed}"
)