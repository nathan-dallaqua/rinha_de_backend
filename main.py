from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from load_balancer import LoadBalancer
from database import get_db_connection

app = FastAPI()

class Transaction(BaseModel):
    valor: int
    tipo: str
    descricao: str

class Balance(BaseModel):
    total: int
    data_extrato: datetime
    limite: int

class Statement(BaseModel):
    load_balancer: Optional[LoadBalancer]
    saldo: Balance
    ultimas_transacoes: List[Transaction]


def get_clients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients")
    rows = cur.fetchall()
    clients = {}
    for row in rows:
        clients[row[0]] = {"limit": row[1], "balance": row[2], "transactions": []}
    cur.close()
    conn.close()
    return clients

@app.post("/clients/{client_id}/transactions")
async def create_transaction(client_id: int, transaction: Transaction):
    clients = get_clients()
    if client_id not in clients:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client = clients[client_id]
    if transaction.tipo == "d" and (client["saldo"] - transaction.valor) < -client["limite"]:
        raise HTTPException(status_code=422, detail="Debit transaction exceeds available limite")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (client_id, valor, tipo, descricao) VALUES (%s, %s, %s, %s)", (client_id, transaction.valor, transaction.tipo, transaction.descricao))
    conn.commit()
    cur.close()
    conn.close()

    client["transactions"].append(transaction)
    if transaction.tipo == "c":
        client["saldo"] += transaction.valor
    else:
        client["saldo"] -= transaction.valor
    
    return {"limite": client["limite"], "saldo": client["saldo"]}

@app.get("/clients/{client_id}/statement")
async def get_statement(client_id: int):
    clients = get_clients()
    if client_id not in clients:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client = clients[client_id]
    saldo_total = client["saldo"]
    data_extrato = datetime.utcnow()
    limite = client["limite"]
    ultimas_transacoes = client["transactions"][-10:]
    load_balancer = LoadBalancer(hostname="rinha-load-balancer", port=9999)

    return {"load_balancer": load_balancer,
            "saldo": {"total": saldo_total, "data_extrato": data_extrato, "limite": limite},
            "ultimas_transacoes": ultimas_transacoes}
