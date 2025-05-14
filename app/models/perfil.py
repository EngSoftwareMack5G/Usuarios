from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Union

class PerfilBase(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = None
    genero: Optional[str] = Field(None, max_length=20)

class PerfilCreate(PerfilBase):
    nome: str = Field(max_length=100) # Nome é obrigatório na criação

class PerfilUpdate(PerfilBase):
    pass # Todos os campos são opcionais na atualização

class PerfilInDBBase(PerfilBase):
    email: EmailStr

    class Config:
        from_attributes = True # Anteriormente orm_mode

class PerfilResponse(PerfilInDBBase):
    pass # Retorna todos os campos (sem a foto)

class PerfilComFoto(PerfilInDBBase):
    foto: Optional[bytes] = None # Para uso interno, se necessário