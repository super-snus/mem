import asyncio
from aiohttp import web, WSMsgType
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import subprocess

# 1️⃣ HTML Web App
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Web Terminal</title>
<style>
body { background:#1e1e1e; color:#c5c8c6; font-family:monospace; margin:0; }
#terminal { padding:10px; height:95vh; overflow-y:auto; white-space:pre-wrap;}
#input { width:100%; border:none; background:#2e2e2e; color:#c5c8c6; padding:8px; font-family:monospace;}
</style>
</head>
<body>
<div id="terminal"></div>
<input id="input" placeholder="Type command..." autofocus />
<script>
const terminalDiv = document.getElementById("terminal");
const input = document.getElementById("input");
const ws = new WebSocket(`ws://${location.host}/ws`);
ws.onmessage = (event) => {
    terminalDiv.innerText += event.data + "\\n";
    terminalDiv.scrollTop = terminalDiv.scrollHeight;
};
input.addEventListener("keydown", (e) => {
    if(e.key==="Enter"){ ws.send(input.value); input.value=""; }
});
</script>
</body>
</html>
"""

# 2️⃣ aiohttp сервер для Web App и WebSocket
async def index(request):
    return web.Response(text=HTML, content_type='text/html')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Запускаем bash
    process = await asyncio.create_subprocess_exec(
        'bash',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    async def read_stdout():
        while True:
            line = await process.stdout.readline()
            if line:
                await ws.send_str(line.decode())
            else:
                break

    asyncio.create_task(read_stdout())

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            process.stdin.write(msg.data.encode() + b'\n')
            await process.stdin.drain()
        elif msg.type == WSMsgType.ERROR:
            break

    process.kill()
    return ws

# 3️⃣ Telegram Bot
TOKEN = "8248310335:AAECHoL6wOvpNxJ2DDsdmGHRTeNjOQybU3s"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Кнопка открытия Web App
    url = f"http://YOUR_SERVER_IP:8080"
    button = InlineKeyboardButton("Open Terminal", web_app={"url": url})
    markup = InlineKeyboardMarkup([[button]])
    await update.message.reply_text("Open the Web Terminal:", reply_markup=markup)

async def main():
    # aiohttp app
    app = web.Application()
    app.add_routes([web.get('/', index), web.get('/ws', websocket_handler)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Web App running at http://0.0.0.0:8080")

    # Telegram Bot
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))

    await bot_app.initialize()
    await bot_app.start()
    print("Telegram bot started")
    await bot_app.updater.start_polling()
    await bot_app.updater.idle()

asyncio.run(main())
