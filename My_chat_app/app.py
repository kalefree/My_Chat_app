from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from uuid import uuid4
import csv

app = FastAPI()
templates = Jinja2Templates(directory="templates")
connected_clients = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# @app.get("/")
# async def get(request: Request):
#     return templates.TemplateResponse("getname.html", {"request": request})

@app.post("/chat")
async def chat(request: Request, name: str = Form(...)):
    # with open('client_data.csv', mode='a') as csv_file:
    #     fieldnames = ['name', 'userAgent', 'language', 'platform', 'ipAddress', 'screenWidth', 'screenHeight', 'windowWidth', 'windowHeight']
    #     writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter='|')
    #     if csv_file.tell() == 0:
    #         writer.writeheader()
    #     if clientInfo["ipAddress"] == "":
    #         clientInfo["ipAddress"] = request.client.host
    #     writer.writerow(clientInfo)
    # this = templates.TemplateResponse("chat.html", {"request": request, "name": clientInfo["name"]})
    # name = clientinfo["name"]

    return templates.TemplateResponse("chat.html", {"request": request, "name": name })
    

@app.websocket("/chat/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{name}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{name} left the chat")



# @app.post("/hello")
# async def register(request: Request, name: str = Form(...)):
#     return templates.TemplateResponse("helloname.html", {"request": request, "name": name})