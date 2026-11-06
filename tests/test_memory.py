import pytest

from backend.nexus.memory import (
    MemoryManager,
    MemoryManagerError,
)


def test_creates_stack_frame():
    memory = MemoryManager()

    memory.push_stack_frame("main")

    assert len(memory.stack) == 1
    assert memory.stack[0].name == "main"


def test_declares_and_assigns_local_variable():
    memory = MemoryManager()

    memory.push_stack_frame()
    memory.declarar_local("edad")
    memory.asignar_local("edad", 20)

    assert memory.obtener_local("edad") == 20


def test_detects_undeclared_local_variable():
    memory = MemoryManager()

    memory.push_stack_frame()

    with pytest.raises(MemoryManagerError):
        memory.obtener_local("edad")


def test_nested_frames_support_variable_lookup():
    memory = MemoryManager()

    memory.push_stack_frame("main")
    memory.declarar_local("numero")
    memory.asignar_local("numero", 10)

    memory.push_stack_frame("function")
    memory.declarar_local("precio")
    memory.asignar_local("precio", 50)

    assert memory.obtener_local("numero") == 10
    assert memory.obtener_local("precio") == 50


def test_nested_frames_support_variable_shadowing():
    memory = MemoryManager()

    memory.push_stack_frame("main")
    memory.declarar_local("numero")
    memory.asignar_local("numero", 10)

    memory.push_stack_frame("function")
    memory.declarar_local("numero")
    memory.asignar_local("numero", 20)

    assert memory.obtener_local("numero") == 20

    memory.pop_stack_frame()

    assert memory.obtener_local("numero") == 10


def test_pop_frame_removes_local_variables():
    memory = MemoryManager()

    memory.push_stack_frame("main")
    memory.declarar_local("numero")

    memory.pop_stack_frame()

    assert len(memory.stack) == 0


def test_cannot_pop_empty_stack():
    memory = MemoryManager()

    with pytest.raises(MemoryManagerError):
        memory.pop_stack_frame()


def test_reserves_and_reads_heap_memory():
    memory = MemoryManager()

    address = memory.reservar_heap("Hola NEXUS")

    assert address == 1000
    assert memory.obtener_heap(address) == "Hola NEXUS"


def test_writes_to_reserved_heap_memory():
    memory = MemoryManager()

    address = memory.reservar_heap()

    memory.escribir_heap(address, 250)

    assert memory.obtener_heap(address) == 250


def test_releases_heap_memory():
    memory = MemoryManager()

    address = memory.reservar_heap(100)

    memory.liberar_heap(address)

    assert address not in memory.heap


def test_detects_double_free():
    memory = MemoryManager()

    address = memory.reservar_heap(100)

    memory.liberar_heap(address)

    with pytest.raises(
        MemoryManagerError,
        match="ya fue liberada"
    ):
        memory.liberar_heap(address)


def test_detects_invalid_heap_address():
    memory = MemoryManager()

    with pytest.raises(MemoryManagerError):
        memory.obtener_heap(9999)


def test_reset_clears_memory():
    memory = MemoryManager()

    memory.push_stack_frame()
    memory.declarar_local("numero")
    memory.asignar_local("numero", 10)

    memory.reservar_heap(200)

    memory.reset()

    assert memory.stack == []
    assert memory.heap == {}
    assert memory.next_address == 1000