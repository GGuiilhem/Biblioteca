from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.models import StatusLivro

class LivroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200, example="Dom Casmurro")
    subtitulo: Optional[str] = Field(None, max_length=200, example="Romance")
    autor_id: int = Field(..., gt=0, example=1)
    editora_id: Optional[int] = Field(None, gt=0, example=1)
    isbn: str = Field(..., min_length=10, max_length=13, example="9788535902777")
    edicao: Optional[int] = Field(1, gt=0, example=1)
    ano_publicacao: Optional[int] = Field(None, ge=1000, le=2100, example=1899)
    num_paginas: Optional[int] = Field(None, gt=0, example=256)
    sinopse: Optional[str] = Field(None, example="Romance narrado em primeira pessoa...")
    genero: Optional[str] = Field(None, max_length=50, example="Romance")
    idioma: Optional[str] = Field("Português", max_length=20, example="Português")
    capa_url: Optional[str] = Field(None, max_length=255)

    @validator('isbn')
    def validate_isbn(cls, v):
        if not v:
            raise ValueError('ISBN é obrigatório')
        
        # Garantir que é string e contém apenas dígitos
        isbn_str = str(v).strip()
        if not isbn_str.isdigit():
            raise ValueError('ISBN deve conter apenas números')
        
        # Validar comprimento
        if len(isbn_str) not in [10, 13]:
            raise ValueError(f'ISBN deve ter 10 ou 13 dígitos. Recebido: {len(isbn_str)} dígitos')
        
        return isbn_str

class LivroCreate(LivroBase):
    pass

class LivroUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    subtitulo: Optional[str] = Field(None, max_length=200)
    autor_id: Optional[int] = Field(None, gt=0)
    editora_id: Optional[int] = Field(None, gt=0)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    edicao: Optional[int] = Field(None, gt=0)
    ano_publicacao: Optional[int] = Field(None, ge=1000, le=2100)
    num_paginas: Optional[int] = Field(None, gt=0)
    sinopse: Optional[str] = None
    genero: Optional[str] = Field(None, max_length=50)
    idioma: Optional[str] = Field(None, max_length=20)
    status: Optional[StatusLivro] = None
    capa_url: Optional[str] = Field(None, max_length=255)

class AutorSimples(BaseModel):
    id: int
    nome: str
    
    class Config:
        from_attributes = True

class EditoraSimples(BaseModel):
    id: int
    nome: str
    
    class Config:
        from_attributes = True

class CategoriaSimples(BaseModel):
    id: int
    nome: str
    
    class Config:
        from_attributes = True

class LivroInDB(LivroBase):
    id: int
    status: StatusLivro
    data_cadastro: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True

class Livro(LivroInDB):
    autor: Optional[AutorSimples] = None
    editora: Optional[EditoraSimples] = None
    categorias: List[CategoriaSimples] = []

# Schemas para compatibilidade com código existente
BookBase = LivroBase
BookCreate = LivroCreate
BookUpdate = LivroUpdate
BookInDB = LivroInDB
Book = Livro
