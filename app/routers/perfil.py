from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import Response, JSONResponse
from typing import Optional
import asyncpg

from app.db.database import get_db_connection
from app.db import crud
from app.models.perfil import PerfilCreate, PerfilUpdate, PerfilResponse
from app.models.token import TokenData
from app.core.security import get_current_user # authorize_perfil_access não será mais usado diretamente aqui
from app.core.config import settings

router = APIRouter(
    prefix="/perfil", # O prefixo continua o mesmo
    tags=["Perfis"],
)

MAX_IMAGE_SIZE = settings.MAX_IMAGE_SIZE
ALLOWED_IMAGE_TYPES = settings.ALLOWED_IMAGE_TYPES

async def validate_image(foto: UploadFile):
    if foto.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de imagem inválido. Permitidos: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    contents = await foto.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Imagem excede o tamanho máximo de {MAX_IMAGE_SIZE / (1024*1024)}MB"
        )
    await foto.seek(0) # Resetar o ponteiro do arquivo para leitura posterior
    return contents

@router.post("", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED)
async def criar_perfil_usuario_logado( # Nome da função mais descritivo
    nome: str = Form(...),
    descricao: Optional[str] = Form(None),
    genero: Optional[str] = Form(None),
    foto: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Cria ou atualiza o perfil do usuário autenticado.
    O e-mail do perfil será o e-mail do usuário autenticado no token.
    Se o perfil já existir, ele será atualizado (comportamento de upsert implícito).
    Para um POST que cria estritamente, verificaríamos primeiro a existência.
    """
    email = current_user.username # Email é obtido do token JWT
    
    # Verificar se o perfil já existe para decidir entre criar ou informar conflito
    existing_perfil = await crud.get_perfil_by_email(conn, email)
    if existing_perfil:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Perfil com este e-mail já existe. Use PUT para atualizar."
        )

    foto_data = await validate_image(foto)
        
    perfil_in = PerfilCreate(nome=nome, descricao=descricao, genero=genero)
    
    created_perfil = await crud.create_perfil(conn, email, perfil_in, foto_data)
    if not created_perfil:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Não foi possível criar o perfil.")
    
    return PerfilResponse(**created_perfil)

@router.get("", response_model=PerfilResponse) # Rota alterada: sem {perfil_email}
async def ler_perfil_usuario_logado( # Nome da função mais descritivo
    current_user: TokenData = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Retorna os dados do perfil do usuário autenticado (sem a imagem).
    O e-mail é obtido do token JWT.
    """
    email = current_user.username # Email é obtido do token JWT
    
    # authorize_perfil_access(current_user.username, perfil_email) # Não é mais necessário
    
    perfil = await crud.get_perfil_by_email(conn, email)
    if not perfil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado para o usuário autenticado")
    return PerfilResponse(**perfil)

@router.get("/imagem") # Rota alterada: sem {perfil_email}
async def ler_imagem_perfil_usuario_logado( # Nome da função mais descritivo
    current_user: TokenData = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Retorna somente a imagem do perfil do usuário autenticado.
    O e-mail é obtido do token JWT.
    """
    email = current_user.username # Email é obtido do token JWT
    
    # authorize_perfil_access(current_user.username, perfil_email) # Não é mais necessário
    
    foto_data = await crud.get_perfil_imagem_by_email(conn, email)
    if not foto_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagem do perfil não encontrada para o usuário autenticado")

    media_type = "application/octet-stream"
    if foto_data.startswith(b'\x89PNG'):
        media_type = "image/png"
    elif foto_data.startswith(b'\xff\xd8'):
        media_type = "image/jpeg"
    
    if media_type == "application/octet-stream" and "image/jpeg" in ALLOWED_IMAGE_TYPES:
        media_type = "image/jpeg"

    return Response(content=foto_data, media_type=media_type)


@router.put("", response_model=PerfilResponse) # Rota alterada: sem {perfil_email}
async def atualizar_perfil_usuario_logado( # Nome da função mais descritivo
    nome: Optional[str] = Form(None),
    descricao: Optional[str] = Form(None),
    genero: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    current_user: TokenData = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Atualiza os dados do perfil do usuário autenticado (inclusive a imagem, se fornecida).
    O e-mail é obtido do token JWT.
    """
    email = current_user.username # Email é obtido do token JWT

    # authorize_perfil_access(current_user.username, perfil_email) # Não é mais necessário

    perfil_existente = await crud.get_perfil_by_email(conn, email)
    if not perfil_existente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado para o usuário autenticado. Crie um perfil primeiro usando POST.")

    foto_data = None
    if foto:
        foto_data = await validate_image(foto)

    perfil_update_data = PerfilUpdate(nome=nome, descricao=descricao, genero=genero)
    update_data_dict = perfil_update_data.model_dump(exclude_none=True) 
    
    if not update_data_dict and foto_data is None:
         # Retorna o perfil existente como está se nada for alterado
         return PerfilResponse(**perfil_existente)

    updated_perfil = await crud.update_perfil(conn, email, PerfilUpdate(**update_data_dict), foto_data)
    
    if not updated_perfil: 
        # Esta condição é improvável de ser atingida se perfil_existente foi encontrado
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado para atualização")
    
    return PerfilResponse(**updated_perfil)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT) # Rota alterada: sem {perfil_email}
async def remover_perfil_usuario_logado( # Nome da função mais descritivo
    current_user: TokenData = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Remove o perfil do usuário autenticado.
    O e-mail é obtido do token JWT.
    """
    email = current_user.username # Email é obtido do token JWT
    
    # authorize_perfil_access(current_user.username, perfil_email) # Não é mais necessário
    
    deleted = await crud.delete_perfil_by_email(conn, email)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado para o usuário autenticado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)