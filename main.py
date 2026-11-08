# main.py
import os
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Configuración de base de datos (Soporta PostgreSQL de Azure/Docker o SQLite local por defecto)
DATABASE_URL = os.getenv("DB_URL", "sqlite:///./notes.db")

# Si el string proviene de PostgreSQL con 'postgres://', SQLAlchemy requiere 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Base de Datos
class NoteModel(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

# Creación de tablas al iniciar
Base.metadata.create_all(bind=engine)

# Esquemas Pydantic v2 (compatibles con Python 3.14)
class NoteCreate(BaseModel):
    text: str

class NoteResponse(BaseModel):
    id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Inicialización de la API
app = FastAPI(title="Notes MVP API")

# Configuración CORS para conexión con el Frontend
cors_origin = os.getenv("CORS_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin] if cors_origin != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inyección de dependencia para la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints CRUD
@app.get("/api/notes", response_model=List[NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    """Retorna la lista de notas ordenadas desde la más reciente[cite: 3]."""
    return db.query(NoteModel).order_by(NoteModel.created_at.desc()).all()

@app.post("/api/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """Crea una nueva nota[cite: 3]."""
    db_note = NoteModel(text=note.text)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.delete("/api/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Elimina una nota por su ID."""
    db_note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    db.delete(db_note)
    db.commit()
    return None