from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.models import StatusReserva

class ReservaBase(BaseModel):
    livro_id: int
    usuario_id: int

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    status: StatusReserva

class Reserva(ReservaBase):
    id: int
    data_reserva: datetime
    status: StatusReserva
    data_validade: Optional[datetime] = None

    class Config:
        from_attributes = True
