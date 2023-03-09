from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from uuid import uuid4
from secrets import openai_token
import csv
import openai
import time

openai.api_key = openai_token


app = FastAPI()
templates = Jinja2Templates(directory="templates")
connected_clients = {}


add_AI_agent = False

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

@app.post("/chat")
async def chat(request: Request, name: str = Form(...), ai: Optional[str] = Form(None)):
    if ai == "on" : 
        add_AI_agent = True
    else : 
        add_AI_agent = False
        
    return templates.TemplateResponse("chat.html", {"request": request, "name": name})
 

@app.websocket("/chat/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{name}: {data}")
            if add_AI_agent :
                prompt = data.strip()
                response = openai.Completion.create(
                    engine="davinci",
                    prompt=prompt,
                    max_tokens=60,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
                ai_chat_response = response.choices[0].text.strip()
                time.sleep(1)
                await websocket.broadcast(f"AI: {ai_chat_response}")    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{name} left the chat")

