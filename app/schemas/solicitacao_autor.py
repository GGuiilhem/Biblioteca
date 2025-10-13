from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.models.models import StatusSolicitacao

class SolicitacaoAutorBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100, example="Machado de Assis")
    nacionalidade: Optional[str] = Field(None, max_length=50, example="Brasileira")
    data_nascimento: Optional[date] = Field(None, example="1839-06-21")
    biografia: Optional[str] = Field(None, example="Joaquim Maria Machado de Assis foi um escritor brasileiro...")

class SolicitacaoAutorCreate(SolicitacaoAutorBase):
    pass

class SolicitacaoAutorUpdate(BaseModel):
    status: StatusSolicitacao
    observacoes: Optional[str] = None

class SolicitacaoAutorResponse(SolicitacaoAutorBase):
    id: int
    status: StatusSolicitacao
    data_solicitacao: datetime
    data_aprovacao: Optional[datetime] = None
    observacoes: Optional[str] = None
    solicitante_nome: str
    aprovado_por_nome: Optional[str] = None
    
    class Config:
        from_attributes = True

class SolicitacaoAutorSimples(BaseModel):
    id: int
    nome: str
    status: StatusSolicitacao
    data_solicitacao: datetime
    solicitante_nome: str
    
    class Config:
        from_attributes = True
