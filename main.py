import os
import json
import logging

import uvicorn
import websockets

from typing import Dict
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()
URI = 'ws://127.0.0.1:5100'
AUTH_KEY = os.environ['AUTH_KEY']


async def send_message(msg: str):
    async with websockets.connect(URI) as websocket:  # type: ignore[attr-defined]
        obj = {
            "auth_code": AUTH_KEY,
            "action": msg
        }
        request = json.dumps(obj)
        await websocket.send(request)
        logging.info(f"[ws client] message  > {request}")
        response = await websocket.recv()
        logging.info(f"[ws server] message  < {response}")
        return json.loads(response)


@app.get("/")
async def get() -> HTMLResponse:
    return HTMLResponse("Working")


@app.get("/bot")
async def bot(action: str) -> Dict:
    resp = await send_message(action)
    return resp


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")