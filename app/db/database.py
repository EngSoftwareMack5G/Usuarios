import asyncpg
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

DB_POOL = None

DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

async def create_db_pool():
    global DB_POOL
    try:
        DB_POOL = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        logger.info("Pool de conexão com o banco de dados criado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao criar pool de conexão com o banco de dados: {e}")
        raise

async def close_db_pool():
    global DB_POOL
    if DB_POOL:
        await DB_POOL.close()
        logger.info("Pool de conexão com o banco de dados fechado.")

async def get_db_connection():
    if not DB_POOL:
        await create_db_pool() # Garante que o pool exista se não foi criado no startup
    async with DB_POOL.acquire() as connection:
        yield connection

async def init_db(conn: asyncpg.Connection):
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS perfis (
        email VARCHAR(255) PRIMARY KEY,
        nome VARCHAR(100),
        descricao TEXT,
        genero VARCHAR(20),
        foto BYTEA
    );
    """)
    logger.info("Tabela 'perfis' verificada/criada.")

# Função de conveniência para inicializar o DB no startup da aplicação
async def initialize_database():
    if not DB_POOL:
        await create_db_pool()
    async with DB_POOL.acquire() as conn:
        await init_db(conn)