from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from starlette.responses import StreamingResponse
import asyncio

app = FastAPI()
current_data = "Ожидание данных..."
subscribers = []

@app.get("/", response_class=HTMLResponse)
def control_panel():
    return """
    <html>
    <body>
        <form action="/update" method="post">
            <input type="text" name="bonus" placeholder="Введите бонус" required>
            <button type="submit">Обновить</button>
        </form>
    </body>
    </html>
    """

@app.post("/update")
def update_data(bonus: str = Form(...)):
    global current_data
    current_data = bonus
    for queue in subscribers:
        queue.put_nowait(bonus)
    return {"message": "Данные обновлены"}

@app.get("/updates")
async def updates():
    queue = asyncio.Queue()
    subscribers.append(queue)
    try:
        async def event_stream():
            while True:
                data = await queue.get()
                yield f"data: {data}\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    finally:
        subscribers.remove(queue)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
