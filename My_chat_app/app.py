from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from uuid import uuid4

app = FastAPI()
templates = Jinja2Templates(directory="templates")
connected_clients = {}

@app.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connected_clients[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            for id, client in connected_clients.items():
                if id != client_id:
                    await client.send_text(f"{client_id}: {data}")
    except WebSocketDisconnect:
        del connected_clients[client_id]

@app.get("/")
async def get(request: Request):
    client_id = str(uuid4())
    return templates.TemplateResponse("index.html", {"request": request, "client_id": client_id})
