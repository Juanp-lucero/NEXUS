from fastapi.testclient import TestClient

from backend.api.main import app


client = TestClient(app)


# ==========================================
# 1. PRUEBAS GENERALES DE LA API
# ==========================================

def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "NEXUS Compiler API"
    assert data["status"] == "running"


def test_health_endpoint():

    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


# ==========================================
# 2. PRUEBA DE COMPILACIÓN EXITOSA
# ==========================================

def test_compile_valid_program():

    source = (
        "int numero1 = 10;\n"
        "int numero2 = 5;\n"
        "int resultado;\n"
        "resultado = numero1 + numero2 * 2;\n"
        "print(resultado);"
    )

    response = client.post(
        "/api/compile",
        json={"source": source}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["execution"]["output"] == ["20"]

    assert data["execution"]["variables"]["resultado"] == 20

    assert len(data["tokens"]) > 0

    assert data["ast"]["node"] == "Program"

    assert len(data["symbol_table"]) == 3

    assert len(data["tac"]) > 0

    assert len(data["quadruples"]) > 0

    assert data["execution"]["instructions_executed"] == 9

    assert data["execution"]["stack"][0]["name"] == "main"


# ==========================================
# 3. ERROR LÉXICO
# ==========================================

def test_compile_lexical_error():

    source = "int numero = 10; @"

    response = client.post(
        "/api/compile",
        json={"source": source}
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"]["stage"] == "lexer"

    assert "Carácter no reconocido" in data["detail"]["message"]


# ==========================================
# 4. ERROR SINTÁCTICO
# ==========================================

def test_compile_syntax_error():

    source = "int edad = 20"

    response = client.post(
        "/api/compile",
        json={"source": source}
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"]["stage"] == "parser"

    assert "Se esperaba ';'" in data["detail"]["message"]


# ==========================================
# 5. ERROR SEMÁNTICO
# ==========================================

def test_compile_semantic_error():

    source = "resultado = 100;"

    response = client.post(
        "/api/compile",
        json={"source": source}
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"]["stage"] == "semantic"

    assert "no ha sido declarada" in data["detail"]["message"]


# ==========================================
# 6. ERROR DE EJECUCIÓN
# ==========================================

def test_compile_execution_error():

    source = "float resultado = 10 / 0;"

    response = client.post(
        "/api/compile",
        json={"source": source}
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"]["stage"] == "virtual_machine"

    assert "No se pudo realizar la operación" in (
        data["detail"]["message"]
    )


# ==========================================
# 7. VALIDACIÓN DE ENTRADA
# ==========================================

def test_compile_empty_source():

    response = client.post(
        "/api/compile",
        json={"source": ""}
    )

    assert response.status_code == 422

    data = response.json()

    assert "detail" in data


# ==========================================
# 8. VALIDACIÓN DE CAMPOS OBLIGATORIOS
# ==========================================

def test_compile_without_source_field():

    response = client.post(
        "/api/compile",
        json={}
    )

    assert response.status_code == 422

    data = response.json()

    assert "detail" in data