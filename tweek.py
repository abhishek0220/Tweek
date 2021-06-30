import os
import asyncio
import discord
import logging
import websockets
import threading

from typing import Awaitable
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv
from pydantic import BaseModel
from websockets.legacy.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.environ['TOKEN']
USER_ID = 664161180121825301
WEBSOCKET_HOST = "127.0.0.1"
WEBSOCKET_PORT = 5100

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(
        command_prefix='.',
        description='abhis Bot',
        case_insensitive=True,
        intents=intents
)


@bot.event
async def on_ready() -> None:
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name=".help 💗")
    )
    logger.info(f'{bot.user.mention} has connected to Discord!')


async def leave_server() -> None:
    await bot.close()
    logger.info(f'{bot.user.mention} disconnected from discord server.')


@bot.command()
async def leave(ctx: Context) -> None:
    if ctx.message.author.id != USER_ID:
        await ctx.send('Dont have permission')
        return
    await ctx.send('Leaving server. BYE!')
    logger.info(f'{bot.user.mention} leaving Server! command from {ctx.author}.')
    await leave_server()


class WebSocketMessage(BaseModel):
    auth_code: str = ''
    action: str
    description: str = ''


async def websocket_func(websocket: WebSocketServerProtocol, path: str):
    logger.info("Websocket Connection Received")
    message = await websocket.recv()
    msg_obj = WebSocketMessage.parse_raw(message)
    logger.info(f"[ws server] message  < {msg_obj.json()}")
    if msg_obj.action == 'LEAVE':
        await websocket.send('{"msg":"leaving bot"}')
        logging.info("Leave request from Websocket")
        await leave_server()
    elif msg_obj.action == 'START':
        await websocket.send('{"msg":"starting bot"}')
        loop.create_task(bot.start(TOKEN))
    elif msg_obj.action == 'STOP':
        await websocket.send('{"msg":"stopping server"}')
        stop_event.set()
    else:
        await websocket.send('{"msg":"no command found"}')
        logging.info("No command found")


async def start_websocket_server(_stop: Awaitable[bool]) -> None:
    async with websockets.serve(  # type: ignore[attr-defined]
            websocket_func, WEBSOCKET_HOST, WEBSOCKET_PORT
    ):
        logging.info(f"Websocket started on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        await _stop

loop = asyncio.get_event_loop()
stop_event = threading.Event()

try:
    stop = asyncio.get_event_loop().run_in_executor(None, stop_event.wait)
    loop.run_until_complete(start_websocket_server(stop))
except KeyboardInterrupt:
    logging.info("Closing Websocket as Keyboard Interrupt occurred")
    stop_event.set()
