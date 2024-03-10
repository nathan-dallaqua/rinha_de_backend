from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from load_balancer import LoadBalancer

app = FastAPI()

class Transaction(BaseModel):
    value: int
    type: str
    description: str

class Balance(BaseModel):
    total: int
    statement_date: datetime
    limit: int

class Statement(BaseModel):
    load_balancer: Optional[LoadBalancer]
    balance: Balance
    recent_transactions: List[Transaction]

CLIENTS = {
    1: {"limit": 100000, "balance": 0, "transactions": []},
    2: {"limit": 80000, "balance": 0, "transactions": []},
    3: {"limit": 1000000, "balance": 0, "transactions": []},
    4: {"limit": 10000000, "balance": 0, "transactions": []},
    5: {"limit": 500000, "balance": 0, "transactions": []},
}

@app.post("/clients/{client_id}/transactions")
async def create_transaction(client_id: int, transaction: Transaction):
    if client_id not in CLIENTS:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client = CLIENTS[client_id]
    if transaction.type == "d" and (client["balance"] - transaction.value) < -client["limit"]:
        raise HTTPException(status_code=422, detail="Limite de débito excedido")

    client["transactions"].append(transaction)
    if transaction.type == "c":
        client["balance"] += transaction.value
    else:
        client["balance"] -= transaction.value
    
    return {"limit": client["limit"], "balance": client["balance"]}

@app.get("/clients/{client_id}/statement")
async def get_statement(client_id: int):
    if client_id not in CLIENTS:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client = CLIENTS[client_id]
    total_balance = client["balance"]
    statement_date = datetime.utcnow()
    limit = client["limit"]
    recent_transactions = client["transactions"][-10:]
    load_balancer = LoadBalancer(hostname="rinha-load-balancer", port=9999)

    return {"load_balancer": load_balancer,
            "balance": {"total": total_balance, "statement_date": statement_date, "limit": limit},
            "recent_transactions": recent_transactions}
