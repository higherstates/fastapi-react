from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS:
origins = [
  'http://localhost:3000'
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])


# Validate with Pydantic:
class TransactionBase(BaseModel):
  amount: float
  category: str
  description: str
  is_income: bool
  date: str

class TransactionModel(TransactionBase):
  id: int

  class Config:
    orm_mode: True


#  Create Database dependency:
def get_db():
  db = SessionLocal()

  # Try create a DB connection, close it after:
  try:
    yield db
  finally:
    db.close()


# We're creating our DB and our DB is going to create our table & columns automatically when this FastAPI app is created:
db_dependency = Annotated[Session, Depends(get_db)]

models.Base.metadata.create_all(bind=engine)

#  First endpoint for our transaction app:
@app.post("/transactions", response_model=TransactionModel)
async def create_transaction(transaction: TransactionBase, db: db_dependency):
  db_transaction = models.Transaction(**transaction.dict())
  db.add(db_transaction)
  db.commit()
  db.refresh(db_transaction)
  return db_transaction


#  Get data from our SQLite DB:
@app.get("/transactions", response_model=List[TransactionModel])
async def read_transaction(db: db_dependency, skip: int = 0, limit: int = 100):  # Query params that will allow us to be able to fetch a certain amount of transactions for our app.
  transactions = db.query(models.Transaction).offset(skip).limit(limit).all()
  return transactions
