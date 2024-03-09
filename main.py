from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from databases import Database

app = FastAPI()

database = Database('sqlite:///transactions.db')

class Transaction(BaseModel):
    client_id: int
    value: int
    type: str
    description: str

@app.on_event("startup")
async def startup():
    await database.connect()
    await create_tables()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

async def create_tables():
    query = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        value INTEGER,
        type TEXT,
        description TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    await database.execute(query)

@app.post("/transactions/")
async def create_transaction(transaction: Transaction):
    query = """
    INSERT INTO transactions (client_id, value, type, description)
    VALUES (:client_id, :value, :type, :description);
    """
    values = {
        "client_id": transaction.client_id,
        "value": transaction.value,
        "type": transaction.type,
        "description": transaction.description
    }
    await database.execute(query=query, values=values)
    return {"status": "Transaction created"}

@app.get("/transactions/{client_id}")
async def get_transactions(client_id: int):
    query = """
    SELECT * FROM transactions WHERE client_id = :client_id;
    """
    transactions = await database.fetch_all(query=query, values={"client_id": client_id})
    return transactions
