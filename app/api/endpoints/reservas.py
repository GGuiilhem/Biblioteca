from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import Reserva as DBReserva, Livro as DBLivro, Usuario as DBUsuario, StatusLivro, StatusReserva
from app.schemas.reserva import Reserva, ReservaCreate, ReservaUpdate
from app.core.auth import get_current_user
from app.models.models import UsuarioAuth

router = APIRouter()

@router.post("/reservas/", response_model=Reserva, status_code=201)
def create_reserva(
    reserva: ReservaCreate, 
    db: Session = Depends(get_db)
):
    """
    Cria uma nova reserva para um livro
    """
    # Verificar se o livro existe
    livro = db.query(DBLivro).filter(DBLivro.id == reserva.livro_id).first()
    if not livro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado"
        )
    
    # Verificar se o livro está emprestado (só pode reservar se estiver emprestado)
    if livro.status != StatusLivro.EMPRESTADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas livros emprestados podem ser reservados"
        )

    # Verificar se o usuário existe
    usuario = db.query(DBUsuario).filter(DBUsuario.id == reserva.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # Verificar se o usuário já tem reserva ativa para este livro
    reserva_existente = db.query(DBReserva).filter(
        DBReserva.usuario_id == reserva.usuario_id,
        DBReserva.livro_id == reserva.livro_id,
        DBReserva.status == StatusReserva.PENDENTE
    ).first()

    if reserva_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já possui uma reserva pendente para este livro"
        )

    # Criar a reserva
    db_reserva = DBReserva(
        usuario_id=reserva.usuario_id,
        livro_id=reserva.livro_id,
        status=StatusReserva.PENDENTE,
        data_validade=datetime.utcnow() + timedelta(days=7) # Validade de 7 dias
    )
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    
    return db_reserva

@router.get("/reservas/", response_model=List[Reserva])
def read_reservas(
    skip: int = 0, 
    limit: int = 100,
    usuario_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Lista todas as reservas
    """
    query = db.query(DBReserva)
    
    if usuario_id:
        query = query.filter(DBReserva.usuario_id == usuario_id)
        
    reservas = query.offset(skip).limit(limit).all()
    return reservas

@router.delete("/reservas/{reserva_id}")
def cancel_reserva(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancela uma reserva
    """
    reserva = db.query(DBReserva).filter(DBReserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    reserva.status = StatusReserva.CANCELADA
    db.commit()
    
    return {"message": "Reserva cancelada com sucesso"}
