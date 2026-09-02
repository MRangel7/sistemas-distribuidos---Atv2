from fastapi import FastAPI, HTTPException, Response, Header
from pydantic import BaseModel, Field
import httpx

app = FastAPI(title="Servico de Pedidos")

ESTOQUE_URL = "http://localhost:8001"

pedidos = {}
proximo_id = 1


class NovoPedido(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


@app.post("/pedidos", status_code=201)
def criar_pedido(
    pedido: NovoPedido,
    response: Response,
    correlation_id: str | None = Header(default=None)
):
    global proximo_id

    url = f"{ESTOQUE_URL}/produtos/{pedido.produto_id}/estoque"

    try:
        headers = {}

        if correlation_id:
            headers["correlation-id"] = correlation_id

        resposta = httpx.get(
            url,
            headers=headers,
            timeout=3.0
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Servico de estoque indisponivel"
        )

    if resposta.status_code == 404:
        raise HTTPException(
            status_code=400,
            detail="Produto inexistente"
        )

    if resposta.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Falha ao consultar estoque"
        )

    estoque = resposta.json()

    if estoque["quantidade_disponivel"] < pedido.quantidade:
        raise HTTPException(
            status_code=409,
            detail="Estoque insuficiente"
        )

    novo_pedido = {
        "pedido_id": proximo_id,
        "status": "aceito",
        "produto_id": pedido.produto_id,
        "quantidade": pedido.quantidade
    }

    pedidos[proximo_id] = novo_pedido

    response.headers["Location"] = f"/pedidos/{proximo_id}"

    proximo_id += 1

    return novo_pedido


@app.get("/pedidos/{pedido_id}")
def consultar_pedido(pedido_id: int):
    pedido = pedidos.get(pedido_id)

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido nao encontrado"
        )

    return pedido