from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

class AutorBase(BaseModel):
    nome: str = Field(..., example="Machado de Assis")
    nacionalidade: Optional[str] = Field(None, example="Brasileiro")
    data_nascimento: Optional[date] = Field(None, example="1839-06-21")
    biografia: Optional[str] = Field(None, example="Joaquim Maria Machado de Assis foi um escritor brasileiro...")

class AutorCreate(AutorBase):
    pass

class AutorUpdate(BaseModel):
    nome: Optional[str] = None
    nacionalidade: Optional[str] = None
    data_nascimento: Optional[date] = None
    biografia: Optional[str] = None

class AutorInDB(AutorBase):
    id: int
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

class Autor(AutorInDB):
    pass

class LivroSimples(BaseModel):
    id: int
    titulo: str
    
    class Config:
        from_attributes = True

class AutorComLivros(Autor):
    livros: List[LivroSimples] = []
