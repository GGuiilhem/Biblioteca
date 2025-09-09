from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Autor as DBAutor
from app.schemas.author import Autor, AutorCreate, AutorUpdate

router = APIRouter(prefix="/v1")

@router.post("/authors/", response_model=Autor, status_code=201)
def create_author(autor: AutorCreate, db: Session = Depends(get_db)):
    """
    Cria um novo autor
    """
    db_autor = DBAutor(**autor.dict())
    db.add(db_autor)
    db.commit()
    db.refresh(db_autor)
    return db_autor

@router.get("/authors/", response_model=List[Autor])
def read_authors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos os autores
    """
    autores = db.query(DBAutor).offset(skip).limit(limit).all()
    return autores

@router.get("/authors/{autor_id}", response_model=Autor)
def read_autor(autor_id: int, db: Session = Depends(get_db)):
    """
    Busca um autor específico pelo ID
    """
    db_autor = db.query(DBAutor).filter(DBAutor.id == autor_id).first()
    if db_autor is None:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    return db_autor

@router.put("/authors/{autor_id}", response_model=Autor)
def update_autor(
    autor_id: int,
    autor: AutorUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza um autor existente
    """
    db_autor = db.query(DBAutor).filter(DBAutor.id == autor_id).first()
    if db_autor is None:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    update_data = autor.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_autor, key, value)

    db.add(db_autor)
    db.commit()
    db.refresh(db_autor)
    return db_autor

@router.delete("/authors/{autor_id}", status_code=204)
def delete_autor(autor_id: int, db: Session = Depends(get_db)):
    """
    Deleta um autor
    """
    db_autor = db.query(DBAutor).filter(DBAutor.id == autor_id).first()
    if db_autor is None:
        raise HTTPException(status_code=404, detail="Autor não encontrado")

    db.delete(db_autor)
    db.commit()
    return {"ok": True}
