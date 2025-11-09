# server.py
import asyncio
import websockets
import shlex

async def terminal_handler(websocket, path):
    # Запускаем bash-процесс
    process = await asyncio.create_subprocess_exec(
        'bash',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    # Чтение stdout и отправка в WebSocket
    async def read_stdout():
        while True:
            line = await process.stdout.readline()
            if line:
                await websocket.send(line.decode())
            else:
                break

    asyncio.create_task(read_stdout())

    # Получение команд от клиента и отправка в bash
    async for message in websocket:
        process.stdin.write(message.encode() + b'\n')
        await process.stdin.drain()

async def main():
    print("Terminal WebSocket running on ws://0.0.0.0:8765")
    async with websockets.serve(terminal_handler, '0.0.0.0', 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())
