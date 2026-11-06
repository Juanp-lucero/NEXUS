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

from .symbol_table import SymbolTable, SymbolError


class SemanticError(Exception):
    """Error producido durante el análisis semántico."""


class SemanticAnalyzer:

    VALID_TYPES = {"int", "float", "string", "bool"}
    NUMERIC_TYPES = {"int", "float"}

    def __init__(self):
        self.symbol_table = SymbolTable()

    def analyze(self, program: Program) -> SymbolTable:
        """Analizar todas las sentencias del programa."""

        for statement in program.statements:
            self.analyze_statement(statement)

        return self.symbol_table

    def analyze_statement(self, statement):

        # Declaración de variables
        if isinstance(statement, VarDeclaration):

            if statement.var_type not in self.VALID_TYPES:
                raise SemanticError(
                    f"Tipo de dato no válido: "
                    f"'{statement.var_type}'."
                )

            initialized = statement.initializer is not None

            if initialized:
                expression_type = self.infer_expression(
                    statement.initializer
                )

                self.check_compatibility(
                    statement.var_type,
                    expression_type,
                    statement.name
                )

            try:
                self.symbol_table.define(
                    name=statement.name,
                    data_type=statement.var_type,
                    initialized=initialized
                )

            except SymbolError as error:
                raise SemanticError(str(error)) from error

        # Asignación de variables
        elif isinstance(statement, Assignment):

            symbol = self.symbol_table.lookup(statement.name)

            if symbol is None:
                raise SemanticError(
                    f"La variable '{statement.name}' "
                    f"no ha sido declarada."
                )

            expression_type = self.infer_expression(
                statement.value
            )

            self.check_compatibility(
                symbol.data_type,
                expression_type,
                statement.name
            )

            symbol.initialized = True

        # Instrucción print
        elif isinstance(statement, PrintStatement):

            self.infer_expression(statement.expression)

        else:
            raise SemanticError(
                f"Tipo de sentencia no soportado: "
                f"{type(statement).__name__}."
            )

    def infer_expression(self, expression) -> str:
        """Determinar el tipo de una expresión."""

        # Valores constantes
        if isinstance(expression, Literal):
            return expression.literal_type

        # Uso de variables
        if isinstance(expression, Variable):

            symbol = self.symbol_table.lookup(expression.name)

            if symbol is None:
                raise SemanticError(
                    f"La variable '{expression.name}' "
                    f"no ha sido declarada."
                )

            if not symbol.initialized:
                raise SemanticError(
                    f"La variable '{expression.name}' "
                    f"se utiliza sin haber sido inicializada."
                )

            return symbol.data_type

        # Operaciones unarias, por ejemplo -numero
        if isinstance(expression, UnaryExpression):

            operand_type = self.infer_expression(
                expression.operand
            )

            if operand_type not in self.NUMERIC_TYPES:
                raise SemanticError(
                    "El operador unario '-' "
                    "solo admite valores numéricos."
                )

            return operand_type

        # Operaciones binarias
        if isinstance(expression, BinaryExpression):

            left_type = self.infer_expression(expression.left)
            right_type = self.infer_expression(expression.right)

            return self.check_binary_operation(
                expression.operator,
                left_type,
                right_type
            )

        raise SemanticError(
            f"Expresión no soportada: "
            f"{type(expression).__name__}."
        )

    def check_binary_operation(
        self,
        operator: str,
        left_type: str,
        right_type: str
    ) -> str:

        # Operaciones aritméticas
        if operator in {"+", "-", "*", "/"}:

            if (
                left_type not in self.NUMERIC_TYPES
                or right_type not in self.NUMERIC_TYPES
            ):
                raise SemanticError(
                    f"El operador '{operator}' "
                    f"requiere valores numéricos. "
                    f"Se recibieron '{left_type}' y "
                    f"'{right_type}'."
                )

            # La división produce un resultado decimal.
            if operator == "/":
                return "float"

            if (
                left_type == "float"
                or right_type == "float"
            ):
                return "float"

            return "int"

        # Operadores de comparación
        if operator in {"<", "<=", ">", ">="}:

            if (
                left_type not in self.NUMERIC_TYPES
                or right_type not in self.NUMERIC_TYPES
            ):
                raise SemanticError(
                    f"El operador '{operator}' "
                    "requiere valores numéricos."
                )

            return "bool"

        # Operadores de igualdad
        if operator in {"==", "!="}:

            both_numeric = (
                left_type in self.NUMERIC_TYPES
                and right_type in self.NUMERIC_TYPES
            )

            same_type = left_type == right_type

            if not both_numeric and not same_type:
                raise SemanticError(
                    f"No se pueden comparar valores "
                    f"de tipo '{left_type}' y '{right_type}'."
                )

            return "bool"

        raise SemanticError(
            f"Operador no soportado: '{operator}'."
        )

    def check_compatibility(
        self,
        expected_type: str,
        actual_type: str,
        variable_name: str
    ) -> None:

        # Se permite convertir int a float.
        compatible = (
            expected_type == actual_type
            or (
                expected_type == "float"
                and actual_type == "int"
            )
        )

        if not compatible:
            raise SemanticError(
                f"Asignación incompatible para '{variable_name}': "
                f"se esperaba '{expected_type}', "
                f"pero se recibió '{actual_type}'."
            )