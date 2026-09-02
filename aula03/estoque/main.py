import time
from fastapi import FastAPI, HTTPException, Header

app = FastAPI(title="Servico de Estoque")

produtos = {
    1: {
        "nome": "Teclado",
        "quantidade": 10,
        "preco": 150.00
    },
    2: {
        "nome": "Mouse",
        "quantidade": 0,
        "preco": 80.00
    },
    3: {
        "nome": "Monitor",
        "quantidade": 4,
        "preco": 900.00
    },
}


@app.get("/produtos/{produto_id}/estoque")
def consultar_estoque(
    produto_id: int,
    correlation_id: str | None = Header(default=None)
):
    time.sleep(1)

    produto = produtos.get(produto_id)

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto nao encontrado"
        )

    return {
    "produto_id": produto_id,
    "nome": produto["nome"],
    "quantidade_disponivel": produto["quantidade"],
    "correlation_id": correlation_id
}

@app.get("/produtos/{produto_id}")
def consultar_produto(produto_id: int):
    produto = produtos.get(produto_id)

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto nao encontrado"
        )

    return {
        "produto_id": produto_id,
        "nome": produto["nome"],
        "quantidade": produto["quantidade"],
        "preco": produto["preco"]
    }