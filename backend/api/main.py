from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.api.compiler_service import compile_source

from backend.nexus.lexer.lexer import LexicalError
from backend.nexus.parser import ParseError
from backend.nexus.semantic import SemanticError
from backend.nexus.ir import IRGenerationError
from backend.nexus.runtime import ExecutionError


# Crear aplicación
app = FastAPI(
    title="NEXUS Compiler API",
    description=(
        "API para analizar, traducir y ejecutar "
        "programas escritos en NexusLang."
    ),
    version="1.0.0"
)


# Configuración CORS para la futura interfaz React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelo de entrada
class CompileRequest(BaseModel):

    source: str = Field(
        min_length=1,
        max_length=50000,
        description="Código fuente escrito en NexusLang."
    )


# Ruta principal
@app.get("/")
def root():

    return {
        "application": "NEXUS Compiler API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs"
    }


# Comprobar estado del servidor
@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "service": "NEXUS Compiler API"
    }


# Compilar y ejecutar código
@app.post("/api/compile")
def compile_program(request: CompileRequest):

    try:

        result = compile_source(request.source)

        return result

    except LexicalError as error:

        raise HTTPException(
            status_code=422,
            detail={
                "stage": "lexer",
                "message": str(error)
            }
        )

    except ParseError as error:

        raise HTTPException(
            status_code=422,
            detail={
                "stage": "parser",
                "message": str(error)
            }
        )

    except SemanticError as error:

        raise HTTPException(
            status_code=422,
            detail={
                "stage": "semantic",
                "message": str(error)
            }
        )

    except IRGenerationError as error:

        raise HTTPException(
            status_code=422,
            detail={
                "stage": "intermediate_code",
                "message": str(error)
            }
        )

    except ExecutionError as error:

        raise HTTPException(
            status_code=422,
            detail={
                "stage": "virtual_machine",
                "message": str(error)
            }
        )