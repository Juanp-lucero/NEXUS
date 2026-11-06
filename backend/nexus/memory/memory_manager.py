from dataclasses import dataclass, field


class MemoryManagerError(Exception):
    """Error relacionado con la gestión de memoria."""


@dataclass
class StackFrame:
    name: str
    locals: dict[str, object] = field(default_factory=dict)


class MemoryManager:

    def __init__(self):
        self.stack: list[StackFrame] = []
        self.heap: dict[int, object] = {}
        self.next_address = 1000

    # STACK: MARCOS DE EJECUCIÓN

    def push_stack_frame(self, name: str = "main") -> None:
        """Crear un nuevo marco de pila."""

        self.stack.append(StackFrame(name=name))

    def pop_stack_frame(self) -> StackFrame:
        """Eliminar el marco de pila más reciente."""

        if not self.stack:
            raise MemoryManagerError(
                "No existen marcos en el Stack."
            )

        return self.stack.pop()

    def declarar_local(self, name: str) -> None:
        """Declarar una variable local sin inicializar."""

        if not self.stack:
            raise MemoryManagerError(
                "No existe un marco de pila activo."
            )

        current_frame = self.stack[-1]

        if name in current_frame.locals:
            raise MemoryManagerError(
                f"La variable '{name}' ya existe "
                "en este marco."
            )

        current_frame.locals[name] = None

    def asignar_local(self, name: str, value: object) -> None:
        """Asignar un valor a una variable del marco actual."""

        if not self.stack:
            raise MemoryManagerError(
                "No existe un marco de pila activo."
            )

        self.stack[-1].locals[name] = value

    def contiene_local(self, name: str) -> bool:
        """Comprobar si una variable existe en los marcos activos."""

        return any(
            name in frame.locals
            for frame in reversed(self.stack)
        )

    def obtener_local(self, name: str) -> object:
        """Buscar una variable desde el marco más reciente."""

        for frame in reversed(self.stack):
            if name in frame.locals:
                return frame.locals[name]

        raise MemoryManagerError(
            f"Variable '{name}' no encontrada en el Stack."
        )

    def actualizar_local(self, name: str, value: object) -> None:
        """Actualizar la variable donde fue declarada."""

        for frame in reversed(self.stack):
            if name in frame.locals:
                frame.locals[name] = value
                return

        raise MemoryManagerError(
            f"No se puede actualizar '{name}': "
            "variable no encontrada."
        )

    # HEAP: MEMORIA DINÁMICA

    def reservar_heap(self, value: object = None) -> int:
        """Reservar una posición en el Heap."""

        address = self.next_address

        self.heap[address] = value
        self.next_address += 1

        return address

    def obtener_heap(self, address: int) -> object:
        """Consultar el contenido de una dirección."""

        if address not in self.heap:
            raise MemoryManagerError(
                f"La dirección {address} no está reservada."
            )

        return self.heap[address]

    def escribir_heap(self, address: int, value: object) -> None:
        """Escribir un valor en una dirección reservada."""

        if address not in self.heap:
            raise MemoryManagerError(
                f"La dirección {address} no está reservada."
            )

        self.heap[address] = value

    def liberar_heap(self, address: int) -> None:
        """Liberar una posición reservada."""

        if address not in self.heap:
            raise MemoryManagerError(
                f"No se puede liberar la dirección {address}: "
                "no está reservada o ya fue liberada."
            )

        del self.heap[address]

    # ESTADO DE MEMORIA

    def snapshot(self) -> dict:
        """Obtener una copia del estado actual de la memoria."""

        return {
            "stack": [
                {
                    "name": frame.name,
                    "locals": frame.locals.copy()
                }
                for frame in self.stack
            ],
            "heap": self.heap.copy()
        }

    def reset(self) -> None:
        """Reiniciar la memoria para otra ejecución."""

        self.stack.clear()
        self.heap.clear()
        self.next_address = 1000