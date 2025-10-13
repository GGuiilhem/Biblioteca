from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from app.models.models import TipoUsuario

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, example="João Silva")
    email: str = Field(..., max_length=100, example="joao.silva@impacta.edu.br")
    cpf: str = Field(..., min_length=11, max_length=11, example="12345678901")
    matricula: str = Field(..., max_length=20, example="2024001")
    tipo: Optional[TipoUsuario] = Field(TipoUsuario.ALUNO, example="aluno")
    curso: Optional[str] = Field(None, max_length=100, example="Análise e Desenvolvimento de Sistemas")
    telefone: Optional[str] = Field(None, max_length=20, example="(11) 99999-0001")
    endereco: Optional[str] = Field(None, example="Rua das Flores, 123")
    data_nascimento: Optional[date] = Field(None, example="2000-01-01")

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email deve conter @')
        return v.lower()

    @validator('cpf')
    def validate_cpf(cls, v):
        # Remove caracteres não numéricos
        clean_cpf = ''.join(c for c in v if c.isdigit())
        if len(clean_cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return clean_cpf

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    matricula: Optional[str] = Field(None, max_length=20)
    tipo: Optional[TipoUsuario] = None
    curso: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = None
    data_nascimento: Optional[date] = None
    ativo: Optional[bool] = None

class EmprestimoSimples(BaseModel):
    id: int
    livro_id: int
    data_emprestimo: datetime
    data_devolucao_prevista: datetime
    status: str
    
    class Config:
        from_attributes = True

class UsuarioInDB(UsuarioBase):
    id: int
    ativo: bool
    data_cadastro: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True

class Usuario(UsuarioInDB):
    emprestimos: List[EmprestimoSimples] = []

# Schemas para compatibilidade com código existente
UserBase = UsuarioBase
UserCreate = UsuarioCreate
UserUpdate = UsuarioUpdate
UserInDB = UsuarioInDB
User = Usuario
