from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: str = Field(..., example="admin@impacta.edu.br")
    senha: str = Field(..., min_length=6, example="123456")

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email deve conter @')
        return v.lower()

class RegisterRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, example="Administrador")
    email: str = Field(..., example="admin@impacta.edu.br")
    senha: str = Field(..., min_length=6, example="123456")
    confirmar_senha: str = Field(..., min_length=6, example="123456")

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email deve conter @')
        return v.lower()

    @validator('confirmar_senha')
    def validate_passwords_match(cls, v, values):
        if 'senha' in values and v != values['senha']:
            raise ValueError('Senhas não coincidem')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # 1 hora

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    matricula: str
    nome: str
    email: str
    criado_em: datetime
    ultimo_login: Optional[datetime] = None
    is_admin: bool = False
    tipo: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @validator('tipo', always=True)
    def set_user_type(cls, v, values):
        # Definir tipo baseado no campo is_admin
        if 'is_admin' in values and values['is_admin']:
            return 'admin'
        return 'usuario'
