from dataclasses import dataclass

from ..ir.tac_generator import IRInstruction
from ..memory.memory_manager import (
    MemoryManager,
    MemoryManagerError,
)


class ExecutionError(Exception):
    """Error producido durante la ejecución del programa."""


@dataclass
class ExecutionResult:
    output: list[str]
    variables: dict
    temporaries: dict
    instructions_executed: int
    stack_snapshot: list[dict]
    heap_snapshot: dict


class VirtualMachine:

    def __init__(self):
        self.memory = MemoryManager()
        self.variable_types = {}
        self.temporaries = {}
        self.output = []

    def execute(
        self,
        instructions: list[IRInstruction]
    ) -> ExecutionResult:

        self.memory.reset()
        self.memory.push_stack_frame("main")

        self.variable_types = {}
        self.temporaries = {}
        self.output = []

        try:
            for index, instruction in enumerate(instructions):

                try:
                    self.execute_instruction(instruction)

                except (
                    ExecutionError,
                    MemoryManagerError,
                    ZeroDivisionError,
                    TypeError
                ) as error:

                    raise ExecutionError(
                        f"Instrucción {index + 1}: {error}"
                    ) from error

            snapshot = self.memory.snapshot()

            return ExecutionResult(
                output=self.output.copy(),
                variables=snapshot["stack"][-1]["locals"].copy(),
                temporaries=self.temporaries.copy(),
                instructions_executed=len(instructions),
                stack_snapshot=snapshot["stack"],
                heap_snapshot=snapshot["heap"]
            )

        finally:
            # Liberar el marco de ejecución principal.
            if self.memory.stack:
                self.memory.pop_stack_frame()

    def resolve_operand(self, operand):

        if operand is None:
            raise ExecutionError(
                "Se recibió un operando vacío."
            )

        if operand.kind == "constant":
            return operand.value

        if operand.kind == "variable":

            value = self.memory.obtener_local(operand.value)

            if value is None:
                raise ExecutionError(
                    f"Variable '{operand.value}' sin inicializar."
                )

            return value

        if operand.kind == "temporary":

            if operand.value not in self.temporaries:
                raise ExecutionError(
                    f"Temporal '{operand.value}' no encontrado."
                )

            return self.temporaries[operand.value]

        raise ExecutionError(
            f"Tipo de operando no reconocido: '{operand.kind}'."
        )

    def assign_value(self, destination, value):

        if destination is None:
            raise ExecutionError(
                "No se indicó dónde almacenar el resultado."
            )

        if destination.kind == "variable":

            name = destination.value

            if not self.memory.contiene_local(name):
                raise ExecutionError(
                    f"Variable '{name}' no declarada."
                )

            self.memory.actualizar_local(name, value)

        elif destination.kind == "temporary":

            self.temporaries[destination.value] = value

        else:
            raise ExecutionError(
                f"Destino no válido: '{destination.kind}'."
            )

    def execute_instruction(self, instruction):

        operator = instruction.operator

        # Declaración de variables en Stack.
        if operator == "DECLARE":

            name = instruction.result.value
            data_type = instruction.arg1.value

            try:
                self.memory.declarar_local(name)

            except MemoryManagerError as error:
                raise ExecutionError(str(error)) from error

            self.variable_types[name] = data_type

        # Asignaciones.
        elif operator == "=":

            value = self.resolve_operand(instruction.arg1)

            self.assign_value(
                instruction.result,
                value
            )

        # Impresión.
        elif operator == "PRINT":

            value = self.resolve_operand(instruction.arg1)

            self.output.append(
                self.format_value(value)
            )

        # Negación.
        elif operator == "NEG":

            value = self.resolve_operand(instruction.arg1)

            self.assign_value(
                instruction.result,
                -value
            )

        # Operaciones aritméticas y comparaciones.
        else:

            left = self.resolve_operand(instruction.arg1)
            right = self.resolve_operand(instruction.arg2)

            result = self.evaluate_operation(
                operator,
                left,
                right
            )

            self.assign_value(
                instruction.result,
                result
            )

    def evaluate_operation(self, operator, left, right):

        operations = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,

            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,

            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }

        if operator not in operations:
            raise ExecutionError(
                f"Operador no soportado: '{operator}'."
            )

        return operations[operator](left, right)

    def format_value(self, value):

        if isinstance(value, bool):
            return str(value).lower()

        return str(value)