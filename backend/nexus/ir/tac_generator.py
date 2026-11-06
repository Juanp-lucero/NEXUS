from dataclasses import dataclass
from typing import Optional

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


class IRGenerationError(Exception):
    """Error durante la generación de código intermedio."""


@dataclass(frozen=True)
class Operand:
    kind: str
    value: object

    def display(self) -> str:
        if self.kind == "constant":
            if isinstance(self.value, bool):
                return str(self.value).lower()

            if isinstance(self.value, str):
                return repr(self.value)

        return str(self.value)


@dataclass
class IRInstruction:
    operator: str
    arg1: Optional[Operand] = None
    arg2: Optional[Operand] = None
    result: Optional[Operand] = None

    def to_tac(self) -> str:

        if self.operator == "DECLARE":
            return (
                f"DECLARE {self.arg1.value} "
                f"{self.result.display()}"
            )

        if self.operator == "=":
            return f"{self.result.display()} = {self.arg1.display()}"

        if self.operator == "PRINT":
            return f"PRINT({self.arg1.display()})"

        if self.operator == "NEG":
            return (
                f"{self.result.display()} = "
                f"-{self.arg1.display()}"
            )

        return (
            f"{self.result.display()} = "
            f"{self.arg1.display()} "
            f"{self.operator} "
            f"{self.arg2.display()}"
        )


class TACGenerator:

    def __init__(self):
        self.instructions: list[IRInstruction] = []
        self.temp_counter = 0

    def generate(self, program: Program) -> list[IRInstruction]:
        """Convertir un AST en instrucciones de tres direcciones."""

        self.instructions = []
        self.temp_counter = 0

        for statement in program.statements:
            self.generate_statement(statement)

        return self.instructions

    def new_temp(self) -> Operand:
        """Crear un temporal automáticamente."""

        self.temp_counter += 1

        return Operand(
            kind="temporary",
            value=f"t{self.temp_counter}"
        )

    def emit(
        self,
        operator: str,
        arg1: Optional[Operand] = None,
        arg2: Optional[Operand] = None,
        result: Optional[Operand] = None,
    ) -> None:

        instruction = IRInstruction(
            operator=operator,
            arg1=arg1,
            arg2=arg2,
            result=result
        )

        self.instructions.append(instruction)

    def generate_statement(self, statement) -> None:

        # Declaración de variables
        if isinstance(statement, VarDeclaration):

            variable = Operand("variable", statement.name)
            data_type = Operand("type", statement.var_type)

            self.emit(
                operator="DECLARE",
                arg1=data_type,
                result=variable
            )

            if statement.initializer is not None:

                value = self.generate_expression(
                    statement.initializer
                )

                self.emit(
                    operator="=",
                    arg1=value,
                    result=variable
                )

        # Asignación
        elif isinstance(statement, Assignment):

            value = self.generate_expression(statement.value)

            variable = Operand(
                "variable",
                statement.name
            )

            self.emit(
                operator="=",
                arg1=value,
                result=variable
            )

        # Impresión
        elif isinstance(statement, PrintStatement):

            value = self.generate_expression(
                statement.expression
            )

            self.emit(
                operator="PRINT",
                arg1=value
            )

        else:
            raise IRGenerationError(
                f"Sentencia no soportada: "
                f"{type(statement).__name__}."
            )

    def generate_expression(self, expression) -> Operand:

        # Valores constantes
        if isinstance(expression, Literal):

            return Operand(
                kind="constant",
                value=expression.value
            )

        # Variables
        if isinstance(expression, Variable):

            return Operand(
                kind="variable",
                value=expression.name
            )

        # Operaciones binarias
        if isinstance(expression, BinaryExpression):

            left = self.generate_expression(expression.left)
            right = self.generate_expression(expression.right)

            temporary = self.new_temp()

            self.emit(
                operator=expression.operator,
                arg1=left,
                arg2=right,
                result=temporary
            )

            return temporary

        # Operaciones unarias
        if isinstance(expression, UnaryExpression):

            operand = self.generate_expression(
                expression.operand
            )

            temporary = self.new_temp()

            self.emit(
                operator="NEG",
                arg1=operand,
                result=temporary
            )

            return temporary

        raise IRGenerationError(
            f"Expresión no soportada: "
            f"{type(expression).__name__}."
        )

    def format_tac(self) -> str:

        return "\n".join(
            f"{index + 1}. {instruction.to_tac()}"
            for index, instruction in enumerate(
                self.instructions
            )
        )