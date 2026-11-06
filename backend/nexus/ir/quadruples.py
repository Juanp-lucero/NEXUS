from dataclasses import dataclass

from .tac_generator import IRInstruction


@dataclass
class Quadruple:
    index: int
    operator: str
    arg1: str
    arg2: str
    result: str

    def to_row(self) -> tuple:
        return (
            self.index,
            self.operator,
            self.arg1,
            self.arg2,
            self.result
        )


def operand_to_string(operand) -> str:
    if operand is None:
        return "-"

    return operand.display()


def convert_to_quadruples(
    instructions: list[IRInstruction]
) -> list[Quadruple]:
    """Convertir instrucciones IR en una lista de cuádruplos."""

    quadruples = []

    for index, instruction in enumerate(instructions, start=1):

        operator = instruction.operator

        if operator == "DECLARE":
            arg1 = str(instruction.arg1.value)
            arg2 = "-"
            result = operand_to_string(instruction.result)

        elif operator == "PRINT":
            arg1 = operand_to_string(instruction.arg1)
            arg2 = "-"
            result = "-"

        elif operator == "NEG":
            arg1 = operand_to_string(instruction.arg1)
            arg2 = "UNARY"
            result = operand_to_string(instruction.result)

        else:
            arg1 = operand_to_string(instruction.arg1)
            arg2 = operand_to_string(instruction.arg2)
            result = operand_to_string(instruction.result)

        quadruple = Quadruple(
            index=index,
            operator=operator,
            arg1=arg1,
            arg2=arg2,
            result=result
        )

        quadruples.append(quadruple)

    return quadruples


def format_quadruples(
    quadruples: list[Quadruple]
) -> str:

    headers = (
        f"{'N.º':<5}"
        f"{'Operador':<12}"
        f"{'Argumento 1':<20}"
        f"{'Argumento 2':<20}"
        f"{'Resultado':<15}"
    )

    separator = "-" * len(headers)

    rows = []

    for quadruple in quadruples:
        rows.append(
            f"{quadruple.index:<5}"
            f"{quadruple.operator:<12}"
            f"{quadruple.arg1:<20}"
            f"{quadruple.arg2:<20}"
            f"{quadruple.result:<15}"
        )

    return "\n".join(
        [headers, separator] + rows
    )