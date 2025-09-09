from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str = Field(..., example="Dom Casmurro")
    author_id: int = Field(..., example=1)
    year: Optional[int] = Field(None, example=1899)
    isbn: str = Field(..., example="978-8535931239")
    status: Optional[str] = Field("disponível", example="disponível")

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author_id: Optional[int] = None
    year: Optional[int] = None
    isbn: Optional[str] = None
    status: Optional[str] = None

class BookInDB(BookBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Book(BookInDB):
    pass
