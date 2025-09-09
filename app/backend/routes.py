from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app import models, schemas

router = APIRouter()

# Exemplo de rota POST para criar um livro
@router.post("/livros/")
async def create_livro(
    titulo: str = Form(...),
    autor_id: int = Form(...),
    genero: str = Form(None),
    ano_publicacao: int = Form(None),
    db: Session = Depends(get_db)
):
    db_livro = models.Livro(
        titulo=titulo,
        autor_id=autor_id,
        genero=genero,
        ano_publicacao=ano_publicacao
    )
    db.add(db_livro)
    db.commit()
    db.refresh(db_livro)
    return RedirectResponse(url="/livros", status_code=303)

# Adicione aqui outras rotas POST conforme necessário
