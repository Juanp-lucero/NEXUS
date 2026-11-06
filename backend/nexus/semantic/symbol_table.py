from dataclasses import dataclass


class SymbolError(Exception):
    """Error relacionado con la tabla de símbolos."""


@dataclass
class Symbol:
    name: str
    data_type: str
    scope_level: int
    initialized: bool = False


class SymbolTable:

    def __init__(self):
        # El primer ámbito siempre es el ámbito global.
        self.scopes: list[dict[str, Symbol]] = [{}]

    @property
    def current_scope_level(self) -> int:
        return len(self.scopes) - 1

    def define(
        self,
        name: str,
        data_type: str,
        initialized: bool = False
    ) -> Symbol:

        current_scope = self.scopes[-1]

        if name in current_scope:
            raise SymbolError(
                f"La variable '{name}' ya fue declarada "
                f"en el ámbito actual."
            )

        symbol = Symbol(
            name=name,
            data_type=data_type,
            scope_level=self.current_scope_level,
            initialized=initialized
        )

        current_scope[name] = symbol

        return symbol

    def lookup(self, name: str) -> Symbol | None:
        # Buscar desde el ámbito más interno hasta el global.
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

        return None

    def enter_scope(self) -> None:
        """Crear un nuevo ámbito."""
        self.scopes.append({})

    def exit_scope(self) -> None:
        """Salir del ámbito actual."""
        if len(self.scopes) == 1:
            raise SymbolError(
                "No se puede eliminar el ámbito global."
            )

        self.scopes.pop()

    def get_all_symbols(self) -> list[Symbol]:
        """Obtener los símbolos de los ámbitos activos."""
        symbols = []

        for scope in self.scopes:
            symbols.extend(scope.values())

        return symbols