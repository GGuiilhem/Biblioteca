from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, timedelta
from app.models.models import StatusEmprestimo

class EmprestimoBase(BaseModel):
    usuario_id: int = Field(..., gt=0, example=1)
    livro_id: int = Field(..., gt=0, example=1)
    observacoes: Optional[str] = Field(None, example="Livro em bom estado")

class EmprestimoCreate(EmprestimoBase):
    pass

class EmprestimoUpdate(BaseModel):
    data_devolucao_real: Optional[datetime] = None
    status: Optional[StatusEmprestimo] = None
    multa: Optional[float] = Field(None, ge=0)
    observacoes: Optional[str] = None

class EmprestimoInDB(EmprestimoBase):
    id: int
    data_emprestimo: datetime
    data_devolucao_prevista: datetime
    data_devolucao_real: Optional[datetime]
    status: StatusEmprestimo
    multa: float
    
    class Config:
        from_attributes = True
        use_enum_values = True

class Emprestimo(EmprestimoInDB):
    pass
