import json
import os
import asyncio
import discord
import logging
import websockets
import threading

from typing import Awaitable
from discord.ext import commands
from discord.ext.commands.context import Context
from Tweek.schema import WebSocketMessage
from websockets.legacy.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TOKEN = os.environ['TOKEN']
USER_ID = 664161180121825301
WEBSOCKET_HOST = "127.0.0.1"
WEBSOCKET_PORT = 5100
isConnected = False

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
    logger.info(f'{bot.user} has connected to Discord!')


async def logout() -> None:
    global isConnected
    if not isConnected:
        return
    isConnected = False
    await bot.close()
    logger.info(f'{bot.user} disconnected from discord server.')


async def login() -> None:
    global isConnected
    if isConnected:
        return
    isConnected = True
    await bot.start(TOKEN)
    logger.info(f'{bot.user} disconnected from discord server.')


@bot.command()
async def leave(ctx: Context) -> None:
    if ctx.message.author.id != USER_ID:
        await ctx.send('Dont have permission')
        return
    await ctx.send('Leaving server. BYE!')
    logger.info(f'{bot.user.mention} leaving Server! command from {ctx.author}.')
    await logout()


async def websocket_func(websocket: WebSocketServerProtocol, path: str):
    global isConnected
    logger.info("Websocket Connection Received")
    message = await websocket.recv()
    msg_obj = WebSocketMessage.parse_raw(message)
    logger.info(f"[ws server] message  < {msg_obj.json()}")
    if msg_obj.action == 'LOGOUT':
        msg = "Logging-out Bot"
        await logout()
    elif msg_obj.action == 'LOGIN':
        msg = "Logging-in Bot"
        await login()
    elif msg_obj.action == 'STOP':
        msg = "Stopping server"
        if isConnected:
            await logout()
        stop_event.set()
    else:
        msg = "No command found"
    resp = {
        'msg': msg
    }
    logging.info(msg)
    await websocket.send(json.dumps(resp))


async def start_websocket_server(_stop: Awaitable[bool]) -> None:
    async with websockets.serve(  # type: ignore[attr-defined]
            websocket_func, WEBSOCKET_HOST, WEBSOCKET_PORT
    ):
        logging.info(f"Websocket started on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        await _stop


loop = asyncio.get_event_loop()
stop_event = threading.Event()


def start_websocket():
    try:
        stop = asyncio.get_event_loop().run_in_executor(None, stop_event.wait)
        loop.run_until_complete(start_websocket_server(stop))
    except KeyboardInterrupt:
        logging.info("Closing Websocket as Keyboard Interrupt occurred")
        stop_event.set()
