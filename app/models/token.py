from pydantic import BaseModel, EmailStr

class TokenData(BaseModel):
    username: EmailStr # Payload do JWT terá o email no campo 'username'
    type: str