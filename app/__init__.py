from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.core.config import settings # Importa para garantir que settings sejam carregadas
from app.db.database import create_db_pool, close_db_pool, initialize_database
from app.routers import perfil as perfil_router

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialização
    logger.info("Iniciando aplicação...")
    await create_db_pool()
    logger.info("Pool de conexão com o banco de dados criado.")
    try:
        await initialize_database() # Cria a tabela se não existir
        logger.info("Banco de dados inicializado.")
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        # Decide se quer parar a aplicação ou continuar sem DB funcional
        # raise # Para a aplicação se o DB for crítico

    yield # Aplicação está rodando

    # Código de limpeza
    logger.info("Encerrando aplicação...")
    await close_db_pool()
    logger.info("Pool de conexão com o banco de dados fechado.")


app = FastAPI(
    title="API de Gerenciamento de Perfis",
    description="Uma API para gerenciar perfis de usuário com FastAPI e PostgreSQL.",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(perfil_router.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API de Gerenciamento de Perfis!"}

# Para gerar um token de teste (NÃO FAÇA ISSO EM PRODUÇÃO SEM AUTENTICAÇÃO REAL)
# Este endpoint é apenas para facilitar os testes, já que não temos um sistema de login/registro.
from app.core.security import create_access_token
from pydantic import EmailStr
from fastapi import Form as FastAPIForm # Renomeado para evitar conflito com o Form de UploadFile

@app.post("/generate-test-token", tags=["Test Utils"])
async def generate_test_token(email: EmailStr = FastAPIForm(...)):
    """
    Endpoint de conveniência para gerar um token JWT para teste.
    **NÃO USE EM PRODUÇÃO.** O email fornecido será o 'username' no payload do token.
    """
    access_token = create_access_token(data={"username": email})
    return {"access_token": access_token, "token_type": "bearer", "email_in_token": email}