from dataclasses import dataclass
from typing import Optional, Union


Value = Union[int, float, str, bool]


@dataclass
class Program:
    statements: list


@dataclass
class VarDeclaration:
    var_type: str
    name: str
    initializer: Optional[object] = None


@dataclass
class Assignment:
    name: str
    value: object


@dataclass
class PrintStatement:
    expression: object


@dataclass
class BinaryExpression:
    left: object
    operator: str
    right: object


@dataclass
class UnaryExpression:
    operator: str
    operand: object


@dataclass
class Literal:
    value: Value
    literal_type: str


@dataclass
class Variable:
    name: str