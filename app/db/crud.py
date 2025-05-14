import asyncpg
from typing import Optional, Dict, Any
from app.models.perfil import PerfilCreate, PerfilUpdate

async def create_perfil(
    conn: asyncpg.Connection,
    email: str,
    perfil_data: PerfilCreate,
    foto_data: Optional[bytes]
) -> Dict[str, Any]:
    query = """
    INSERT INTO perfis (email, nome, descricao, genero, foto)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING email, nome, descricao, genero;
    """
    try:
        row = await conn.fetchrow(
            query,
            email,
            perfil_data.nome,
            perfil_data.descricao,
            perfil_data.genero,
            foto_data
        )
        return dict(row) if row else None
    except asyncpg.exceptions.UniqueViolationError:
        return None # Ou levantar uma exceção específica

async def get_perfil_by_email(conn: asyncpg.Connection, email: str) -> Optional[Dict[str, Any]]:
    query = "SELECT email, nome, descricao, genero FROM perfis WHERE email = $1;"
    row = await conn.fetchrow(query, email)
    return dict(row) if row else None

async def get_perfil_imagem_by_email(conn: asyncpg.Connection, email: str) -> Optional[bytes]:
    query = "SELECT foto FROM perfis WHERE email = $1;"
    row = await conn.fetchrow(query, email)
    return row['foto'] if row and row['foto'] else None

async def update_perfil(
    conn: asyncpg.Connection,
    email: str,
    perfil_data: PerfilUpdate,
    foto_data: Optional[bytes] = None
) -> Optional[Dict[str, Any]]:
    # Busca o perfil existente para não sobrescrever campos não enviados com None
    current_perfil = await get_perfil_by_email(conn, email)
    if not current_perfil:
        return None

    # Monta os campos a serem atualizados
    update_fields = perfil_data.model_dump(exclude_unset=True) # Pega apenas os campos fornecidos

    if not update_fields and foto_data is None: # Nada para atualizar
        return current_perfil

    set_clauses = []
    query_params = []
    param_idx = 1

    for key, value in update_fields.items():
        set_clauses.append(f"{key} = ${param_idx}")
        query_params.append(value)
        param_idx += 1

    if foto_data is not None:
        set_clauses.append(f"foto = ${param_idx}")
        query_params.append(foto_data)
        param_idx += 1
    
    query_params.append(email) # Para o WHERE clause

    if not set_clauses: # Caso só a foto tenha sido atualizada e update_fields estava vazio
        if foto_data is not None: # Caso especial onde apenas a foto é atualizada e outros campos não
             set_clauses.append(f"foto = ${param_idx -1}") # Reajusta o índice
        else:
            return current_perfil # Nada mudou

    query = f"""
    UPDATE perfis
    SET {', '.join(set_clauses)}
    WHERE email = ${param_idx}
    RETURNING email, nome, descricao, genero;
    """
    
    row = await conn.fetchrow(query, *query_params)
    return dict(row) if row else None


async def delete_perfil_by_email(conn: asyncpg.Connection, email: str) -> bool:
    query = "DELETE FROM perfis WHERE email = $1 RETURNING email;"
    deleted_email = await conn.fetchval(query, email)
    return deleted_email is not None